from __future__ import annotations

import logging
import time
from typing import Any

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.ai_helper import get_openai_response
from src.logging_setup import configure_logging

configure_logging()
log = logging.getLogger(__name__)


def _wait(driver: WebDriver, by: str, value: str, *, timeout: int = 10):
    return WebDriverWait(driver, timeout, poll_frequency=0.1).until(
        EC.presence_of_element_located((by, value))
    )


def _click(driver: WebDriver, by: str, value: str, *, timeout: int = 10) -> None:
    element = WebDriverWait(driver, timeout, poll_frequency=0.1).until(
        EC.element_to_be_clickable((by, value))
    )
    element.click()


def search_jobs(driver: WebDriver, keyword: str, location: str) -> None:
    """Search jobs on Dice using the provided filters."""
    url = (
        "https://www.dice.com/jobs"
        f"?q={keyword}&location={location}&radius=30&radiusUnit=mi"
        "&page=1&pageSize=20&filters.postedDate=THREE&filters.easyApply=true&language=en"
    )
    log.info("Navigating to %s", url)
    driver.get(url)
    _wait(driver, By.CSS_SELECTOR, "a.card-title-link", timeout=15)


def apply_to_jobs(driver: WebDriver, data: dict[str, Any], *, dry_run: bool = False) -> None:
    """Apply to every matching job on the current page, then paginate."""
    while True:
        jobs = driver.find_elements(By.CSS_SELECTOR, "a.card-title-link")
        log.info("Found %d job(s) on this page.", len(jobs))

        for job in jobs:
            try:
                job.click()
                time.sleep(2)
                driver.switch_to.window(driver.window_handles[-1])

                if not _is_easy_apply_available(driver):
                    log.info("Skipping — already applied or Easy Apply unavailable.")
                    continue

                if dry_run:
                    log.info("[dry-run] would click Easy Apply.")
                    continue

                log.info("Clicking Easy Apply.")
                _click(driver, By.CSS_SELECTOR, "apply-button-wc", timeout=10)
                time.sleep(2)
                _navigate_form_and_submit(driver, data)

            except Exception as exc:  # noqa: BLE001
                log.error("Error applying to job: %s", exc)
            finally:
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

        if not _go_to_next_page(driver):
            log.info("No more pages — done.")
            break


def _is_easy_apply_available(driver: WebDriver) -> bool:
    try:
        if driver.find_element(By.CSS_SELECTOR, "apply-button-wc"):
            return True
    except NoSuchElementException:
        pass
    return False


def _navigate_form_and_submit(driver: WebDriver, data: dict[str, Any]) -> None:
    """Fill textareas + radio groups, click Next/Submit until the form completes."""
    while True:
        try:
            _fill_textareas(driver, data)
            _fill_radio_groups(driver, data)

            try:
                _click(
                    driver,
                    By.XPATH,
                    "//span[contains(text(),'Next')] "
                    "| //button[contains(text(),'Next')] "
                    "| //button[contains(text(),'Continue')]",
                    timeout=8,
                )
                time.sleep(2)
            except TimeoutException:
                try:
                    _click(
                        driver,
                        By.XPATH,
                        "//button[contains(@class,'btn-next') "
                        "and .//span[contains(text(),'Submit')]]",
                        timeout=8,
                    )
                    log.info("Application submitted.")
                    return
                except TimeoutException:
                    log.error("Could not find Next/Submit button — exiting form.")
                    return
        except Exception as exc:  # noqa: BLE001
            log.error("Error navigating form: %s", exc)
            return


def _fill_textareas(driver: WebDriver, data: dict[str, Any]) -> None:
    textareas = driver.find_elements(By.TAG_NAME, "textarea")
    if not textareas:
        return
    log.info("Processing %d textarea(s).", len(textareas))
    for textarea in textareas:
        try:
            textarea_id = textarea.get_attribute("id")
            if not textarea_id:
                continue
            label = driver.find_element(By.XPATH, f"//label[@for='{textarea_id}']")
            question = label.text.strip()
            log.info("Textarea question: %r", question)
            answer = get_openai_response(question, data)
            textarea.clear()
            textarea.send_keys(answer)
        except NoSuchElementException:
            continue
        except Exception as exc:  # noqa: BLE001
            log.error("Textarea error: %s", exc)


def _fill_radio_groups(driver: WebDriver, data: dict[str, Any]) -> None:
    groups = driver.find_elements(By.CLASS_NAME, "radio-input-wrapper")
    if not groups:
        return
    log.info("Processing %d radio group(s).", len(groups))
    for group in groups:
        try:
            question = group.find_element(By.TAG_NAME, "seds-paragraph").text.strip()
            log.info("Radio question: %r", question)
            radio_options = group.find_elements(By.TAG_NAME, "label")
            options = [o.text.strip() for o in radio_options]
            ai_response = get_openai_response(question, data, options)
            log.info("AI picks: %r", ai_response)
            for option in radio_options:
                if ai_response.lower() in option.text.strip().lower():
                    option.find_element(By.TAG_NAME, "input").click()
                    log.info("Selected %r", option.text.strip())
                    break
        except NoSuchElementException:
            continue
        except Exception as exc:  # noqa: BLE001
            log.error("Radio error: %s", exc)


def _go_to_next_page(driver: WebDriver) -> bool:
    try:
        next_button = driver.find_element(
            By.XPATH,
            "//li[contains(@class,'pagination-next') and not(contains(@class,'disabled'))]//a",
        )
        next_button.click()
        time.sleep(3)
        log.info("Moved to next page.")
        return True
    except NoSuchElementException:
        log.info("No next page.")
    except Exception as exc:  # noqa: BLE001
        log.error("Pagination error: %s", exc)
    return False
