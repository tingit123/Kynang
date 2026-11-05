"""
Scheduler – Điều phối lịch cào dữ liệu tự động
Mỗi 6 giờ cào một lần, gửi dữ liệu lên API
"""
import os
import logging
import time
import schedule
import requests

from crawler import JobCrawler
from cleaner import DataCleaner

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CRAWLER] %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)

API_BASE_URL   = os.getenv("API_BASE_URL", "http://localhost:8000")
CRAWL_INTERVAL = int(os.getenv("CRAWL_INTERVAL_HOURS", "6"))


def send_to_api(jobs: list) -> int:
    """Gửi danh sách jobs lên Core API, trả về số job đã lưu."""
    saved = 0
    for job in jobs:
        try:
            resp = requests.post(
                f"{API_BASE_URL}/api/jobs/",
                json=job,
                timeout=15,
            )
            if resp.status_code in (200, 201):
                saved += 1
            elif resp.status_code == 409:
                log.debug(f"Duplicate skipped: {job.get('title')}")
        except Exception as e:
            log.warning(f"Không gửi được job lên API: {e}")
    return saved


def run_crawl():
    """Một chu kỳ crawl đầy đủ."""
    log.info("=" * 50)
    log.info("🕷️  BẮT ĐẦU CHU KỲ CÀO DỮ LIỆU")
    log.info("=" * 50)

    crawler = JobCrawler(api_url=API_BASE_URL)
    cleaner = DataCleaner()

    # Bước 1: Cào dữ liệu
    raw_jobs = crawler.crawl_all()
    log.info(f"📥 Cào được: {len(raw_jobs)} tin thô")

    # Bước 2: Làm sạch & loại trùng
    clean_jobs, dup_count = cleaner.clean_and_deduplicate(raw_jobs)
    log.info(f"🧹 Sau làm sạch: {len(clean_jobs)} tin (bỏ {dup_count} trùng)")

    # Bước 3: Gửi lên API
    saved = send_to_api(clean_jobs)
    log.info(f"💾 Đã lưu: {saved}/{len(clean_jobs)} tin vào DB")
    log.info("✅ Hoàn tất chu kỳ cào\n")


if __name__ == "__main__":
    log.info("🚀 Data Crawler khởi động...")
    log.info(f"   API: {API_BASE_URL}")
    log.info(f"   Chu kỳ cào: mỗi {CRAWL_INTERVAL} giờ")

    # Chạy ngay lần đầu
    run_crawl()

    # Lên lịch tự động
    schedule.every(CRAWL_INTERVAL).hours.do(run_crawl)

    while True:
        schedule.run_pending()
        time.sleep(60)
