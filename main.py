#!/usr/bin/python3

# ADD API KEY TO BASHRC
# nano ~/.bashrc
# export ANTHROPIC_API_KEY=
# source ~/.bashrc

# RUN ME FROM ANYWWHERE
# chmod +x prompter.py
# mv prompter.py prompter
# sed -i 's/\r$//' prompter
# sudo cp prompter /usr/local/bin/
# set the PROMPT_DIR value
# ex: PROMPT_DIR=/home/wsl_ubuntu/prompter/prompts
# source ~/.bashrc

# CHANGE FORMAT IF ISSUE
# sed -i 's/\r$//' /usr/local/bin/prompter

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
import datetime
import sys

# Initialize colorama
init(autoreset=True)

def get_multiline_input():
    print("Enter your input (press Enter twice to finish):")
    lines = []
    empty_lines = 0
    while True:
        line = input()
        if line.strip() == "":
            empty_lines += 1
            if empty_lines == 2:
                print_info("Processing Input...\n")
                break
        else:
            empty_lines = 0
        lines.append(line)
    return "\n".join(lines[:-2])  # Remove the last two empty lines

def get_script_directory():
    return Path(__file__).parent.resolve()

def list_prompts():
    script_dir = get_script_directory()
    prompts = [f.stem for f in script_dir.glob('*.md') if f.stem.lower() != 'readme']
    return sorted(prompts)

def get_input_from_pipe():
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
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
    script_dir = get_script_directory()
    prompt_file = script_dir / f"{prompt_title}.md"
    try:
        with open(prompt_file, 'r') as file:
            return file.read()
    except IOError as e:
        print_error(f"Error reading prompt file: {e}")
        return None

def process_with_anthropic(content, selected_prompt):
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

def prompt_completer(prefix, **kwargs):
    return (prompt for prompt in list_prompts() if prompt.startswith(prefix))

def save_output(content, filename=None):
    if not filename:
        filename = f"output_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
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
    parser = argparse.ArgumentParser(description="CLI tool for LLM processing with anonymization")
    parser.add_argument("-i", "--input", help="User input or file path")
    parser.add_argument("-f", "--file", help="Input file path")
    parser.add_argument("-p", "--prompt", help="Prompt title").completer = prompt_completer
    parser.add_argument("-u", "--url", help="URL to extract content from")
    parser.add_argument("-uf", "--url-file", help="File containing URLs to process")
    parser.add_argument("-o", "--output", nargs='?', const='', help="Save output to file (optional filename)")
    parser.add_argument("-ap", "--add-prompt", help="Additional prompt text to append")
    parser.add_argument("-np", "--new-prompt", help="Use a custom prompt directly")
    parser.add_argument("-c", "--copy", action="store_true", help="Copy output to clipboard")
    parser.add_argument("-l", "--list", action="store_true", help="List available prompts")

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if args.list:
        prompts = list_prompts()
        print_info("Available prompts:")
        for prompt in prompts:
            print(prompt)
        return

    if not args.prompt and not args.new_prompt:
        print_error("Error: Please provide either a prompt title (-p) or a new prompt (-np).")
        return

    piped_input = get_input_from_pipe()
    if piped_input:
        content = piped_input
    elif args.input:
        content = args.input
    elif args.file:
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
    else:
        content = get_multiline_input()

    if args.new_prompt:
        prompt = args.new_prompt
    else:
        prompt = get_prompt(args.prompt)
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
        
        if args.copy:
            pyperclip.copy(final_content)
        
        if args.output is not None:
            save_output(final_content, args.output)
    else:
        print_warning("No content to display due to processing error.")

if __name__ == "__main__":
    main()
