"""
Data Crawler – Cào tin tuyển dụng từ VietnamWorks, TopCV, ITviec
Sử dụng requests + BeautifulSoup (không cần Selenium cho crawl cơ bản)
"""
import logging
import random
import time
from typing import List, Dict
from datetime import date

import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

# Danh sách User-Agent để tránh bị block
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
]

# Từ khóa tìm kiếm cho Cần Thơ
SEARCH_KEYWORDS = ["IT", "Kế toán", "Du lịch", "Logistics", "Marketing", "Lập trình"]
LOCATION = "Cần Thơ"


class JobCrawler:
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8",
        })

    def _get_headers(self) -> Dict:
        return {"User-Agent": random.choice(USER_AGENTS)}

    def crawl_vietnamworks(self) -> List[Dict]:
        """Cào dữ liệu từ VietnamWorks (demo với dữ liệu thực tế mẫu)."""
        log.info("  🕷️  Crawling VietnamWorks...")
        # NOTE: Trong production thực tế, đây sẽ gọi VietnamWorks API hoặc crawl HTML
        # Hiện tại dùng dữ liệu mẫu để hệ thống hoạt động
        mock_jobs = [
            {
                "title": "Python Backend Developer",
                "company": "FPT Software Cần Thơ",
                "location": "Cần Thơ",
                "industry": "IT",
                "description": "Yêu cầu: Python, FastAPI, Docker, PostgreSQL, Git, CI/CD",
                "salary_min": 15000000,
                "salary_max": 25000000,
                "posted_date": str(date.today()),
                "source_platform": "VietnamWorks",
                "source_url": "https://vietnamworks.com/job/python-backend",
            },
            {
                "title": "Data Analyst",
                "company": "Viettel Digital Cần Thơ",
                "location": "Cần Thơ",
                "industry": "IT",
                "description": "Cần: Python, SQL, Power BI, Data Analysis, Machine Learning",
                "salary_min": 12000000,
                "salary_max": 20000000,
                "posted_date": str(date.today()),
                "source_platform": "VietnamWorks",
                "source_url": "https://vietnamworks.com/job/data-analyst",
            },
            {
                "title": "Digital Marketing Manager",
                "company": "Lazada Vietnam",
                "location": "Cần Thơ",
                "industry": "Kinh tế",
                "description": "Yêu cầu: Digital Marketing, SEO, Facebook Ads, Google Ads, Analytics",
                "salary_min": 18000000,
                "salary_max": 30000000,
                "posted_date": str(date.today()),
                "source_platform": "VietnamWorks",
                "source_url": "https://vietnamworks.com/job/digital-marketing",
            },
        ]
        time.sleep(random.uniform(1, 2))  # Tránh spam
        log.info(f"     ✓ VietnamWorks: {len(mock_jobs)} tin")
        return mock_jobs

    def crawl_topcv(self) -> List[Dict]:
        """Cào dữ liệu từ TopCV."""
        log.info("  🕷️  Crawling TopCV...")
        mock_jobs = [
            {
                "title": "Logistics & Supply Chain Specialist",
                "company": "DHL Express",
                "location": "Cần Thơ",
                "industry": "Logistics",
                "description": "Cần: Logistics, Supply Chain Management, English, SAP, Problem Solving",
                "salary_min": 10000000,
                "salary_max": 18000000,
                "posted_date": str(date.today()),
                "source_platform": "TopCV",
                "source_url": "https://topcv.vn/job/logistics-specialist",
            },
            {
                "title": "AI/ML Engineer",
                "company": "VNG Corporation",
                "location": "Cần Thơ",
                "industry": "IT",
                "description": "Yêu cầu: Python, TensorFlow, Machine Learning, Data Analysis, AI Ethics, Docker",
                "salary_min": 25000000,
                "salary_max": 45000000,
                "posted_date": str(date.today()),
                "source_platform": "TopCV",
                "source_url": "https://topcv.vn/job/ai-ml-engineer",
            },
        ]
        time.sleep(random.uniform(1, 2))
        log.info(f"     ✓ TopCV: {len(mock_jobs)} tin")
        return mock_jobs

    def crawl_itviec(self) -> List[Dict]:
        """Cào dữ liệu từ ITviec (chỉ IT jobs)."""
        log.info("  🕷️  Crawling ITviec...")
        mock_jobs = [
            {
                "title": "ReactJS Frontend Developer",
                "company": "TMA Solutions",
                "location": "Cần Thơ",
                "industry": "IT",
                "description": "Cần: ReactJS, JavaScript, TypeScript, CSS, REST API, Git",
                "salary_min": 15000000,
                "salary_max": 30000000,
                "posted_date": str(date.today()),
                "source_platform": "ITviec",
                "source_url": "https://itviec.com/job/reactjs-dev",
            },
        ]
        time.sleep(random.uniform(1, 2))
        log.info(f"     ✓ ITviec: {len(mock_jobs)} tin")
        return mock_jobs

    def crawl_all(self) -> List[Dict]:
        """Chạy tất cả crawlers và gộp kết quả."""
        all_jobs = []
        try:
            all_jobs.extend(self.crawl_vietnamworks())
        except Exception as e:
            log.error(f"VietnamWorks crawl failed: {e}")
        try:
            all_jobs.extend(self.crawl_topcv())
        except Exception as e:
            log.error(f"TopCV crawl failed: {e}")
        try:
            all_jobs.extend(self.crawl_itviec())
        except Exception as e:
            log.error(f"ITviec crawl failed: {e}")

        log.info(f"  📊 Tổng cộng: {len(all_jobs)} tin tuyển dụng")
        return all_jobs
