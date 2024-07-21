# Prompter

## LLM Processing Tool with Anonymization

> This tool processes content using the Anthropic API with customizable prompts and anonymization features.
It supports input from text, files, or URLs, and provides a user-friendly command-line interface.

### Key Features:
- Content anonymization and de-anonymization
- Custom prompt selection
- Input from text, file, or URL
- Colorized console output
- Clipboard integration for easy output copying

### Usage:
python script_name.py [-h] [-i INPUT] [-f FILE] [-p PROMPT] [-l] [-u URL]

### Dependencies:
- anthropic
- pyperclip
- colorama
- readability-lxml
- requests
- argcomplete
