#!/usr/bin/python3

# ADD API KEY TO BASHRC
# nano ~/.bashrc
# export ANTHROPIC_API_KEY=
# source ~/.bashrc

# RUN ME FROM ANYWWHERE
# chmod +x prompter.py
# mv prompter.py prompter
# sudo cp prompter /usr/local/bin/
# set the PROMPT_DIR value
# ex: PROMPT_DIR=/home/wsl_ubuntu/prompter/prompts
# source ~/.bashrc

# COPY PASTE WIZARD
# sudo apt install xclip
# Put this in your ~/.bashrc or ~/.zshrc:
# alias c='xclip -selection clipboard'
# alias p='xclip -selection clipboard -o'
# source ~/.bashrc

import os
import argparse
import re
import anthropic
import pyperclip
from pathlib import Path
from colorama import init, Fore, Style
from readability import Document
import requests
import argcomplete
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
import datetime

# Initialize colorama
init(autoreset=True)

# Global variable for prompt directory
PROMPT_DIR = Path('prompts')

def get_prompt(prompt_title):
    prompt_file = PROMPT_DIR / prompt_title / 'system.md'
    try:
        with open(prompt_file, 'r') as file:
            return file.read()
    except IOError as e:
        print_error(f"Error reading prompt file: {e}")
        return None

def print_info(message):
    print(f"{Fore.CYAN}{message}{Style.RESET_ALL}")

def print_success(message):
    print(f"{Fore.GREEN}{message}{Style.RESET_ALL}")

def print_error(message):
    print(f"{Fore.RED}{message}{Style.RESET_ALL}")

def print_warning(message):
    print(f"{Fore.YELLOW}{message}{Style.RESET_ALL}")

def anonymize_sensitive_text(text):
    pattern = r'\*\*(.*?)\*\*'
    placeholders = {}
    
    def replace(match):
        content = match.group(1)
        placeholder = f"PLACEHOLDER_{len(placeholders) + 1}"
        placeholders[placeholder] = content
        return placeholder
    
    anonymized_text = re.sub(pattern, replace, text)
    return anonymized_text, placeholders

def deanonymize_text(text, placeholders):
    for placeholder, original in placeholders.items():
        text = text.replace(placeholder, f"{original}")
    return text

def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except IOError as e:
        print_error(f"Error reading file: {e}")
        return None

def get_prompt(prompt_title):
    prompt_dir = Path('prompts') / prompt_title
    system_file = prompt_dir / 'system.md'
    try:
        with open(system_file, 'r') as file:
            return file.read()
    except IOError as e:
        print_error(f"Error reading prompt file: {e}")
        return None

def process_with_anthropic(content, selected_prompt):
    print_info("Processing...")
    try:
        client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
        prompt = f"""
        {selected_prompt}
        <user query>{content}</user query>
        """
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=2000,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        processed_content = message.content[0].text
        return processed_content
    except Exception as e:
        print_error(f"Error processing with Anthropic API: {e}")
        return None

def extract_content_from_url(url):
    try:
        response = requests.get(url)
        doc = Document(response.text)
        return doc.summary()
    except Exception as e:
        print_error(f"Error extracting content from URL: {e}")
        return None

def list_prompts():
    prompts = [d.name for d in PROMPT_DIR.iterdir() if d.is_dir()]
    print_info("\nAvailable prompts:")
    for i, prompt in enumerate(prompts, 1):
        print(f"{i}. {prompt}")
    print("")
    return prompts

def prompt_completer(prefix, **kwargs):
    return (d.name for d in PROMPT_DIR.iterdir() if d.is_dir() and d.name.startswith(prefix))

def select_prompt():
    prompts = list_prompts()
    completer = WordCompleter(prompts + [str(i) for i in range(1, len(prompts) + 1)])
    
    while True:
        user_input = prompt("Select a prompt (number or name): ", completer=completer)
        
        if user_input.isdigit():
            index = int(user_input) - 1
            if 0 <= index < len(prompts):
                return prompts[index]
        elif user_input in prompts:
            return user_input
        
        print_error("Invalid selection. Please try again.")

def save_output(content, filename=None, path=None):
    if not filename:
        filename = f"output_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    if path:
        full_path = Path(path) / filename
    else:
        full_path = Path(filename)
    
    try:
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w') as file:
            file.write(content)
        print_success(f"Output saved to: {full_path}")
    except IOError as e:
        print_error(f"Error saving output: {e}")

def process_url_file(file_path):
    try:
        with open(file_path, 'r') as file:
            urls = file.read().splitlines()
        
        content = ""
        for url in urls:
            print_info(f"Extracting content from URL: {url}")
            url_content = extract_content_from_url(url)
            if url_content:
                content += f"\n\nURL: {url}\n{url_content}"
        
        return content
    except IOError as e:
        print_error(f"Error reading URL file: {e}")
        return None

def main():
    global PROMPT_DIR
    
    parser = argparse.ArgumentParser(description="CLI tool for LLM processing with anonymization")
    parser.add_argument("-i", "--input", help="User input or file path")
    parser.add_argument("-f", "--file", help="Input file path")
    parser.add_argument("-p", "--prompt", help="Prompt title").completer = prompt_completer
    parser.add_argument("-l", "--list", action="store_true", help="List available prompts")
    parser.add_argument("-u", "--url", help="URL to extract content from")
    parser.add_argument("-uf", "--url-file", help="File containing URLs to process")
    parser.add_argument("-o", "--output", nargs='?', const='', help="Save output to file (optional filename)")
    parser.add_argument("-op", "--output-path", help="Path to save the output file")
    parser.add_argument("-ap", "--add-prompt", help="Additional prompt text to append")
    parser.add_argument("-np", "--new-prompt", help="Use a custom prompt directly")
    parser.add_argument("-pd", "--prompt-dir", help="Set custom prompt directory")
    
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if args.prompt_dir:
        PROMPT_DIR = Path(args.prompt_dir)
        print_info(f"Using custom prompt directory: {PROMPT_DIR}")

    if args.list:
        list_prompts()
        return

    if not args.input and not args.file and not args.url and not args.url_file:
        print_error("Error: Please provide either input text, a file path, a URL, or a file containing URLs.")
        return

    content = args.input
    if args.file:
        print_info(f"Reading input from file: {args.file}")
        content = read_file(args.file)
        if content is None:
            return
    elif args.url:
        print_info(f"Extracting content from URL: {args.url}")
        content = extract_content_from_url(args.url)
        if content is None:
            return
    elif args.url_file:
        print_info(f"Processing URLs from file: {args.url_file}")
        content = process_url_file(args.url_file)
        if content is None:
            return

    if args.new_prompt:
        prompt = args.new_prompt
    else:
        if not args.prompt:
            selected_prompt = select_prompt()
        else:
            selected_prompt = args.prompt

        prompt = get_prompt(selected_prompt)
        if prompt is None:
            return

        if args.add_prompt:
            prompt += f"\n{args.add_prompt}"

    anonymized_content, placeholders = anonymize_sensitive_text(content)
    
    processed_content = process_with_anthropic(anonymized_content, prompt)

    if processed_content:
        final_content = deanonymize_text(processed_content, placeholders)
        print_success("Response from Claude LLM:\n")
        print(final_content)
        print("")
        pyperclip.copy(final_content)
        print_info("Output copied to clipboard.")
        
        if args.output is not None:
            save_output(final_content, args.output, args.output_path)
    else:
        print_warning("No content to display due to processing error.")

if __name__ == "__main__":
    main()
