# Prompter

## LLM Processing Tool with Anonymization

> This tool processes content using the Anthropic API with customizable prompts and anonymization features.
It supports input from text, files, or URLs, and provides a user-friendly command-line interface.

### Key Features
- Content anonymization and de-anonymization
- Custom prompt selection
- Input from text, file, or URL
- Colorized console output
- Clipboard integration for easy output copying

### Usage
python script_name.py [-h] [-i INPUT] [-f FILE] [-p PROMPT] [-l] [-u URL]

### Dependencies
- anthropic
- pyperclip
- colorama
- readability-lxml
- requests
- argcomplete

### Installation Guide

Below guide explains how to install a Python tool so it can be called from anywhere in PowerShell or terminal.

#### Windows

1. Ensure your Python script has a shebang line:
   At the top of your Python file, add:
   ```python
   #!/usr/bin/env python3
   ```

2. Rename the script (optional):
   You might want to rename it without the .py extension for easier calling:
   ```
   ren your_script.py your_script
   ```

3. Create a directory for your scripts:
   ```
   mkdir C:\Users\YourUsername\Scripts
   ```

4. Move your script to this directory.

5. Add the directory to your PATH:
   - Open PowerShell as administrator
   - Run the following command:
     ```powershell
     [Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Users\YourUsername\Scripts", "User")
     ```
   - Close and reopen PowerShell for changes to take effect

Now you should be able to call your script from anywhere in PowerShell.

#### Linux/Mac

1. Ensure your Python script has a shebang line:
   At the top of your Python file, add:
   ```python
   #!/usr/bin/env python3
   ```

2. Make the script executable:
   ```bash
   chmod +x your_script.py
   ```

3. Rename the script (optional):
   ```bash
   mv your_script.py your_script
   ```

4. Move the script to a directory in your PATH:
   ```bash
   sudo mv your_script /usr/local/bin
   ```

5. If you prefer not to use /usr/local/bin, you can create a new directory and add it to your PATH:
   ```bash
   mkdir ~/bin
   mv your_script ~/bin
   echo 'export PATH=$PATH:~/bin' >> ~/.bashrc
   source ~/.bashrc
   ```

Now you should be able to call your script from anywhere in the terminal.
