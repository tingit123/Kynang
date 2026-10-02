"""
Skill Extractor – Trích xuất kỹ năng từ mô tả công việc
Sử dụng rule-based keyword matching + regex
"""
import re
import logging
from typing import List, Dict
import requests

log = logging.getLogger(__name__)

# Danh sách kỹ năng cần nhận diện
SKILL_KEYWORDS = {
    "Python", "Java", "JavaScript", "TypeScript", "ReactJS", "Vue.js", "Node.js",
    "FastAPI", "Django", "Flask", "Docker", "Kubernetes", "Git", "CI/CD",
    "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis",
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
    "Data Analysis", "Power BI", "Tableau", "Excel", "Data Science",
    "AI Ethics", "NLP", "Computer Vision",
    "English", "Communication", "Problem Solving", "Customer Service",
    "Digital Marketing", "SEO", "Facebook Ads", "Google Ads", "Content Writing",
    "Logistics", "Supply Chain", "SAP", "Import/Export", "Negotiation",
    "Accounting", "MISA", "Financial Analysis", "Tax Law",
    "Hospitality", "Local Knowledge", "Tourism Management",
}


class SkillExtractor:
    def __init__(self, api_url: str):
        self.api_url = api_url

    def fetch_unclassified_jobs(self) -> List[Dict]:
        """Lấy danh sách job postings từ API."""
        try:
            resp = requests.get(f"{self.api_url}/api/jobs/", timeout=10)
            resp.raise_for_status()
            jobs = resp.json()
            return [j for j in jobs if not j.get("ai_classified", False)]
        except Exception as e:
            log.error(f"Không thể lấy jobs từ API: {e}")
            return []

    def extract_skills(self, text: str) -> List[str]:
        """Trích xuất kỹ năng từ text bằng keyword matching."""
        if not text:
            return []
        found_skills = []
        text_lower = text.lower()
        for skill in SKILL_KEYWORDS:
            # Tìm cả cụm từ (word boundary matching)
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)
        return list(set(found_skills))

