# AI Projects Portfolio

A GitHub-ready Python portfolio with practical AI and analytics mini-projects. Each project is designed to run locally with simple commands and minimal setup.

## Included Projects

### 1. Resume Analyzer

Compare a resume against a job description, calculate a skill match score, identify matched skills, and suggest missing skills.

### 2. Fake News Detector

Classify a news article as likely real or fake using a lightweight NLP pipeline and a small built-in training dataset.

### 3. AI Chatbot

A basic intent-based chatbot that replies automatically in the terminal.

## Project Structure

```text
ai-projects-portfolio/
|-- chatbot.py
|-- intents.json
|-- projects/
|   |-- fake_news_detector/
|   |   |-- app.py
|   |   |-- dataset.json
|   |   |-- README.md
|   |-- resume_analyzer/
|   |   |-- app.py
|   |   |-- sample_job_description.txt
|   |   |-- sample_resume.txt
|   |   |-- skills.json
|   |   |-- README.md
|-- tests/
|   |-- test_chatbot.py
|   |-- test_fake_news_detector.py
|   |-- test_resume_analyzer.py
|-- .gitignore
|-- LICENSE
|-- README.md
```

## Requirements

- Python 3
- No external packages required for the current version

## How To Run

### Chatbot

```bash
python chatbot.py
```

### Resume Analyzer

```bash
python projects/resume_analyzer/app.py
```

### Fake News Detector

```bash
python projects/fake_news_detector/app.py
```

## Run Tests

```bash
python -m unittest discover -s tests
```

## Why These Projects Stand Out

- They are easy to demo in interviews and on GitHub
- They use practical AI and analytics ideas
- They are structured like real mini products, not just code snippets
- They are easy to upgrade later with TensorFlow, scikit-learn, Flask, or Streamlit

## License

This project is licensed under the MIT License.
