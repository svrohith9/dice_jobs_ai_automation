from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def wait_for_element(driver, by, value, timeout=10, poll_frequency=0.1):
    """Utility function to wait for an element to be present."""
    return WebDriverWait(driver, timeout, poll_frequency=poll_frequency).until(
        EC.presence_of_element_located((by, value))
    )

def click_element(driver, by, value, timeout=10, poll_frequency=0.1):
    """Utility function to click on an element."""
    element = WebDriverWait(driver, timeout, poll_frequency=poll_frequency).until(
        EC.element_to_be_clickable((by, value))
    )
    element.click()

def search_jobs(driver, keyword, location):
    """Search jobs on Dice website using filters."""
    url = f"https://www.dice.com/jobs?q={keyword}&location={location}&radius=30&radiusUnit=mi&page=1&pageSize=20&filters.postedDate=THREE&filters.easyApply=true&language=en"
    logging.info(f"Navigating to URL: {url}")
    driver.get(url)
    wait_for_element(driver, By.CSS_SELECTOR, "a.card-title-link", timeout=5)  # Wait for jobs to load

def apply_to_jobs(driver):
    """Apply to jobs on the current page and handle pagination."""
    while True:
        jobs = driver.find_elements(By.CSS_SELECTOR, "a.card-title-link")
        logging.info(f"Found {len(jobs)} job(s) to apply for on this page.")

        for job in jobs:
            try:
                job.click()
                time.sleep(2)  # Short delay to allow the page to load
                
                # Switch to the newly opened job window
                driver.switch_to.window(driver.window_handles[-1])

                # Check if "Easy Apply" button is available
                if is_easy_apply_available(driver):
                    # Click the "Easy Apply" button
                    logging.info("Waiting for 'Easy Apply' button.")
                    apply_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "apply-button-wc"))
                    )
                    apply_button.click()
                    logging.info("Clicked 'Easy Apply' button.")
                    time.sleep(1)  # Short sleep to ensure click is registered

                    # Navigate through the form and submit the application
                    navigate_form_and_submit(driver)
                else:
                    logging.info("Job already applied or 'Easy Apply' not available. Skipping this job.")

            except Exception as e:
                logging.error(f"Error applying to job: {e}")
            
            finally:
                # Close the job tab and switch back to the job list (main window)
                if len(driver.window_handles) > 1:
                    driver.close()  # Close the current job tab
                    driver.switch_to.window(driver.window_handles[0])  # Switch back to the original tab

        # Move to the next page if available
        if not go_to_next_page(driver):
            logging.info("No more pages left. Exiting.")
            break

def is_easy_apply_available(driver):
    """Check if the 'Easy Apply' button is available to determine if the job is already applied."""
    try:
        # Check for "Easy Apply" button
        apply_button = driver.find_element(By.CSS_SELECTOR, "apply-button-wc")
        if apply_button:
            logging.info("'Easy Apply' button found, proceeding with application.")
            return True
    except NoSuchElementException:
        logging.info("'Easy Apply' button not found. Job likely already applied.")
        return False

def navigate_form_and_submit(driver):
    """Navigate through the form pages by filling textareas with 'NA' and clicking 'Next' until reaching 'Submit'."""
    try:
        while True:
            try:
                # Fill all textarea elements with "NA" before proceeding
                textareas = driver.find_elements(By.TAG_NAME, "textarea")
                if textareas:
                    logging.info(f"Found {len(textareas)} textarea(s). Filling them with 'NA'.")
                    for textarea in textareas:
                        try:
                            # Clear any existing text and input "NA"
                            textarea.clear()
                            textarea.send_keys("NA")
                            logging.debug("Filled a textarea with 'NA'.")
                        except Exception as e:
                            logging.warning(f"Could not fill a textarea: {e}")
                else:
                    logging.info("No textarea elements found on this page.")

                # Dynamically wait for the "Next" button and click if found
                next_button = WebDriverWait(driver, 5, poll_frequency=0.1).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        "//span[contains(text(), 'Next')] | //button[contains(text(), 'Next')] | //button[contains(text(), 'Continue')]"
                    ))
                )
                next_button.click()
                logging.info("Clicked 'Next' button to continue to the next form step.")
                time.sleep(1)  # Short delay to allow the next form step to load

            except TimeoutException:
                logging.info("No 'Next' button found. Checking for 'Submit' button.")

                # Look for "Submit" button with class 'btn-next' and text 'Submit'
                try:
                    submit_button = WebDriverWait(driver, 5, poll_frequency=0.1).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-next') and .//span[contains(text(), 'Submit')]]"))
                    )
                    submit_button.click()
                    logging.info("Application submitted successfully.")
                    break  # Exit loop after application is submitted

                except TimeoutException:
                    logging.error("Could not find 'Submit' button. Exiting form process.")
                    break

    except Exception as e:
        logging.error(f"Error navigating form or submitting the application: {e}")

def go_to_next_page(driver):
    """Navigate to the next page of job listings if available."""
    try:
        next_button = driver.find_element(By.XPATH, "//li[contains(@class, 'pagination-next') and not(contains(@class, 'disabled'))]//a")
        next_button.click()
        time.sleep(2)  # Allow the next page to load
        logging.info("Moved to the next page.")
        return True
    except NoSuchElementException:
        logging.info("No 'Next' button found or last page reached.")
        return False

# Example usage:
# from selenium import webdriver
# driver = webdriver.Chrome()
# search_jobs(driver, "Software Engineer", "New York")
# apply_to_jobs(driver)
# driver.quit()
