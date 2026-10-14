"""
Data Cleaner – Làm sạch và loại bỏ trùng lặp tin tuyển dụng
"""
import hashlib
import re
from typing import List, Dict


class DataCleaner:
    def __init__(self):
        self.seen_hashes = set()

    def clean_text(self, text: str) -> str:
        """Chuẩn hóa text: bỏ khoảng trắng thừa, ký tự đặc biệt."""
        if not text:
            return ""
        text = re.sub(r"\s+", " ", text.strip())
        text = re.sub(r"[^\w\s\-&/.,()]", "", text)
        return text

    def compute_hash(self, job: Dict) -> str:
        """Tạo hash duy nhất cho mỗi tin dựa trên title + company."""
        key = f"{job.get('title', '').lower()}|{job.get('company', '').lower()}"
        return hashlib.md5(key.encode("utf-8")).hexdigest()

    def is_duplicate(self, job: Dict) -> bool:
        """Kiểm tra tin có trùng lặp không."""
        h = self.compute_hash(job)
        if h in self.seen_hashes:
            return True
        self.seen_hashes.add(h)
        return False

    def clean_job(self, job: Dict) -> Dict:
        """Làm sạch một tin tuyển dụng."""
        return {
            "title":           self.clean_text(job.get("title", "")),
            "company":         self.clean_text(job.get("company", "")),
            "location":        self.clean_text(job.get("location", "Cần Thơ")),
            "industry":        job.get("industry", "Khác"),
            "description":     self.clean_text(job.get("description", "")),
            "salary_min":      job.get("salary_min"),
            "salary_max":      job.get("salary_max"),
            "posted_date":     job.get("posted_date"),
            "source_url":      job.get("source_url", ""),
            "source_platform": job.get("source_platform", ""),
            "duplicate_hash":  self.compute_hash(job),
        }

    def clean_and_deduplicate(self, jobs: List[Dict]) -> List[Dict]:
        """Làm sạch toàn bộ danh sách và loại bỏ trùng lặp."""
        cleaned = []
        duplicates = 0
        for job in jobs:
            if self.is_duplicate(job):
                duplicates += 1
                continue
            cleaned.append(self.clean_job(job))
        return cleaned, duplicates
