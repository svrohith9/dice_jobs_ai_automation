# src/app.py

from login import login_to_dice
from job_search import search_jobs, apply_to_jobs
from ai_helper import load_config, initialize_openai, load_data
from selenium import webdriver
import logging

def main():
    # Load configurations
    config = load_config()
    logging.debug(f"Loaded config: {config}")  # Optional: For additional debugging
    
    # Initialize OpenAI with the entire config
    initialize_openai(config)  # Pass the entire config dictionary

    # Load personal data
    data = load_data()
    logging.debug(f"Loaded data: {data}")  # Optional: For additional debugging

    # Initialize Selenium WebDriver
    options = webdriver.ChromeOptions()
    # options.add_argument("--start-maximized")
    # Uncomment the next line to run Chrome in headless mode
    # options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    try:
        # Login to Dice
        login_to_dice(driver, config['credentials']['username'], config['credentials']['password'])

        # Perform job search and apply
        search_jobs(driver, config['search_params']['keyword'], config['search_params']['location'])
        apply_to_jobs(driver, data)  # Pass 'data' to apply_to_jobs

    finally:
        driver.quit()
        logging.info("WebDriver closed.")

if __name__ == "__main__":
    main()
