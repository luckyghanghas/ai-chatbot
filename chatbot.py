import json
import random
import re


def load_intents(file_path="intents.json"):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def clean_text(text):
    return re.sub(r"[^a-zA-Z0-9\s]", "", text.lower()).strip()


def get_response(user_input, intents):
    text = clean_text(user_input)

    for intent in intents["intents"]:
        for pattern in intent["patterns"]:
            if clean_text(pattern) in text or text in clean_text(pattern):
                return random.choice(intent["responses"])

    return "Sorry, I do not understand that yet. Try asking something else."


def main():
    intents = load_intents()
    print("AI Chatbot started. Type 'exit' to quit.")

    while True:
        user_input = input("You: ")

        if user_input.lower().strip() == "exit":
            print("Bot: Goodbye!")
            break

        response = get_response(user_input, intents)
        print(f"Bot: {response}")


if __name__ == "__main__":
    main()
