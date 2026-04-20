from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any

import yaml
from openai import APIError, OpenAI, RateLimitError

from src.logging_setup import configure_logging

configure_logging()
log = logging.getLogger(__name__)

_client: OpenAI | None = None


def load_config(config_path: str | Path = "src/config.yaml") -> dict[str, Any]:
    """Load configuration from a YAML file."""
    path = Path(config_path)
    try:
        with path.open("r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
        log.info("Loaded config from %s", path)
        return config
    except FileNotFoundError:
        log.error("Config file %s not found.", path)
        return {}
    except yaml.YAMLError as exc:
        log.error("Error parsing %s: %s", path, exc)
        return {}


def load_data(data_path: str | Path = "src/data.yaml") -> dict[str, Any]:
    """Load personal data from a YAML file."""
    path = Path(data_path)
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        log.info("Loaded personal data from %s", path)
        return data
    except FileNotFoundError:
        log.error("Data file %s not found.", path)
        return {}
    except yaml.YAMLError as exc:
        log.error("Error parsing %s: %s", path, exc)
        return {}


def initialize_openai(config: dict[str, Any]) -> OpenAI | None:
    """Initialize the OpenAI client using env var first, then config."""
    global _client
    api_key = os.getenv("OPENAI_API_KEY") or config.get("openai", {}).get("api_key")
    if not api_key:
        log.error("OpenAI API key not found in OPENAI_API_KEY or config['openai']['api_key'].")
        return None
    _client = OpenAI(api_key=api_key)
    log.info("OpenAI client initialized.")
    return _client


def get_openai_response(
    question: str,
    data: dict[str, Any],
    options: list[str] | None = None,
    *,
    model: str = "gpt-4o-mini",
    retries: int = 3,
    delay: float = 5.0,
) -> str:
    """Ask the LLM to fill a form field given the user's personal data.

    Falls back to ``"NA"`` on repeated failure so the bot keeps moving.
    """
    if _client is None:
        log.error("OpenAI client not initialized — returning 'NA'.")
        return "NA"

    data_json = json.dumps(data, indent=2)

    if options:
        options_block = "\n".join(f"- {o}" for o in options)
        user_prompt = (
            "You are an assistant that helps fill out job-application forms based on "
            "the user's personal data.\n\n"
            f"Personal data:\n{data_json}\n\n"
            f'Question:\n"{question}"\n\n'
            f"Choose the single most appropriate option and return it verbatim:\n{options_block}"
        )
    else:
        user_prompt = (
            "You are an assistant that helps fill out job-application forms based on "
            "the user's personal data.\n\n"
            f"Personal data:\n{data_json}\n\n"
            f'Question:\n"{question}"\n\n'
            "Provide a concise, professional answer based on the personal data."
        )

    messages = [
        {
            "role": "system",
            "content": "You generate short, accurate answers for job-application form fields.",
        },
        {"role": "user", "content": user_prompt},
    ]

    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            completion = _client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=200,
                temperature=0.2,
            )
            answer = (completion.choices[0].message.content or "").strip()
            log.info("LLM answer for %r: %s", question, answer)
            return answer or "NA"
        except RateLimitError as exc:
            last_exc = exc
            log.warning("Rate-limited (attempt %d/%d): %s", attempt, retries, exc)
        except APIError as exc:
            last_exc = exc
            log.warning("OpenAI APIError (attempt %d/%d): %s", attempt, retries, exc)
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            log.warning("Unexpected error (attempt %d/%d): %s", attempt, retries, exc)
        if attempt < retries:
            sleep_for = delay * attempt
            log.info("Retrying in %.1fs…", sleep_for)
            time.sleep(sleep_for)

    log.error("All retries exhausted (%s); using 'NA'.", last_exc)
    return "NA"
