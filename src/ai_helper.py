# src/ai_helper.py

import openai
import yaml

# Load the configuration and OpenAI API key
def load_config():
    with open("src/config.yaml", 'r') as file:
        config = yaml.safe_load(file)
    return config

def initialize_openai():
    config = load_config()
    openai.api_key = config['openai']['api_key']

# Function to handle OpenAI responses for job applications
def get_openai_response(prompt):
    try:
        response = openai.Completion.create(
            engine="gpt-4",  # Choose the appropriate engine
            prompt=prompt,
            max_tokens=50
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error generating response from OpenAI: {e}")
        return ""

