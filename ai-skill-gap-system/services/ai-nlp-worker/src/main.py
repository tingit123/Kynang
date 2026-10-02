"""
AI NLP Worker – Main Entry Point
Tự động chạy, phân tích kỹ năng từ job postings và cập nhật skill gap
"""
import os
import time
import logging
import schedule

from extractor import SkillExtractor
from classifier import SkillClassifier
from gap_analyzer import GapAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [NLP-WORKER] %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def run_analysis():
    """Pipeline đầy đủ: Trích xuất → Phân loại → Tính gap."""
    log.info("🤖 Bắt đầu chu kỳ phân tích AI...")

    extractor  = SkillExtractor(api_url=API_BASE_URL)
    classifier = SkillClassifier()
    analyzer   = GapAnalyzer(api_url=API_BASE_URL)

    # Bước 1: Lấy job postings chưa được AI classify
    jobs = extractor.fetch_unclassified_jobs()
    log.info(f"   📋 Tìm thấy {len(jobs)} tin chưa phân tích")

    for job in jobs:
        # Bước 2: Trích xuất kỹ năng từ mô tả công việc
        skills = extractor.extract_skills(job.get("description", ""))
        log.info(f"   🔍 Job #{job['id']}: trích xuất được {len(skills)} kỹ năng")

        # Bước 3: Phân loại theo ngành
        classified = classifier.classify(skills, job.get("industry", "IT"))
        log.info(f"   🏷️  Đã phân loại: {classified}")

    # Bước 4: Tính toán và cập nhật skill gap
    analyzer.calculate_and_update_gap()
    log.info("✅ Hoàn tất chu kỳ phân tích AI")


if __name__ == "__main__":
    log.info("🚀 AI NLP Worker khởi động...")
    log.info(f"   API: {API_BASE_URL}")

    # Chạy ngay lần đầu
    run_analysis()

    # Lên lịch chạy mỗi 2 giờ
    schedule.every(2).hours.do(run_analysis)

    while True:
        schedule.run_pending()
        time.sleep(60)
