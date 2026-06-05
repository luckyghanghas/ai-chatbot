import os
import json
import re
import string
import concurrent.futures
import urllib.request
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

# Optional NLP imports - wrapped with fallback
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Machine learning imports
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Google Generative AI import (new SDK)
from google import genai
from google.genai import types

# Keyless fallback import
import g4f

# Initialize NLTK resources safely
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)

# Preprocessing utilities
stop_words_set = set()
try:
    stop_words_set = set(stopwords.words('english'))
except Exception:
    # Basic English stop words fallback
    stop_words_set = {"i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", 
                      "he", "him", "his", "she", "her", "it", "its", "they", "them", "what", "which", "who", 
                      "whom", "this", "that", "am", "is", "are", "was", "were", "be", "been", "being", "have", 
                      "has", "had", "do", "does", "did", "the", "a", "an", "and", "but", "if", "or", "because", 
                      "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", 
                      "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", 
                      "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once"}

lemmatizer = None
try:
    lemmatizer = WordNetLemmatizer()
except Exception:
    lemmatizer = None

def preprocess_text(text):
    # Lowercase
    text = text.lower()
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Tokenization
    try:
        tokens = word_tokenize(text)
    except Exception:
        # Fallback simple split
        tokens = re.findall(r'\b\w+\b', text)
    
    # Stop words removal & Lemmatization
    cleaned_tokens = []
    for token in tokens:
        if token not in stop_words_set:
            if lemmatizer:
                try:
                    token = lemmatizer.lemmatize(token)
                except Exception:
                    pass
            cleaned_tokens.append(token)
            
    return " ".join(cleaned_tokens)

# Flask configuration
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Load FAQ data
FAQ_FILE = os.path.join(os.path.dirname(__file__), 'faqs.json')
try:
    with open(FAQ_FILE, 'r', encoding='utf-8') as f:
        faqs = json.load(f)
except Exception as e:
    print(f"Error loading FAQs: {e}")
    faqs = []

# Precompute vectors for FAQ questions
def init_vectorizer():
    global vectorizer, faq_vectors, preprocessed_questions
    if not faqs:
        return
    
    # Combine question and tags to improve matching context
    preprocessed_questions = []
    for faq in faqs:
        question_text = faq['question']
        tags_text = " ".join(faq.get('tags', []))
        # Give higher weight to the actual question by repeating it
        combined_text = f"{question_text} {question_text} {tags_text}"
        preprocessed_questions.append(preprocess_text(combined_text))
        
    vectorizer = TfidfVectorizer()
    faq_vectors = vectorizer.fit_transform(preprocessed_questions)

init_vectorizer()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/faqs', methods=['GET'])
def get_faqs():
    return jsonify(faqs)

@app.route('/api/chat', methods=['POST'])
def chat():
    if not faqs:
        return jsonify({
            "answer": "FAQ database is currently empty. Please add some FAQs first.",
            "confidence": 0.0,
            "match": None
        })

    data = request.json or {}
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({
            "answer": "I didn't catch that. Could you please type your question?",
            "confidence": 0.0,
            "match": None
        })
        
    # Preprocess user query
    processed_query = preprocess_text(user_message)
    
    # If the user query is completely empty after preprocessing (e.g. only stopwords/punctuation)
    if not processed_query:
        processed_query = user_message.lower()

    # Transform query to TF-IDF
    query_vector = vectorizer.transform([processed_query])
    
    # Compute similarity
    similarities = cosine_similarity(query_vector, faq_vectors).flatten()
    
    # Find best match
    best_match_idx = np.argmax(similarities)
    best_score = float(similarities[best_match_idx])
    
    # Confidence threshold
    THRESHOLD = 0.22
    
    # Check for API key (prioritize header, then environment)
    # Supports Gemini key (X-Gemini-Key) and Groq key (X-Groq-Key)
    api_key = request.headers.get('X-Gemini-Key') or os.environ.get('GEMINI_API_KEY')
    groq_key = request.headers.get('X-Groq-Key') or os.environ.get('GROQ_API_KEY')
    
    if best_score >= THRESHOLD:
        best_match = faqs[best_match_idx]
        
        # Get alternative recommendations if any are relatively close
        suggestions = []
        for i, score in enumerate(similarities):
            if i != best_match_idx and score > 0.15:
                suggestions.append(faqs[i]['question'])
                if len(suggestions) >= 2:
                    break
                    
        return jsonify({
            "answer": best_match['answer'],
            "confidence": best_score,
            "matched_question": best_match['question'],
            "category": best_match['category'],
            "suggestions": suggestions,
            "is_generated": False
        })

    # Build shared prompt for all AI backends
    context_string = "\n".join([f"Q: {f['question']}\nA: {f['answer']}" for f in faqs])
    ai_prompt = (
        "You are an intelligent FAQ chatbot assistant for Antigravity Tech E-Store.\n"
        "Here is the database of official FAQs:\n"
        f"{context_string}\n\n"
        f"User Question: \"{user_message}\"\n\n"
        "Instructions:\n"
        "1. If the user's question is answered in the FAQs, use that information to construct the reply.\n"
        "2. If it is NOT in the FAQs, answer their question directly, accurately, and politely as a general customer service representative.\n"
        "3. Keep your reply concise (1-3 sentences) and professional."
    )

    # --- Backend 1: Groq (free, fast, reliable) ---
    if groq_key:
        try:
            payload = json.dumps({
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": ai_prompt}],
                "max_tokens": 200
            }).encode()
            req = urllib.request.Request(
                "https://api.groq.com/openai/v1/chat/completions",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {groq_key}"
                }
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                groq_data = json.loads(r.read())
            groq_answer = groq_data["choices"][0]["message"]["content"].strip()
            if groq_answer:
                return jsonify({
                    "answer": groq_answer,
                    "confidence": 1.0,
                    "matched_question": "Generative Fallback",
                    "category": "AI Assistant",
                    "suggestions": [],
                    "is_generated": True
                })
        except Exception as e:
            print(f"Groq API Error: {e}")

    # --- Backend 2: Gemini ---
    if api_key:
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=ai_prompt
            )
            generated_answer = response.text.strip()
            return jsonify({
                "answer": generated_answer,
                "confidence": 1.0,
                "matched_question": "Generative Fallback",
                "category": "AI Assistant",
                "suggestions": [],
                "is_generated": True
            })
        except Exception as e:
            print(f"Gemini API Error: {e}")

    # No match and no API key — keyless fallback
    context_string_short = "\n".join([f"Q: {f['question']}\nA: {f['answer']}" for f in faqs[:5]])
    prompt = (
        "You are an FAQ chatbot assistant for Antigravity Tech E-Store.\n"
        "Here is the database of official FAQs:\n"
        f"{context_string_short}\n\n"
        f"User Question: \"{user_message}\"\n\n"
        "Instructions:\n"
        "1. If the user's question is answered in the FAQs, use that information to construct the reply.\n"
        "2. If it is NOT in the FAQs, answer their question directly, accurately, and politely as a general customer service representative.\n"
        "3. Keep your reply concise (1-3 sentences) and professional."
    )

    # Helper: strip internal reasoning/thinking blocks from model output
    def clean_answer(text):
        text = str(text).strip()
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
        return text

    # --- Keyless Fallback: Pollinations.ai REST API (GET request, no auth, no rate limit per IP) ---
    def call_pollinations(user_msg):
        import urllib.parse
        encoded = urllib.parse.quote(user_msg)
        url = f"https://text.pollinations.ai/{encoded}?model=openai&system=You+are+a+helpful+FAQ+assistant+for+Antigravity+Tech+E-Store.+Be+concise+and+professional."
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read().decode('utf-8').strip()

    try:
        poll_answer = call_pollinations(
            f"FAQ context:\n{context_string}\n\nUser question: {user_message}\n\nAnswer concisely in 1-3 sentences as a customer service rep."
        )
        if poll_answer and len(poll_answer) > 5:
            return jsonify({
                "answer": clean_answer(poll_answer),
                "confidence": 1.0,
                "matched_question": "Generative Fallback (Keyless)",
                "category": "AI Assistant",
                "suggestions": [],
                "is_generated": True
            })
    except Exception as e:
        print(f"Pollinations Fallback Error: {e}")

    # --- Secondary Keyless Fallback: g4f with working providers ---
    def call_g4f_provider(provider):
        return g4f.ChatCompletion.create(
            model=g4f.models.default,
            provider=provider,
            messages=[{"role": "user", "content": prompt}]
        )

    keyless_providers = [
        g4f.Provider.Qwen_Qwen_3,
        g4f.Provider.BlackboxPro,
        g4f.Provider.DeepInfra,
        g4f.Provider.PollinationsAI,
    ]

    for provider in keyless_providers:
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(call_g4f_provider, provider)
                generated_answer = future.result(timeout=10)
            cleaned = clean_answer(generated_answer)
            if cleaned and len(cleaned) > 5:
                return jsonify({
                    "answer": cleaned,
                    "confidence": 1.0,
                    "matched_question": "Generative Fallback (Keyless)",
                    "category": "AI Assistant",
                    "suggestions": [],
                    "is_generated": True
                })
        except Exception as e:
            print(f"Keyless Fallback Error ({provider.__name__}): {e}")
            continue

    # Fallback to local suggestion chips if all AI systems fail
    fallback_suggestions = []
    sorted_indices = np.argsort(similarities)[::-1]
    for idx in sorted_indices[:3]:
        if similarities[idx] > 0.05:
            fallback_suggestions.append(faqs[int(idx)]['question'])
            
    if not fallback_suggestions:
        fallback_suggestions = [faq['question'] for faq in faqs[:3]]

    return jsonify({
        "answer": "I couldn't find a match for that in our FAQs. Add a free API key in settings (⚙️ gear icon) to enable AI answers — get a free Groq key at console.groq.com or a Gemini key at aistudio.google.com.",
        "confidence": best_score,
        "matched_question": None,
        "category": None,
        "suggestions": fallback_suggestions,
        "is_generated": False
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
