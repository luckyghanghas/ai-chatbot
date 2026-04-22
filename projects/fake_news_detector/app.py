import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
STOP_WORDS = {
    "a", "an", "the", "and", "or", "is", "are", "was", "were", "to", "of",
    "in", "on", "for", "with", "at", "by", "from", "that", "this", "it",
    "as", "be", "has", "have", "had", "will", "would", "can", "could"
}


def load_dataset(file_name="dataset.json"):
    with open(BASE_DIR / file_name, "r", encoding="utf-8") as file:
        return json.load(file)["articles"]


def tokenize(text):
    words = re.findall(r"[a-zA-Z']+", text.lower())
    return [word for word in words if word not in STOP_WORDS and len(word) > 2]


def train_model(dataset):
    class_word_counts = defaultdict(Counter)
    class_doc_counts = Counter()
    vocabulary = set()

    for item in dataset:
        label = item["label"]
        tokens = tokenize(item["text"])
        class_doc_counts[label] += 1
        class_word_counts[label].update(tokens)
        vocabulary.update(tokens)

    return {
        "class_word_counts": class_word_counts,
        "class_doc_counts": class_doc_counts,
        "vocabulary": vocabulary,
        "total_docs": sum(class_doc_counts.values()),
    }


def predict(text, model):
    tokens = tokenize(text)
    vocabulary_size = len(model["vocabulary"]) or 1
    scores = {}

    for label, doc_count in model["class_doc_counts"].items():
        log_prob = math.log(doc_count / model["total_docs"])
        total_words = sum(model["class_word_counts"][label].values())

        for token in tokens:
            token_count = model["class_word_counts"][label][token]
            token_prob = (token_count + 1) / (total_words + vocabulary_size)
            log_prob += math.log(token_prob)

        scores[label] = log_prob

    best_label = max(scores, key=scores.get)
    sorted_scores = sorted(scores.values(), reverse=True)
    gap = sorted_scores[0] - sorted_scores[1] if len(sorted_scores) > 1 else 0
    confidence = round(min(99.0, 50 + (gap * 10)), 2)

    return {
        "label": best_label,
        "confidence": confidence,
        "tokens_used": tokens,
    }


def main():
    dataset = load_dataset()
    model = train_model(dataset)

    sample_text = (
        "Breaking report claims a miracle herb instantly cures every disease and "
        "governments are hiding the truth from citizens."
    )
    result = predict(sample_text, model)

    print("Fake News Detector")
    print("=" * 19)
    print(f"Prediction: {result['label'].upper()}")
    print(f"Confidence: {result['confidence']}%")
    print(f"Processed Tokens: {', '.join(result['tokens_used'])}")


if __name__ == "__main__":
    main()
