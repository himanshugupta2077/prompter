import os
import argparse
import re
import anthropic
from pathlib import Path
from colorama import init, Fore, Style

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
        # print_success("Processing complete.")
        return processed_content
    except Exception as e:
        print_error(f"Error processing with Anthropic API: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="CLI tool for LLM processing with anonymization")
    parser.add_argument("-i", "--input", help="User input or file path")
    parser.add_argument("-f", "--file", help="Input file path")
    parser.add_argument("-p", "--prompt", default="ai", help="Prompt title (default: ai)")
    args = parser.parse_args()

    if not args.input and not args.file:
        print_error("Error: Please provide either input text or a file path.")
        return

    content = args.input
    if args.file:
        print_info(f"Reading input from file: {args.file}")
        content = read_file(args.file)
        if content is None:
            return

    # print_info(f"Using prompt: {args.prompt}")
    prompt = get_prompt(args.prompt)
    if prompt is None:
        return

    # print_info("Anonymizing sensitive text...")
    anonymized_content, placeholders = anonymize_sensitive_text(content)
    
    processed_content = process_with_anthropic(anonymized_content, prompt)

    if processed_content:
        # print_info("Deanonymizing processed content...")
        final_content = deanonymize_text(processed_content, placeholders)
        print_success("Response from claude LLM:\n")
        print(final_content)  # This is the LLM output, so we don't color it
        print("")
    else:
        print_warning("No content to display due to processing error.")

if __name__ == "__main__":
    main()