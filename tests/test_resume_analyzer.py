import unittest

from projects.resume_analyzer.app import analyze_resume, extract_skills


class ResumeAnalyzerTests(unittest.TestCase):
    def setUp(self):
        self.skills = ["python", "sql", "excel", "machine learning", "communication"]
        self.resume = "I know Python, SQL, and communication."
        self.job = "We need Python, SQL, Excel, and machine learning."

    def test_extract_skills_finds_known_matches(self):
        extracted = extract_skills(self.resume, self.skills)
        self.assertEqual(extracted, ["communication", "python", "sql"])

    def test_analyze_resume_calculates_score_and_missing_skills(self):
        report = analyze_resume(self.resume, self.job, self.skills)
        self.assertEqual(report["match_score"], 50.0)
        self.assertEqual(report["missing_skills"], ["excel", "machine learning"])


if __name__ == "__main__":
    unittest.main()
