# src/ai_helper.py

import openai
import yaml
import os
import logging
import time
import json

# Configure logging for ai_helper.py
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("application.log"),
        logging.StreamHandler()
    ]
)

def load_config(config_path="src/config.yaml"):
    """
    Load configuration from a YAML file.

    :param config_path: Path to the config.yaml file.
    :return: Configuration dictionary.
    """
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        logging.info("Configuration loaded successfully.")
        logging.debug(f"Configuration content: {config}")  # Added for debugging
        return config
    except FileNotFoundError:
        logging.error(f"Configuration file {config_path} not found.")
        return {}
    except yaml.YAMLError as exc:
        logging.error(f"Error parsing {config_path}: {exc}")
        return {}

def initialize_openai(config):
    """
    Initialize OpenAI with the API key from the config or environment variable.

    :param config: Configuration dictionary.
    """
    try:
        # Retrieve API key from environment variable if available, else from config
        api_key = os.getenv('OPENAI_API_KEY', config.get('openai', {}).get('api_key'))
        if api_key:
            openai.api_key = api_key
            logging.info("OpenAI initialized successfully.")
        else:
            logging.error("OpenAI API key not found in configuration or environment.")
            raise KeyError("Missing 'openai.api_key' in config.")
    except KeyError as e:
        logging.error(f"KeyError: {e}")
    except Exception as e:
        logging.error(f"Error initializing OpenAI: {e}")

def load_data(data_path="src/data.yaml"):
    """
    Load personal data from a YAML file.

    :param data_path: Path to the data.yaml file.
    :return: Personal data dictionary.
    """
    try:
        with open(data_path, 'r') as file:
            data = yaml.safe_load(file)
        logging.info("Personal data loaded successfully from data.yaml.")
        logging.debug(f"Personal data content: {data}")  # Added for debugging
        return data
    except FileNotFoundError:
        logging.error(f"Data file {data_path} not found.")
        return {}
    except yaml.YAMLError as exc:
        logging.error(f"Error parsing {data_path}: {exc}")
        return {}

def get_openai_response(question, data, retries=3, delay=5):
    """
    Generate a response for a given question using OpenAI's API and the provided data.

    :param question: The question extracted from the form's label.
    :param data: The parsed YAML data as a dictionary.
    :param retries: Number of retry attempts.
    :param delay: Delay between retries in seconds.
    :return: The generated response string.
    """
    # Convert data to a JSON string for better formatting in the prompt
    data_json = json.dumps(data, indent=2)
  

    messages = [
        {"role": "system", "content": "You are a helpful assistant that generates answers for job application questions based on the user's personal data."},
        {"role": "user", "content": f"""
You are an assistant that helps fill out job application forms based on provided personal data.

Personal data:
{data_json}

Question:
"{question}"

Provide a concise and appropriate answer based on the personal data.
"""}
    ]

    for attempt in range(1, retries + 1):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # or "gpt-4" if available and accessible
                messages=messages,
                max_tokens=150,
                temperature=0.3,
                n=1,
                stop=None,
            )
            answer = response.choices[0].message.content.strip()
            logging.info(f"Generated response for question '{question}': {answer}")
            return answer
        except Exception as e:
            logging.error(f"Attempt {attempt} - Error generating response from OpenAI: {e}")
            if attempt < retries:
                logging.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logging.error("All retry attempts failed. Using 'NA' as fallback.")
                return "NA"  # Fallback answer in case of error
