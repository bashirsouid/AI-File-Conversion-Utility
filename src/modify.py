#!/usr/bin/env python3

import os
import json
import random
import re
import requests
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration defaults
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")
DEFAULT_CONFIG = {
    "file_extension": ".json",
    "output_suffix": ".converted",
    "replace_original": False,
    "prompt_file": None,
    "prompt_text": "Return back the original file again with no changes.",
}

# Load environment variables from .modify.env
def load_env(target_directory, config):
    env_file = config.get("env_file", ".modify.env")
    env_paths = [
        os.path.join(target_directory, env_file),
        os.path.join(SCRIPT_DIR, env_file)
    ]
    for path in env_paths:
        if os.path.exists(path):
            load_dotenv(path)
            return
    raise FileNotFoundError(f"Environment file '{env_file}' not found in target or script directory.")

# Load API keys from environment variables
def load_api_keys():
    api_keys = []
    for key, value in os.environ.items():
        if key.startswith("API_KEY_"):
            api_keys.append(value)
    if not api_keys:
        raise ValueError("No API keys found in the .modify.env file.")
    return api_keys

# Load configuration from a JSON file
def load_config(config_path):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, "r") as f:
        return json.load(f)

# Save a blank config file
def save_blank_config(config_path):
    with open(config_path, "w") as f:
        json.dump(DEFAULT_CONFIG, f, indent=4)
    print(f"Blank config file created at {config_path}")

# Logging function
def log_message(message):
    print(message)

# Extract content inside triple backticks or fallback to full response
def extract_content(content):
    match = re.search(r"``````", content, re.DOTALL)
    return match.group(1).strip() if match else content.strip()

# Process a single file
def process_file(file_path, config, api_keys):
    output_suffix = config["output_suffix"]
    replace_original = config["replace_original"]

    # Determine output file path
    base_name, ext = os.path.splitext(file_path)
    if replace_original:
        backup_path = f"{file_path}.bak"
        os.rename(file_path, backup_path)
        final_output_file_path = file_path
    else:
        final_output_file_path = f"{base_name}{output_suffix}{ext}"

    # Skip processing if output already exists
    if os.path.exists(final_output_file_path):
        log_message(f"Skipping {file_path}: Converted version already exists.")
        return

    # Read input file content
    with open(file_path, "r") as f:
        file_content = f.read().strip()

    # Prepare payload for API request
    payload = {
        "model": "llama-3.1-sonar-huge-128k-online",
        "temperature": 0,
        "messages": [
            {"role": "user", "content": "I am going to give you a file to process and then a prompt with instructions for how to transform it. First I will give you the file to proccess, then I will give you the prompt with instructions in the subsequent message."},
            {"role": "assistant", "content": "I understand. First, please provide the file to process."},
            {"role": "user", "content": file_content},
            {"role": "assistant", "content": "Thank you for the file contents. Now please provide the prompt with instructions for how to transform the file."},
            {"role": "user", "content": config.get("prompt_text", "")}
        ],
    }

    # Make API request and write response to output file
    try:
        api_key = random.choice(api_keys)  # Randomly select an API key from the array
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        response = requests.post("https://api.perplexity.ai/chat/completions", headers=headers, json=payload)
        response.raise_for_status()

        agent_message = extract_content(response.text)
        with open(final_output_file_path, "w") as f:
            f.write(agent_message + "\n")

        log_message(f"Processed {file_path} -> {final_output_file_path}")

    except Exception as e:
        log_message(f"Error processing {file_path}: {str(e)}")

# Main function to process all files in a directory recursively
def main(target_directory, config):
    load_env(target_directory, config)
    
    # Load API keys from .modify.env
    api_keys = load_api_keys()

    # Load reference and prompt content if specified in the config
    reference_file = config.get("reference_file")
    prompt_file = config.get("prompt_file")

    if reference_file and os.path.exists(reference_file):
        with open(reference_file, "r") as f:
            config["reference_content"] = f.read().strip()

    if prompt_file and os.path.exists(prompt_file):
        with open(prompt_file, "r") as f:
            config["prompt_text"] = f.read().strip()

    original_files = []
    for root, _, files in os.walk(target_directory):
        for file in files:
            if file.endswith(config["file_extension"]):
                original_files.append(os.path.join(root, file))

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_file, file, config, api_keys) for file in original_files]
        for future in as_completed(futures):
            future.result()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process files with AI transformations.")
    
    parser.add_argument("directory", help="Target directory containing files to process.")
    parser.add_argument("--config", help="Path to configuration JSON file.", default=DEFAULT_CONFIG_PATH)
    
    args = parser.parse_args()
    
    try:
        if not os.path.exists(args.config):
            create_config_prompt = input("Config file not found. Create a blank one? (y/n): ").strip().lower()
            if create_config_prompt == 'y':
                save_blank_config(args.config)
                exit(0)
            else:
                print("Exiting. Config file is required.")
                exit(1)

        config_data = load_config(args.config)
        main(args.directory, config_data)

    except Exception as e:
        log_message(f"Fatal error: {str(e)}")
