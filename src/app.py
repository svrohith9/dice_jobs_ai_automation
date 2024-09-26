# src/app.py

from login import login_to_dice
from job_search import search_jobs, apply_to_jobs
from ai_helper import load_config, initialize_openai
from selenium import webdriver

def main():
    # Load configurations and initialize OpenAI
    config = load_config()
    initialize_openai()

    # Initialize Selenium WebDriver
    driver = webdriver.Chrome()

    try:
        # Login to Dice
        login_to_dice(driver, config['credentials']['username'], config['credentials']['password'])

        # Perform job search and apply
        search_jobs(driver, config['search_params']['keyword'], config['search_params']['location'])
        apply_to_jobs(driver)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
