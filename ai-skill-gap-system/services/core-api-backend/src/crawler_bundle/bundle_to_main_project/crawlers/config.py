"""
config.py - Cấu hình hệ thống Crawler TopCV.vn
Dự án: Skill Gap Analysis tại khu vực Đà Nẵng mở rộng (Đà Nẵng, Huế, Quảng Ngãi)
"""

import os

# Đường dẫn thư mục gốc của project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Đường dẫn file ghi nhận lỗi
ERROR_LOG_PATH = os.path.join(BASE_DIR, "errors.log")

# ==============================================================================
import os

# 1. CẤU HÌNH KẾT NỐI CƠ SỞ DỮ LIỆU MYSQL
# ==============================================================================
MYSQL_CONFIG = {
    "host": os.getenv("CRAWLER_DB_HOST") or os.getenv("MYSQL_HOST") or "127.0.0.1",
    "user": os.getenv("CRAWLER_DB_USER") or os.getenv("MYSQL_USER") or "root",
    "password": os.getenv("CRAWLER_DB_PASSWORD") or os.getenv("MYSQL_PASSWORD") or "Xloc3805no!",
    "database": os.getenv("CRAWLER_DB_NAME") or os.getenv("MYSQL_DATABASE") or "skill_intelligence",
    "port": int(os.getenv("CRAWLER_DB_PORT") or os.getenv("MYSQL_PORT") or 3306),
    "charset": "utf8mb4",
    "autocommit": True
}

# Tên bảng lưu dữ liệu tuyển dụng thô
TABLE_NAME = "jobs_raw"

# ==============================================================================
# 2. CẤU HÌNH 4 NHÓM NGÀNH CẦN THU THẬP
# ==============================================================================
# Gồm mã category_family trên TopCV và tên chuẩn hóa để lưu vào cột category
CATEGORIES = {
    "r257": {
        "name": "Công nghệ Thông tin",
        "code": "r257",
        "category_db": "Công nghệ Thông tin"
    },
    "r857": {
        "name": "Nhà hàng/Khách sạn/Du lịch",
        "code": "r857",
        "category_db": "Du lịch-Dịch vụ"
    },
    "r711": {
        "name": "Logistics/Thu mua/Kho vận",
        "code": "r711",
        "category_db": "Logistics"
    },
    "r392": {
        "name": "Kế toán/Kiểm toán/Thuế",
        "code": "r392",
        "category_db": "Kế toán"
    }
}

# ==============================================================================
# 3. CẤU HÌNH KHU VỰC VÀ ĐƯỜNG DẪN URL
# ==============================================================================
# Khu vực: l8 = Đà Nẵng (bao gồm Quảng Nam), l61 = Thừa Thiên Huế, l52 = Quảng Ngãi
LOCATIONS = "l8_l61_l52"

# Trang chủ TopCV để khởi tạo phiên & cookies an toàn
BASE_URL = "https://www.topcv.vn"

# Cấu trúc URL trang danh sách (Listing page)
SEARCH_URL_TEMPLATE = (
    "https://www.topcv.vn/tim-viec-lam-moi-nhat"
    "?category_family={category_code}&locations={locations}&page={page}&type_keyword=1&sba=1"
)

# ==============================================================================
# 4. THÔNG SỐ CHỐNG CHẶN VÀ RATE LIMIT TỐI ƯU
# ==============================================================================
# Thời gian chờ vừa phải (0.8s - 1.5s) giúp tốc độ vừa nhanh vừa không kích hoạt 429 WAF của TopCV
MIN_DELAY_SECONDS = 0.8
MAX_DELAY_SECONDS = 1.5

# Số luồng song song an toàn (3 luồng kết hợp delay ~2-3 request/giây đạt hiệu quả cao nhất)
MAX_WORKERS = 3

# Thời gian chờ phản hồi tối đa cho mỗi request (giây)
REQUEST_TIMEOUT = 25

# Số lần thử lại tối đa khi gặp gián đoạn hoặc 429 cooldown
MAX_RETRIES = 5

# Giả lập HTTP Headers của trình duyệt Chrome thật
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.topcv.vn/",
    "Upgrade-Insecure-Requests": "1"
}

# Cấu hình mục tiêu thu thập: 250 bài job mỗi ngành -> Tổng 1,000 bài job
TARGET_JOBS_PER_CATEGORY = 250
MAX_PAGES_PER_CATEGORY = None

# ==============================================================================
# 5. CẤU HÌNH GROQ API & EMBEDDING CHO SKILL EXTRACTION
# ==============================================================================
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = "qwen/qwen3.8-27b"

# Mô hình embedding đa ngôn ngữ để so khớp ngữ nghĩa Việt - Anh (ESCO)
EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

# Ngưỡng cosine similarity tối thiểu để coi là khớp với skill ESCO (0.0 -> 1.0)
# Nếu >= SIMILARITY_THRESHOLD: Khớp với ESCO (chuẩn hóa theo ESCO)
# Nếu < SIMILARITY_THRESHOLD: Giữ nguyên skill tiếng Việt đặc thù -> lưu vào taxonomy & MySQL
SIMILARITY_THRESHOLD = 0.75

# Giới hạn tần suất xử lý qua Groq API (100 request/phút theo yêu cầu)
GROQ_RPM = 100
GROQ_MAX_WORKERS = 4

