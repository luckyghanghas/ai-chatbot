import unittest

from chatbot import DEFAULT_FALLBACK, clean_text, get_response, load_intents


class ChatbotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.intents = load_intents()

    def test_clean_text_removes_punctuation(self):
        self.assertEqual(clean_text("Hello!!!"), "hello")

    def test_greeting_response_matches_known_intent(self):
        response = get_response("hello", self.intents)
        greeting_responses = self.intents["intents"][0]["responses"]
        self.assertIn(response, greeting_responses)

    def test_unknown_question_uses_fallback(self):
        response = get_response("tell me about quantum robots", self.intents)
        self.assertEqual(response, DEFAULT_FALLBACK)


if __name__ == "__main__":
    unittest.main()
