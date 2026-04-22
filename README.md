# AI Chatbot

A simple AI-style chatbot project built with Python. It accepts user questions in the terminal and replies automatically using an intent-based response system.

## Features

- Accepts user input from the terminal
- Responds automatically with matching answers
- Uses a clean `intents.json` file for chatbot data
- Easy to expand with new questions and responses
- Includes a basic test file for quick verification

## Tech Stack

- Python
- JSON
- NLP-style text cleaning with regular expressions

## Project Structure

```text
ai-chatbot/
|-- chatbot.py
|-- intents.json
|-- test_chatbot.py
|-- requirements.txt
|-- .gitignore
|-- LICENSE
|-- README.md
```

## How It Works

The chatbot normalizes user input, compares it against known patterns stored in `intents.json`, and returns a matching response. If no intent matches, it returns a fallback message.

## Setup

1. Make sure Python 3 is installed.
2. Open the project folder.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run The Chatbot

```bash
python chatbot.py
```

Type `exit` to close the chatbot.

## Run Tests

```bash
python -m unittest test_chatbot.py
```

## Example

```text
AI Chatbot started. Type 'exit' to quit.
You: hello
Bot: Hello! How can I help you today?

You: what is your name
Bot: I am your AI chatbot assistant.
```

## Future Improvements

- Add TensorFlow-based intent classification
- Add speech input and speech output
- Build a GUI with Tkinter, Flask, or Streamlit
- Add more intents and custom training data
- Integrate OpenCV for webcam-based features

## License

This project is licensed under the MIT License.
