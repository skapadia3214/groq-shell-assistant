# Groq Shell Assistant

## Overview
Groq Shell Assistant is a conversational AI assistant that can interact with users and call external tools to perform tasks.

## Setup

### Prerequisites
* Python 3.8+
* pip

### Clone the Repository
```bash
https://github.com/skapadia3214/groq-shell-assistant.git
```

### Install Dependencies
```bash
cd groq-shell-assistant
pip install -r requirements.txt
```

### Set up Environment Variables
Create a `.env` file in the root of the repository with the following contents:
```makefile
GROQ_API_KEY=<your-groq-api-key>
TAVILY_API_KEY=<your-tavily-api-key> (optional)
```

### Run the Assistant
```bash
python main.py
```

## Optional Arguments
You can run the main.py with some optional arguments:

* `--model`: Specify the Groq model to use (default: `llama-3.1-70b-versatile`)
* `--messages`: Specify initial messages in JSON format
* `--current_dir`: Specify the current working directory

### Interacting with the Assistant
To interact with the assistant, simply type a message and press enter. The assistant will respond with a helpful response.

## Contributing

Contributions are welcome! To contribute, simply fork the repository, make your changes, and submit a pull request.

## License

This project is licensed under the Apache License 2.0. See the LICENSE file for details.
