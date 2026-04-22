import json
import re
from collections import Counter
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def load_text(file_name):
    return (BASE_DIR / file_name).read_text(encoding="utf-8")


def load_skills(file_name="skills.json"):
    with open(BASE_DIR / file_name, "r", encoding="utf-8") as file:
        return json.load(file)["skills"]


def normalize_text(text):
    return re.sub(r"[^a-zA-Z0-9+#.\s]", " ", text.lower())


def extract_skills(text, skill_list):
    normalized_text = normalize_text(text)
    found_skills = set()

    for skill in skill_list:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, normalized_text):
            found_skills.add(skill)

    return sorted(found_skills)


def calculate_match_score(resume_skills, job_skills):
    if not job_skills:
        return 0

    matched = set(resume_skills) & set(job_skills)
    return round((len(matched) / len(job_skills)) * 100, 2)


def keyword_frequency(text):
    words = re.findall(r"[a-zA-Z0-9+#.]+", text.lower())
    return Counter(words)


def analyze_resume(resume_text, job_description_text, skill_list):
    resume_skills = extract_skills(resume_text, skill_list)
    job_skills = extract_skills(job_description_text, skill_list)
    matched_skills = sorted(set(resume_skills) & set(job_skills))
    missing_skills = sorted(set(job_skills) - set(resume_skills))
    score = calculate_match_score(resume_skills, job_skills)
    freq = keyword_frequency(resume_text)

    return {
        "resume_skills": resume_skills,
        "job_skills": job_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_score": score,
        "top_resume_keywords": freq.most_common(10),
    }


def print_report(report):
    print("Resume Analyzer Report")
    print("=" * 24)
    print(f"Match Score: {report['match_score']}%")
    print(f"Job Skills: {', '.join(report['job_skills']) or 'None detected'}")
    print(f"Matched Skills: {', '.join(report['matched_skills']) or 'None'}")
    print(f"Missing Skills: {', '.join(report['missing_skills']) or 'None'}")
    print("Top Resume Keywords:")

    for keyword, count in report["top_resume_keywords"]:
        print(f"- {keyword}: {count}")


def main():
    skills = load_skills()
    resume_text = load_text("sample_resume.txt")
    job_description_text = load_text("sample_job_description.txt")
    report = analyze_resume(resume_text, job_description_text, skills)
    print_report(report)


if __name__ == "__main__":
    main()
