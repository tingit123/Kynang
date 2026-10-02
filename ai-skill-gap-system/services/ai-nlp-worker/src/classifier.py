"""
Skill Classifier – Phân loại kỹ năng theo ngành
"""
from typing import List, Dict

INDUSTRY_SKILL_MAP = {
    "IT": {
        "Python", "Java", "JavaScript", "TypeScript", "ReactJS", "Node.js",
        "FastAPI", "Django", "Docker", "SQL", "Machine Learning", "Deep Learning",
        "TensorFlow", "Data Analysis", "AI Ethics", "NLP", "Git", "CI/CD",
    },
    "Kinh tế": {
        "Digital Marketing", "SEO", "Facebook Ads", "Google Ads",
        "Accounting", "MISA", "Financial Analysis", "Tax Law", "Excel",
        "Content Writing",
    },
    "Logistics": {
        "Logistics", "Supply Chain", "SAP", "Import/Export",
        "Negotiation", "Problem Solving",
    },
    "Du lịch": {
        "Customer Service", "Communication", "English",
        "Hospitality", "Local Knowledge", "Tourism Management",
    },
    "Tất cả": {
        "English", "Communication", "Problem Solving", "Customer Service",
    },
}


class SkillClassifier:
    def classify(self, skills: List[str], job_industry: str) -> Dict[str, str]:
        """Phân loại từng kỹ năng vào ngành phù hợp."""
        result = {}
        for skill in skills:
            assigned = "Khác"
            # Kiểm tra theo ngành job trước
            if job_industry in INDUSTRY_SKILL_MAP:
                if skill in INDUSTRY_SKILL_MAP[job_industry]:
                    assigned = job_industry
            # Tìm trong tất cả ngành
            if assigned == "Khác":
                for industry, skill_set in INDUSTRY_SKILL_MAP.items():
                    if skill in skill_set:
                        assigned = industry
                        break
            result[skill] = assigned
        return result
