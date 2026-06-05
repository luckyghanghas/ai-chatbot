# AI-Powered FAQ Chatbot

An intelligent, interactive web-based FAQ Chatbot featuring natural language preprocessing (NLP), semantic similarity matching, and a dynamic keyless/keyed generative AI fallback engine. 

Designed with a premium glassmorphic interface, it responds to official support queries using a local database and handles off-topic or general queries dynamically.

---

## 🌟 Features

*   **Semantic Similarity Matching**:
    *   Preprocesses queries using NLTK (Tokenization, Stopwords removal, Lemmatization).
    *   Uses TF-IDF Vectorization and Cosine Similarity (Scikit-Learn) to match user input with the local FAQ dataset.
    *   Displays match confidence percentages.
*   **Dual Generative Fallback Engines**:
    *   **Keyless AI Fallback**: If a question doesn't match the FAQ dataset, the system automatically uses a keyless AI model (via `g4f` with `PollinationsAI`) to answer.
    *   **Gemini AI Fallback**: Supports configuring a Google Gemini API Key directly in the UI for official high-performance responses.
*   **Premium Glassmorphic UI**:
    *   Smooth floating gradient background orbs.
    *   Dynamic category filtering chips (All, General, Payments, Shipping, Issues).
    *   Click-to-ask FAQ directory explorer.
    *   Interactive greeting cards, quick suggestion chips, and typing indicators.
    *   Fully responsive sidebar for mobile devices.

---

## 🛠️ Tech Stack

*   **Frontend**: HTML5, CSS3 (Vanilla Custom Styles), JavaScript (Vanilla ES6), FontAwesome Icons.
*   **Backend**: Python, Flask, Flask-CORS.
*   **NLP & ML**: NLTK, Scikit-Learn, NumPy.
*   **Generative AI**: `g4f` (PollinationsAI), `google-generativeai` (Gemini API).

---

## 🚀 Getting Started

### 📋 Prerequisites

Make sure you have **Python 3.8+** installed on your system.

### 🔧 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/luckyghanghas/ai-chatbot.git
   cd ai-chatbot
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 🏃 Running the Application

Start the Flask development server:
```bash
python app.py
```

Open your browser and navigate to:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## ⚙️ Configuration

### Customizing FAQs
You can modify or expand the list of support questions by editing the `faqs.json` file in the root directory:
```json
{
  "id": 1,
  "category": "General",
  "question": "What is Antigravity Tech E-Store?",
  "answer": "Antigravity Tech E-Store is a premium online marketplace...",
  "tags": ["about", "company", "who are you"]
}
```

### Adding a Gemini API Key (Optional)
To use official Google Gemini models for fallbacks:
1. Click the **Gear Icon (⚙️)** in the top right corner of the chat header.
2. Paste your Gemini API Key.
3. Click **Save Key**. The key is stored securely in your browser's `localStorage` and sent with query headers.

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
