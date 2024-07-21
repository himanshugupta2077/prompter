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

# Initialize colorama
init(autoreset=True)

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
    prompt_dir = Path('prompts')
    prompts = [d.name for d in prompt_dir.iterdir() if d.is_dir()]
    print_info("Available prompts:")
    for prompt in prompts:
        print(prompt)

def prompt_completer(prefix, **kwargs):
    prompt_dir = Path('prompts')
    return (d.name for d in prompt_dir.iterdir() if d.is_dir() and d.name.startswith(prefix))

def main():
    parser = argparse.ArgumentParser(description="CLI tool for LLM processing with anonymization")
    parser.add_argument("-i", "--input", help="User input or file path")
    parser.add_argument("-f", "--file", help="Input file path")
    parser.add_argument("-p", "--prompt", default="ai", help="Prompt title (default: ai)").completer = prompt_completer
    parser.add_argument("-l", "--list", action="store_true", help="List available prompts")
    parser.add_argument("-u", "--url", help="URL to extract content from")
    
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if args.list:
        list_prompts()
        return

    if not args.input and not args.file and not args.url:
        print_error("Error: Please provide either input text, a file path, or a URL.")
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

    prompt = get_prompt(args.prompt)
    if prompt is None:
        return

    anonymized_content, placeholders = anonymize_sensitive_text(content)
    
    processed_content = process_with_anthropic(anonymized_content, prompt)

    if processed_content:
        final_content = deanonymize_text(processed_content, placeholders)
        print_success("Response from Claude LLM:\n")
        print(final_content)
        print("")
        pyperclip.copy(final_content)
        print_info("Output copied to clipboard.")
    else:
        print_warning("No content to display due to processing error.")

if __name__ == "__main__":
    main()
