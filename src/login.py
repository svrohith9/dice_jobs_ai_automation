from __future__ import annotations

import logging

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.logging_setup import configure_logging

configure_logging()
log = logging.getLogger(__name__)


def login_to_dice(driver: WebDriver, username: str, password: str, *, timeout: int = 15) -> bool:
    """Log in to dice.com. Returns True on success, False otherwise."""
    driver.get("https://www.dice.com/dashboard/login")
    try:
        email_input = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        email_input.clear()
        email_input.send_keys(username)

        WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        ).click()

        password_input = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_input.clear()
        password_input.send_keys(password)

        WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        ).click()

        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(),'Welcome')]"))
        )
        log.info("Login successful.")
        return True
    except TimeoutException as exc:
        log.error("Login timed out: %s", exc)
        return False
    except Exception as exc:  # noqa: BLE001
        log.error("Login failed: %s", exc)
        return False
