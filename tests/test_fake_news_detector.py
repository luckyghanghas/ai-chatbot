import unittest

from projects.fake_news_detector.app import load_dataset, predict, train_model


class FakeNewsDetectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = train_model(load_dataset())

    def test_predict_fake_style_story(self):
        text = "A secret cure is being hidden by powerful groups and it works instantly."
        result = predict(text, self.model)
        self.assertEqual(result["label"], "fake")

    def test_predict_real_style_story(self):
        text = "The education board published official exam results after the review meeting."
        result = predict(text, self.model)
        self.assertEqual(result["label"], "real")


if __name__ == "__main__":
    unittest.main()
