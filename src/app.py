from __future__ import annotations

import argparse
import logging
import sys

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from src.ai_helper import initialize_openai, load_config, load_data
from src.job_search import apply_to_jobs, search_jobs
from src.logging_setup import configure_logging
from src.login import login_to_dice

configure_logging()
log = logging.getLogger(__name__)


def build_driver(*, headless: bool) -> webdriver.Chrome:
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,900")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=options)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="dice-apply",
        description="Auto-apply to matching jobs on Dice.com.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log what would happen without actually clicking Apply.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run Chrome in headless mode.",
    )
    parser.add_argument(
        "--config",
        default="src/config.yaml",
        help="Path to config.yaml (default: src/config.yaml)",
    )
    parser.add_argument(
        "--data",
        default="src/data.yaml",
        help="Path to data.yaml (default: src/data.yaml)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    config = load_config(args.config)
    if not config:
        log.error("Missing or invalid config. Copy config.yaml.example → config.yaml.")
        return 1

    data = load_data(args.data)
    if initialize_openai(config) is None:
        log.error("Cannot start without an OpenAI API key.")
        return 2

    try:
        credentials = config["credentials"]
        search = config["search_params"]
    except KeyError as exc:
        log.error("Missing required config key: %s", exc)
        return 3

    driver = build_driver(headless=args.headless)
    try:
        if not login_to_dice(driver, credentials["username"], credentials["password"]):
            log.error("Login failed — aborting.")
            return 4

        search_jobs(driver, search["keyword"], search["location"])
        apply_to_jobs(driver, data, dry_run=args.dry_run)
    finally:
        driver.quit()
        log.info("WebDriver closed.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
