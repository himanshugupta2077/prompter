# LLM Processing CLI Tool
> Inspired by [fabric](https://github.com/danielmiessler/fabric) by Daniel Miessler.

This CLI tool processes text input using the Anthropic API, with support for anonymization, file input, URL content extraction, and custom prompts.

## Philosophy
- This tool was inspired by the concept of fabric and aims to streamline repetitive LLM-based tasks. It allows users to leverage pre-written prompts for various operations on different types of input (text, files, URLs, or lists of URLs). The core idea is that well-crafted prompts lead to better results, and this CLI tool makes it easy to apply these prompts consistently across various input sources, enhancing productivity and ensuring consistent output quality for frequently performed LLM operations.

## Features

- Process text input or file content with Anthropic's Claude LLM
- Anonymize sensitive information in the input
- Extract content from URLs or process multiple URLs from a file
- Use custom prompts stored in a local directory
- Save output to a file
- Copy output to clipboard automatically

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/llm-processing-cli.git
   cd llm-processing-cli
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your Anthropic API key as an environment variable:
   ```
   export ANTHROPIC_API_KEY=your_api_key_here
   ```

## Usage

```
python3 llm_processor.py [-h] [-i INPUT] [-f FILE] [-p PROMPT] [-l] [-u URL] [-uf URL_FILE] [-o [OUTPUT]] [-op OUTPUT_PATH]
```

### Arguments

- `-h`, `--help`: Show help message and exit
- `-i INPUT`, `--input INPUT`: User input text
- `-f FILE`, `--file FILE`: Input file path
- `-p PROMPT`, `--prompt PROMPT`: Prompt title
- `-l`, `--list`: List available prompts
- `-u URL`, `--url URL`: URL to extract content from
- `-uf URL_FILE`, `--url-file URL_FILE`: File containing URLs to process
- `-o [OUTPUT]`, `--output [OUTPUT]`: Save output to file (optional filename)
- `-op OUTPUT_PATH`, `--output-path OUTPUT_PATH`: Path to save the output file

### Examples

1. Process input text:
   ```
   python3 llm_processor.py -i "Your input text here"
   ```

2. Process a file:
   ```
   python3 llm_processor.py -f input.txt
   ```

3. Extract and process content from a URL:
   ```
   python3 llm_processor.py -u https://example.com
   ```

4. Process multiple URLs from a file:
   ```
   python3 llm_processor.py -uf urls.txt
   ```

5. Use a specific prompt:
   ```
   python3 llm_processor.py -i "Your input" -p custom_prompt
   ```

6. Save output to a file:
   ```
   python3 llm_processor.py -i "Your input" -o output.md
   ```

## Prompt Structure

Custom prompts should be stored in the `prompts` directory, with each prompt in its own subdirectory containing a `system.md` file.

Example:
```
prompts/
  custom_prompt/
    system.md
```

## Anonymization

Sensitive information in the input can be anonymized by enclosing it in double asterisks:
```
This is a **sensitive** piece of information.
```

