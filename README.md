# Dice Job Application Automation

This is an automated script that applies for jobs on Dice.com using Selenium WebDriver. The script searches for jobs based on keywords and location, navigates to the job posting, clicks on the "Easy Apply" button, and automatically fills and submits job applications.

## Features

- Automates job applications on Dice.com
- Uses Selenium to navigate job listings and fill application forms
- Skips already applied jobs
- Handles multiple pages of forms by clicking "Next" until the "Submit" button is reached

## Prerequisites

Before setting up the environment, make sure you have the following installed:

- Python 3.8 or later
- Google Chrome browser
- ChromeDriver (compatible with your Chrome version)
- Selenium WebDriver

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/svrohith9/dice_job_application_automation.git
cd dice-job-automation
```

### 2. Create and Activate Virtual Environment

Create a virtual environment to manage dependencies:

On macOS and Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

Install the required packages using `pip`:

```bash
pip install -r requirements.txt
```

### 4. Setup ChromeDriver

You will need to download the ChromeDriver that matches your installed version of Chrome. Download it from [here](https://sites.google.com/a/chromium.org/chromedriver/downloads).

1. Place the ChromeDriver executable in your system's PATH or in the project directory.
2. Ensure it's executable by running:

```bash
chmod +x chromedriver
```

Alternatively, specify the path to ChromeDriver in the script.

### 5. Update Configurations

If necessary, update the following parts of the script based on your environment:

- **ChromeDriver Path**: If ChromeDriver is not in your system's PATH, specify the full path to `chromedriver` in the Selenium `driver` initialization.
- **Search Parameters**: Customize the job search keyword and location in the script.

### 6. Run the Script

Once everything is set up, you can run the script:

```bash
python app.py
```

The script will automatically:
- Search for jobs on Dice.com using predefined keywords and location
- Apply to jobs that have not yet been applied to
- Submit applications through the form flow by clicking the "Next" and "Submit" buttons

## Logging

The script provides informative logs to track progress. You can find logs output in the console.

## Notes

- Ensure that your browser is updated and the version of ChromeDriver matches your installed Chrome version.
- The script relies on page elements, so changes to the Dice.com UI may require adjustments to the script's locators (CSS selectors, XPaths).

## Issues

If you run into any issues or bugs, feel free to create an issue on this repository, and I'll take a look as soon as possible!

## License

This project is licensed under the MIT License.
