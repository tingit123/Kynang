"""
evaluate_gold_standard.py
=============================================================================
Đánh giá độ chính xác của Pipeline Trích xuất Kỹ năng (Skill Extraction)
so với Bộ dữ liệu Chuẩn (Gold Standard):
  - 80 JD trong gold_jd_raw..csv (đối chiếu với gold_annotation_CLEAN.xlsx)
  - 40 CV trong gold_cv_raw.csv (đối chiếu với gold_cv_annotation_DRAFT.xlsx)

Các chỉ số đánh giá:
  - Precision, Recall, F1 toàn bộ
  - Precision, Recall, F1 theo từng skill_type (HARD, SOFT, TOOL, KNOWLEDGE, CERTIFICATION, LANGUAGE)
  - Phân tách độc lập cho JD và CV
  - Phân tích lỗi (Error Analysis: FP, FN, Type mismatch)

Xuất kết quả:
  - In báo cáo console
  - Lưu vào:
      gold_standard/evaluation/metrics_overall.json
      gold_standard/evaluation/metrics_by_skill_type.json
      gold_standard/evaluation/metrics_jd_vs_cv.json
      gold_standard/evaluation/error_analysis.md
=============================================================================
"""

import os
import sys
import re
import csv
import json
import time
import threading
import openpyxl
import concurrent.futures
from difflib import SequenceMatcher
from typing import Dict, List, Any, Set, Tuple, Optional

import groq
import config

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA1_DIR = os.path.join(BASE_DIR, "data1")
EVAL_DIR = os.path.join(BASE_DIR, "gold_standard", "evaluation")
CACHE_DIR = os.path.join(BASE_DIR, "gold_standard", "cache")

os.makedirs(EVAL_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

JD_CACHE_FILE = os.path.join(CACHE_DIR, "machine_jd_extractions.json")
CV_CACHE_FILE = os.path.join(CACHE_DIR, "machine_cv_extractions.json")

# =============================================================================
# 1. TỪ ĐIỂN VÀ QUY TẮC CHUẨN HÓA / ĐỐI SÁNH (MATCHING LOGIC)
# =============================================================================

SYNONYM_MAP = {
    # Cơ sở dữ liệu & Công nghệ
    "postgres sql": "postgresql",
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "ms sql": "sql server",
    "mssql": "sql server",
    "sql server": "sql server",
    "ms sql server": "sql server",
    "reactjs": "react",
    "react.js": "react",
    "react": "react",
    "nodejs": "node.js",
    "node.js": "node.js",
    "node js": "node.js",
    "vuejs": "vue.js",
    "vue.js": "vue.js",
    "angularjs": "angular",
    "c#": "c#",
    "c sharp": "c#",
    "dotnet": ".net",
    ".net core": ".net",
    "asp.net": ".net",
    "golang": "go",
    "restful api": "rest api",
    "restful apis": "rest api",
    "rest api": "rest api",
    "rest apis": "rest api",
    "ci/cd": "cicd",
    "ci cd": "cicd",
    "microsoft excel": "excel",
    "ms excel": "excel",
    "microsoft office": "ms office",
    "msoffice": "ms office",
    "power point": "powerpoint",
    "ms powerpoint": "powerpoint",
    "3dmax": "3ds max",
    "3ds max": "3ds max",
    "3dsmax": "3ds max",
    "photoshop": "adobe photoshop",
    "adobe photoshop": "adobe photoshop",
    "illustrator": "adobe illustrator",
    "adobe illustrator": "adobe illustrator",
    
    # Kiểm thử
    "kiểm thử": "kiểm thử",
    "kiểm thử uat": "kiểm thử",
    "uat testing": "kiểm thử",
    "uat": "kiểm thử",
    "kiểm thử phần mềm": "kiểm thử",
    "software testing": "kiểm thử",
    "manual test": "kiểm thử",
    "manual testing": "kiểm thử",
    "kiểm thử thủ công": "kiểm thử",
    "automation test": "kiểm thử",
    "automation testing": "kiểm thử",
    "web/app testing": "kiểm thử",
    "kiểm thử web/app/api": "kiểm thử",
    "functional testing": "kiểm thử",
    "security testing": "kiểm thử",
    "load testing": "kiểm thử",
    "performance testing": "kiểm thử",
    "backend testing": "kiểm thử",
    "context driven testing": "kiểm thử",
    "test sql": "sql",
    "tester": "kiểm thử",
    "qa/qc": "kiểm thử",
    "qa engineer": "kiểm thử",

    # Soft skills (10 nhóm hạt nhân)
    "kỹ năng giao tiếp": "kỹ năng giao tiếp",
    "giao tiếp": "kỹ năng giao tiếp",
    "communication": "kỹ năng giao tiếp",
    "communication skills": "kỹ năng giao tiếp",
    "làm việc nhóm": "làm việc nhóm",
    "kỹ năng làm việc nhóm": "làm việc nhóm",
    "teamwork": "làm việc nhóm",
    "collaboration": "làm việc nhóm",
    "đàm phán & thuyết phục": "đàm phán & thuyết phục",
    "đàm phán": "đàm phán & thuyết phục",
    "thuyết phục": "đàm phán & thuyết phục",
    "negotiation": "đàm phán & thuyết phục",
    "chăm sóc khách hàng": "chăm sóc khách hàng",
    "customer service": "chăm sóc khách hàng",
    "kỹ năng lãnh đạo": "kỹ năng lãnh đạo",
    "lãnh đạo": "kỹ năng lãnh đạo",
    "leadership": "kỹ năng lãnh đạo",
    "quản lý nhóm": "kỹ năng lãnh đạo",
    "quản lý thời gian": "quản lý thời gian",
    "time management": "quản lý thời gian",
    "giải quyết vấn đề": "giải quyết vấn đề",
    "xử lý vấn đề": "giải quyết vấn đề",
    "problem solving": "giải quyết vấn đề",
    "problem-solving": "giải quyết vấn đề",
    "xử lý sự cố": "giải quyết vấn đề",
    "khắc phục sự cố": "giải quyết vấn đề",
    "tư duy logic & phản biện": "tư duy logic & phản biện",
    "tư duy phản biện & logic": "tư duy logic & phản biện",
    "tư duy logic": "tư duy logic & phản biện",
    "tư duy phản biện": "tư duy logic & phản biện",
    "critical thinking": "tư duy logic & phản biện",
    "chủ động & trách nhiệm": "chủ động & trách nhiệm",
    "chủ động": "chủ động & trách nhiệm",
    "trách nhiệm": "chủ động & trách nhiệm",
    "tinh thần trách nhiệm": "chủ động & trách nhiệm",
    "chịu áp lực công việc": "chịu áp lực công việc",
    "chịu áp lực": "chịu áp lực công việc",
    "work under pressure": "chịu áp lực công việc",
    
    # Ngoại ngữ
    "tiếng anh": "tiếng anh",
    "english": "tiếng anh",
    "english proficiency": "tiếng anh",
    "tiếng anh giao tiếp": "tiếng anh",
    "tiếng anh thương mại": "tiếng anh thương mại",
    "business english": "tiếng anh thương mại",
    "tiếng nhật": "tiếng nhật",
    "japanese": "tiếng nhật",
    "tiếng hàn": "tiếng hàn",
    "korean": "tiếng hàn",
    "tiếng trung": "tiếng trung",
    "chinese": "tiếng trung",
    
    # Bổ sung so khớp mở rộng
    "giao tiếp tốt": "giao tiếp",
    "tư duy hệ thống": "tư duy logic",
    "negotiations expert": "đàm phán & thuyết phục",
    "leadership/communication skills": "lãnh đạo",
}

# =============================================================================
# QUY TẮC BỔ SUNG: CANONICAL, STOP-LIST & PHÂN ĐỊNH HARD VS TOOL
# =============================================================================

# Soft skill chỉ giữ nếu map được về 10 nhóm hạt nhân
SOFT_CANONICAL = {
    # 1. Giao tiếp
    "giao tiếp": "Kỹ năng giao tiếp",
    "kỹ năng giao tiếp": "Kỹ năng giao tiếp",
    "giao tiếp tốt": "Kỹ năng giao tiếp",
    "communication": "Kỹ năng giao tiếp",
    "communication skills": "Kỹ năng giao tiếp",
    
    # 2. Làm việc nhóm
    "làm việc nhóm": "Làm việc nhóm",
    "kỹ năng làm việc nhóm": "Làm việc nhóm",
    "teamwork": "Làm việc nhóm",
    "team player": "Làm việc nhóm",
    "collaboration": "Làm việc nhóm",
    
    # 3. Đàm phán & Thuyết phục
    "đàm phán": "Đàm phán & Thuyết phục",
    "thuyết phục": "Đàm phán & Thuyết phục",
    "negotiation": "Đàm phán & Thuyết phục",
    "negotiations expert": "Đàm phán & Thuyết phục",
    "đàm phán & thuyết phục": "Đàm phán & Thuyết phục",
    
    # 4. Chăm sóc khách hàng
    "chăm sóc khách hàng": "Chăm sóc khách hàng",
    "customer service": "Chăm sóc khách hàng",
    "hỗ trợ khách hàng": "Chăm sóc khách hàng",
    
    # 5. Kỹ năng lãnh đạo
    "lãnh đạo": "Kỹ năng lãnh đạo",
    "kỹ năng lãnh đạo": "Kỹ năng lãnh đạo",
    "leadership": "Kỹ năng lãnh đạo",
    "quản lý nhóm": "Kỹ năng lãnh đạo",
    "leadership/communication skills": "Kỹ năng lãnh đạo",
    
    # 6. Quản lý thời gian
    "quản lý thời gian": "Quản lý thời gian",
    "time management": "Quản lý thời gian",
    "manage time": "Quản lý thời gian",
    "multi-tasking": "Quản lý thời gian",
    
    # 7. Giải quyết vấn đề
    "giải quyết vấn đề": "Giải quyết vấn đề",
    "problem-solving": "Giải quyết vấn đề",
    "problem solving": "Giải quyết vấn đề",
    "xử lý vấn đề": "Giải quyết vấn đề",
    
    # 8. Tư duy logic & Phản biện
    "tư duy logic": "Tư duy logic & Phản biện",
    "tư duy phản biện": "Tư duy logic & Phản biện",
    "critical thinking": "Tư duy logic & Phản biện",
    "tư duy hệ thống": "Tư duy logic & Phản biện",
    "tư duy logic & phản biện": "Tư duy logic & Phản biện",
    
    # 9. Chủ động & Trách nhiệm
    "chủ động": "Chủ động & Trách nhiệm",
    "trách nhiệm": "Chủ động & Trách nhiệm",
    "tinh thần trách nhiệm": "Chủ động & Trách nhiệm",
    "proactive": "Chủ động & Trách nhiệm",
    "chủ động & trách nhiệm": "Chủ động & Trách nhiệm",
    
    # 10. Chịu áp lực công việc
    "chịu áp lực": "Chịu áp lực công việc",
    "chịu áp lực công việc": "Chịu áp lực công việc",
    "work under pressure": "Chịu áp lực công việc",
    "tolerate stress": "Chịu áp lực công việc",
}

# Danh sách stop-skills loại bỏ triệt để: tính cách thuần, nhiệm vụ chung, phân hệ/ngành rác
STOP_SKILLS = {
    # Tính cách / phẩm chất thuần túy
    "nhiệt tình", "chăm chỉ", "trung thực", "nhanh nhẹn", "tự tin",
    "hòa đồng", "kiên nhẫn", "thật thà", "năng động", "cầu tiến",
    "cẩn thận", "tỉ mỉ", "chu đáo", "hoạt bát", "chịu khó",
    "ham học hỏi", "tinh thần học hỏi cao", "thân thiện", "linh hoạt", "khéo léo",
    "tận tâm", "nhiệt huyết", "đam mê", "gọn gàng", "sạch sẽ", "ngăn nắp",
    "sáng tạo", "chính xác",

    # Nhiệm vụ / hoạt động công việc chung chung
    "viết tài liệu", "hỗ trợ người dùng", "đào tạo người dùng", "chẩn đoán", "xử lý sự cố",
    "phối hợp", "quản lý quy trình nghiệp vụ", "báo cáo công việc", "lập báo cáo", "làm báo cáo",
    "nhập liệu", "soạn thảo văn bản", "trực điện thoại", "hỗ trợ kỹ thuật",
    "bảo trì hệ thống", "quản trị hệ thống", "vận hành thiết bị",
    "giám sát", "reconciliation", "budgeting", "change management",
    "enterprise platforms", "performance criteria tracking",
    "operations management", "quản lý vận hành",

    # Kỹ năng / cụm từ quá hẹp hoặc chung chung theo chỉ đạo
    "phát hiện đối tượng", "phân loại hình ảnh", "object detection", "image classification",
    "phân tích", "analysis",
    "handmade",
    "quality assessment", "quality improvement", "đánh giá chất lượng", "cải tiến chất lượng",
    "software testing methodology", "phương pháp kiểm thử phần mềm", "quy trình kiểm thử phần mềm",
    "đọc hiểu tài liệu kỹ thuật bằng tiếng anh",

    # Phân hệ / ngành / lĩnh vực rác (không phải skill độc lập)
    "pos", "bán hàng", "kho", "tin học văn phòng", "tin học văn phòng cơ bản",
    "it - phần mềm", "it-phần mềm", "ngành it", "phần mềm",
    "tài chính", "kế toán", "kiểm toán", "thuế", "xây dựng",
    "logistic / vận tải", "logistics / vận tải", "logistic", "logistics", "vận tải",
    "du lịch", "dịch vụ", "nghiệp vụ kế toán", "kiến thức kế toán", "kiến thức ngành",
    "ngành nghề", "lĩnh vực", "kiến thức ngành logistic / vận tải", "kiến thức ngành it - phần mềm",
    "kiến thức tạo hình sản phẩm bằng giấy, papercraft, kirigami",
    "kiến thức tạo hình sản phẩm bằng giấy (papercraft, kirigami)",
    "banking domain", "core banking business processes", "retail banking", "corporate banking",
    "công nghệ thông tin và ngân hàng", "nghề nghiệp ngân hàng", "banking, fintech, payment domain", "lending",
    "marketing / quảng cáo", "kiến thức về thị trường game", "kiến thức về erp",
    "hiểu biết về quy trình kế toán", "kiến thức nền về kế toán, quản trị doanh nghiệp hoặc hệ thống erp",
    "các loại kỹ thuật kiểm thử, loại kiểm thử, quy trình kiểm thử",
    "core banking implementation", "core banking integration", "core banking enhancement",
    "core banking support", "product configuration", "solution architecture", "pre-sales activities",
    "banking solutions design", "banking solutions implementation", "functional consulting",
    "technical consulting", "core banking migration", "hiểu biết về khối chính phủ",
    "southeast asian banking projects", "banking transformation", "saas business metrics understanding",
    "churn rate", "mrr/arr", "ltv", "cac", "net revenue retention (nrr)", "dunning management"
}

# Chức danh công việc / vị trí (KHÔNG giữ làm kỹ năng, chuyển sang Position)
POSITIONS_AS_SKILLS = {
    "business analyst", "tester", "qa/qc", "qa qc", "qa engineer", "qc engineer",
    "data engineer", "manual tester", "automation tester", "kế toán trưởng",
    "kế toán viên", "developer", "lập trình viên", "software engineer",
    "frontend developer", "backend developer", "fullstack developer", "system admin",
    "product owner", "scrum master", "trưởng nhóm", "trưởng phòng", "giám đốc",
    "nhân viên", "chuyên viên", "thực tập sinh", "fresher", "intern"
}

# Ép kiểu TOOL (phần mềm, nền tảng, công cụ, hệ quản trị CSDL)
FORCE_TOOL = {
    "excel", "misa", "sap", "erp", "docker", "jira", "git", "github", "gitlab",
    "confluence", "postman", "jmeter", "loadrunner", "mysql", "postgresql", "mongodb", "oracle",
    "linux", "unix", "windows", "aws", "azure", "gcp", "sharepoint", "onedrive",
    "power apps", "power automate", "tensorflow", "pytorch", "opencv",
    "scikit-learn", "microsoft office", "fast", "bravo", "smartpro",
    "figma", "canva", "power bi", "powerbi", "k8s", "kubernetes", "redis",
    "visual studio", "vs code", "eclipse", "intellij", "word", "powerpoint", "3ds max"
}

# Ép kiểu HARD (kỹ năng chuyên môn, ngôn ngữ lập trình, nghiệp vụ)
FORCE_HARD = {
    "python", "java", "c#", "c++", "golang", "go", "javascript", "typescript",
    "php", "ruby", "rust", "sql", "computer vision", "machine learning", "deep learning",
    "kiểm thử", "testing", "data analysis", "data analytics", "etl/elt", "etl", "elt",
    "kế toán tổng hợp", "kế toán thuế", "kế toán kho", "quản lý kho", "xuất nhập khẩu",
    "incoterms", "thủ tục hải quan", "khai hải quan", "báo cáo tài chính", "lập báo cáo tài chính",
    "kế toán công nợ", "html/css"
}

# Chuẩn hóa tên chuẩn (Canonical mapping)
NAME_CANONICAL = {
    "postgres sql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "ms sql": "MS SQL",
    "mssql": "MS SQL",
    "ms sql server": "SQL Server",
    "sql server": "SQL Server",
    "english proficiency": "Tiếng Anh",
    "english": "Tiếng Anh",
    "tiếng anh giao tiếp": "Tiếng Anh",
    "problem-solving": "Giải quyết vấn đề",
    "problem solving": "Giải quyết vấn đề",
    "problem-solving skills": "Giải quyết vấn đề",
    "xử lý vấn đề": "Giải quyết vấn đề",
    "analytical skills": "Tư duy logic & Phản biện",
    "manual test": "Kiểm thử",
    "manual testing": "Kiểm thử",
    "kiểm thử thủ công": "Kiểm thử",
    "automation test": "Kiểm thử tự động",
    "automation testing": "Kiểm thử tự động",
    "test sql": "SQL",
    "uat testing": "Kiểm thử",
    "kiểm thử uat": "Kiểm thử",
    "uat": "Kiểm thử",
    "kiểm thử phần mềm": "Kiểm thử",
    "software testing": "Kiểm thử",
    "web/app testing": "Kiểm thử",
    "kiểm thử web/app/api": "Kiểm thử",
    "functional testing": "Kiểm thử",
    "security testing": "Kiểm thử",
    "load testing": "Kiểm thử",
    "performance testing": "Kiểm thử",
    "backend testing": "Kiểm thử",
    "context driven testing": "Kiểm thử",
    "loadrunner": "LoadRunner",
    "jmeter": "JMeter",
    "postman": "Postman",
    "ai": "Adobe Illustrator",
    "pts": "Adobe Photoshop",
    "scikit-learn": "Scikit-learn",
    "toeic": "TOEIC",
    "restful api": "RESTful API",
    "rest api": "RESTful API",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "power point": "PowerPoint",
    "powerpoint": "PowerPoint",
    "ms office": "Microsoft Office",
    "msoffice": "Microsoft Office",
    "3dmax": "3ds Max",
    "3ds max": "3ds Max",
    "photoshop": "Adobe Photoshop",
    "adobe photoshop": "Adobe Photoshop",
    "illustrator": "Adobe Illustrator",
    "adobe illustrator": "Adobe Illustrator",
    "financial reporting": "Lập báo cáo tài chính",
    "báo cáo tài chính": "Lập báo cáo tài chính",
    "accounts receivable": "Kế toán công nợ",
    "customer service": "Chăm sóc khách hàng",
    "inventory management": "Quản lý kho",
    "data analytics": "Data Analysis",
    "data analytics pipelines": "ETL/ELT",
    "data analysis tools": "Data Analysis",
    "etl": "ETL/ELT",
    "elt": "ETL/ELT",
    "html": "HTML/CSS",
    "css": "HTML/CSS"
}

ALLOWED_SKILLS_FILE = os.path.join(BASE_DIR, "allowed_skills.json")
ALLOWED_SKILLS = {}
WHITELIST_LOOKUP = {}
SOFT_LOOKUP = {}

STOP_SOFT_SKILLS = {
    "cẩn thận", "cẩn thận tỉ mỉ", "tỉ mỉ", "attend to detail", "detail-oriented",
    "chú ý đến chi tiết và độ chính xác", "chính xác", "chính xác tỉ mỉ chi tiết",
    "trung thực và trách nhiệm", "trung thực chịu áp lực và tinh thần trách nhiệm cao",
    "thật thà", "kỷ luật trung thực chăm chỉ", "chăm chỉ", "thái độ làm việc chăm chỉ",
    "thái độ làm việc tốt", "nhiệt tình với công việc", "professionalism", "tác phong chuyên nghiệp",
    "tác phong nhanh nhẹn", "nhanh nhẹn cẩn thận tỉ mỉ", "thái độ tích cực", "ý thức tiết kiệm",
    "ý thức sạch sẽ vệ sinh tốt", "work efficiently", "thân thiện", "vui vẻ", "diligence",
    "gắn bó lâu dài", "gắn bó công việc ổn định lâu dài", "định hướng lâu dài",
    "định hướng làm nghề bếp lâu dài", "nhận việc ngay", "sẵn sàng đi công tác",
    "sẵn sàng đi công tác nước ngoài", "khả năng đi công tác làm đêm", "làm việc theo ca",
    "sẵn sàng làm việc theo ca", "sẵn sàng làm việc ca xoay", "làm việc xoay ca",
    "làm việc ca đêm", "chịu áp lực công việc ca đêm", "làm việc ca gãy", "sức khỏe tốt",
    "thể chất tốt", "ngoại hình ưa nhìn", "đã lập gia đình", "đam mê nấu ăn",
    "yêu thích công việc bếp", "maintain kitchen equipment at correct temperature",
    "characteristics of products", "sáng tạo", "think creatively", "develop creative ideas",
    "kỹ năng sáng tạo và chủ động", "tư duy thẩm mỹ", "màu sắc", "cảm thụ màu sắc",
    "staf", "design process", "business analyst", "tester", "manual tester", "qa/qc",
    "data engineer", "kế toán trưởng"
}

if os.path.exists(ALLOWED_SKILLS_FILE):
    try:
        with open(ALLOWED_SKILLS_FILE, "r", encoding="utf-8") as f:
            ALLOWED_SKILLS = json.load(f)
        for canon, data in ALLOWED_SKILLS.items():
            stype = data.get("skill_type", "HARD")
            WHITELIST_LOOKUP[canon.lower()] = (canon, stype)
            if stype == "SOFT":
                SOFT_LOOKUP[canon.lower()] = canon
            for a in data.get("aliases", []):
                WHITELIST_LOOKUP[a.lower()] = (canon, stype)
                if stype == "SOFT":
                    SOFT_LOOKUP[a.lower()] = canon
    except Exception as e:
        print(f"Lỗi nạp allowed_skills.json: {e}")

MATCH_PREFIXES = [
    "kỹ năng ", "khả năng ", "kinh nghiệm ", "thành thạo ", "hiểu biết về ",
    "kiến thức về ", "sử dụng ", "làm việc với ", "kinh nghiệm về "
]

def soft_collapse(skill_name: str) -> Optional[str]:
    """
    Chuẩn hóa toàn bộ kỹ năng mềm về đúng 1 trong 10 nhóm hạt nhân (Canonical Name).
    Nếu thuộc danh sách STOP hoặc không thuộc 10 nhóm -> trả về None (DROP).
    """
    if not skill_name:
        return None
    raw = skill_name.strip()
    low = raw.lower()
    low = re.sub(r'[\r\n\t]+', ' ', low)
    low = re.sub(r'\s+', ' ', low).strip('.,;:\'"-_`()[]{}')

    if not low:
        return None

    # 1. Bỏ qua nếu thuộc danh sách STOP soft skills
    if low in STOP_SOFT_SKILLS:
        return None

    # 2. Match trực tiếp trong 10 nhóm hạt nhân
    if low in SOFT_LOOKUP:
        return SOFT_LOOKUP[low]

    # 3. Match sau khi lược bỏ prefix
    for p in MATCH_PREFIXES:
        if low.startswith(p):
            sub = low[len(p):].strip()
            if sub in SOFT_LOOKUP:
                return SOFT_LOOKUP[sub]

    # 4. Soft rule: chủ động & trách nhiệm
    if ("chủ động" in low or "trách nhiệm" in low or "proactive" in low or "responsibility" in low) and low not in STOP_SOFT_SKILLS:
        return "Chủ động & Trách nhiệm"

    return None

def match_skill_to_whitelist(skill_name: str):
    """Ánh xạ tên kỹ năng đề xuất sang (canonical_name, skill_type) trong whitelist taxonomy."""
    if not skill_name or not WHITELIST_LOOKUP:
        return None
    raw = skill_name.strip()
    low = raw.lower()
    low = re.sub(r'[\r\n\t]+', ' ', low)
    low = re.sub(r'\s+', ' ', low).strip('.,;:\'"-_`()[]{}')

    if not low:
        return None

    # Ưu tiên kiểm tra soft_collapse
    soft_res = soft_collapse(raw)
    if soft_res:
        return (soft_res, "SOFT")

    # Match trực tiếp qua alias / canonical
    if low in WHITELIST_LOOKUP:
        return WHITELIST_LOOKUP[low]

    # Match sau khi lược bỏ prefix phổ biến
    for p in MATCH_PREFIXES:
        if low.startswith(p):
            sub = low[len(p):].strip()
            if sub in WHITELIST_LOOKUP:
                return WHITELIST_LOOKUP[sub]

    return None

def clean_skills(skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Hậu xử lý chuẩn hóa và kiểm duyệt qua whitelist taxonomy:
    1. Lọc bỏ Stop-skills và chức danh vị trí công việc.
    2. Nếu là kỹ năng mềm (hoặc có nhãn SOFT): bắt buộc gom về 10 nhóm hạt nhân qua soft_collapse.
       Nếu không thuộc 10 nhóm -> DROP.
    3. Nếu là HARD/TOOL/KNOWLEDGE/CERTIFICATION/LANGUAGE: ánh xạ qua Whitelist Taxonomy.
       Nếu không thuộc Whitelist -> DROP.
    4. Khử trùng lặp theo (skill_canonical.lower(), skill_type).
    """
    cleaned = []
    seen = set()

    for s in skills:
        if not s.get("skill_name"):
            continue
        raw = s["skill_name"].strip()
        key = raw.lower()
        stype = (s.get("skill_type") or "").upper()

        # 1. Bỏ qua nếu thuộc STOP_SKILLS hoặc chức danh công việc hoặc STOP_SOFT_SKILLS
        if key in STOP_SKILLS or key in POSITIONS_AS_SKILLS or key in STOP_SOFT_SKILLS:
            continue

        # 2. Xử lý SOFT skill: chỉ cho phép 10 nhóm canonical
        soft_canon = soft_collapse(raw)
        if soft_canon:
            canon_name = soft_canon
            final_stype = "SOFT"
        elif stype == "SOFT":
            # Là soft skill mà không map được vào 10 nhóm hạt nhân -> DROP
            continue
        else:
            # 3. Xử lý các loại kỹ năng khác qua Whitelist Taxonomy
            res = match_skill_to_whitelist(raw)
            if not res:
                # Kỹ năng nằm ngoài taxonomy -> DROP
                continue
            canon_name, final_stype = res
            if final_stype == "SOFT":
                soft_canon = soft_collapse(canon_name)
                if not soft_canon:
                    continue
                canon_name = soft_canon

        # 4. Khử trùng lặp theo (canon_name.lower(), final_stype)
        dedupe_key = (canon_name.lower(), final_stype)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)

        out = dict(s)
        out["skill_name"] = canon_name
        out["skill_type"] = final_stype
        cleaned.append(out)

    return cleaned

# =============================================================================
# KEYWORD BOOST (HARD & TOOL) - Bổ sung nếu LLM bỏ sót
# =============================================================================

GENERIC_TOOL_EXCLUDE = {
    'phần mềm kế toán', 'word', 'microsoft office', 'powerpoint',
    'thành thạo tin học văn phòng', 'laptop cá nhân', 'laptop', 'tmđt',
    'tin học văn phòng', 'tin học văn phòng cơ bản', 'điện thoại', 'xe máy',
    'crm', 'wms', 'dms', 'tài liệu', 'công việc'
}

CORE_HARD_BOOST = {
    'kiểm thử', 'etl/elt', 'phân tích yêu cầu', 'phân tích nghiệp vụ',
    'python', 'java', 'c#', 'c++', 'javascript', 'typescript', 'php', 'sql',
    'computer vision', 'machine learning', 'deep learning', 'agile/scrum', 'sdlc',
    'hạch toán', 'kế toán thuế', 'kế toán tổng hợp', 'kế toán nội bộ', 'quyết toán thuế',
    'game design', 'game balancing', 'gameplay'
}

CASE_SENSITIVE_ALIASES = {'ba', 'pm', 'net', 'sms', 'ems', 'dms', 'ecs', 'wms', 'ota'}

BOOST_RULES = []
if ALLOWED_SKILLS:
    for canon, data in ALLOWED_SKILLS.items():
        stype = data.get('skill_type', '')
        canon_low = canon.lower().strip()
        
        if canon_low in GENERIC_TOOL_EXCLUDE or canon_low in STOP_SKILLS:
            continue

        if stype == 'TOOL':
            pass
        elif stype == 'HARD' and canon_low in CORE_HARD_BOOST:
            pass
        else:
            continue
        
        terms = [canon] + data.get('aliases', [])
        for t in terms:
            t_clean = t.strip()
            t_low = t_clean.lower()
            if len(t_low) <= 1 or t_low in ('c', 'r') or t_low in GENERIC_TOOL_EXCLUDE or t_low in STOP_SKILLS:
                continue
            
            is_case_sens = (t_low in CASE_SENSITIVE_ALIASES)
            escaped = re.escape(t_clean)
            if t_low == 'c#':
                pattern = re.compile(r'(?:^|[\s,;:(])c#(?:$|[\s,;:).])', re.IGNORECASE)
            elif t_low == 'c++':
                pattern = re.compile(r'(?:^|[\s,;:(])c\+\+(?:$|[\s,;:).])', re.IGNORECASE)
            elif is_case_sens:
                pattern = re.compile(r'\b' + re.escape(t_clean.upper()) + r'\b')
            else:
                pattern = re.compile(r'\b' + escaped + r'\b', re.IGNORECASE)
                
            BOOST_RULES.append({
                'canon': canon,
                'stype': stype,
                'term': t_clean,
                'pattern': pattern
            })

    BOOST_RULES.sort(key=lambda r: len(r['term']), reverse=True)

def boost_hard_tool_skills(text: str, current_skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Quét văn bản để bổ sung các kỹ năng HARD và TOOL nếu LLM bỏ sót.
    TUYỆT ĐỐI không boost kỹ năng mềm (SOFT).
    """
    if not text:
        return current_skills
    seen_canon = {s.get('skill_name', '').lower() for s in current_skills}
    boosted = list(current_skills)
    for r in BOOST_RULES:
        canon_low = r['canon'].lower()
        if canon_low in seen_canon:
            continue
        m = r['pattern'].search(text)
        if m:
            start = max(0, m.start() - 30)
            end = min(len(text), m.end() + 30)
            snippet = text[start:end].replace('\n', ' ').strip()
            boosted.append({
                'skill_name': r['canon'],
                'skill_type': r['stype'],
                'context_snippet': snippet,
                'requirement_level': 'mentioned'
            })
            seen_canon.add(canon_low)
    return boosted

def normalize_gold_for_eval(gold_skills: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Chuẩn hóa Gold Standard về cùng không gian tên:
    1. Lọc bỏ STOP_SKILLS, STOP_SOFT_SKILLS, POSITIONS_AS_SKILLS.
    2. Đối với SOFT: chỉ chấp nhận và chuẩn hóa về 1 trong 10 nhóm hạt nhân. Nếu là soft mà không map được hoặc thuộc stop -> DROP.
    3. Đối với các loại khác: match qua Whitelist nếu có, giữ nguyên nếu không.
    4. Dedupe theo (canon_name.lower(), stype).
    """
    norm = []
    seen = set()
    for s in gold_skills:
        raw = s.get("skill_name", "").strip()
        if not raw:
            continue
        low = raw.lower()
        stype = s.get("skill_type", "HARD").upper()

        # Bỏ qua nếu thuộc STOP
        if low in STOP_SKILLS or low in POSITIONS_AS_SKILLS or low in STOP_SOFT_SKILLS:
            continue

        # Xử lý SOFT
        soft_canon = soft_collapse(raw)
        if soft_canon:
            canon_name = soft_canon
            final_stype = "SOFT"
        elif stype == "SOFT":
            # Không map được vào 10 nhóm hạt nhân -> DROP
            continue
        else:
            res = match_skill_to_whitelist(raw)
            if res:
                canon_name, final_stype = res
            else:
                canon_name = raw
                final_stype = stype

        dedupe_key = (canon_name.lower(), final_stype)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)

        out = dict(s)
        out["skill_name"] = canon_name
        out["skill_type"] = final_stype
        norm.append(out)
    return norm

def clean_text(s: Any) -> str:
    """Chuẩn hóa cơ bản: chữ thường, bỏ khoảng trắng thừa và dấu câu bao quanh."""
    if s is None:
        return ""
    t = str(s).strip().lower()
    t = re.sub(r'[\r\n\t]+', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    t = t.strip('.,;:\'"-_`()[]{}')
    return t

def canonical_skill_name(s: str) -> str:
    """Chuẩn hóa ngữ nghĩa về từ chuẩn."""
    c = clean_text(s)
    if c in SYNONYM_MAP:
        return SYNONYM_MAP[c]
    for prefix in ["kỹ năng ", "khả năng ", "kinh nghiệm ", "thành thạo ", "hiểu biết về "]:
        if c.startswith(prefix):
            sub = c[len(prefix):].strip()
            if sub in SYNONYM_MAP:
                return SYNONYM_MAP[sub]
            return sub
    return c

def is_skill_match(machine_name: str, gold_name: str) -> bool:
    """
    Quy tắc so khớp kỹ năng (được tính là True Positive):
    1. Trùng khớp hoàn toàn sau khi chuẩn hóa chữ thường + bỏ khoảng trắng.
    2. Trùng khớp sau khi quy về từ chuẩn (canonical / synonym map).
    3. Soft matching nhẹ:
       - Substring khi độ dài chuỗi con đủ lớn (>= 4 ký tự) và mang nghĩa trọn vẹn.
       - Token overlap / SequenceMatcher ratio >= 0.85 (VD: 'PostgreSQL' ≈ 'Postgres SQL').
    """
    m_clean = clean_text(machine_name)
    g_clean = clean_text(gold_name)
    
    if not m_clean or not g_clean:
        return False
        
    # 1. Exact match
    if m_clean == g_clean:
        return True
        
    # 2. Canonical synonym match
    m_canon = canonical_skill_name(m_clean)
    g_canon = canonical_skill_name(g_clean)
    if m_canon == g_canon:
        return True
        
    # 3. Soft matching nhẹ
    m_tokens = set(m_canon.split())
    g_tokens = set(g_canon.split())
    if m_tokens == g_tokens:
        return True
        
    if len(m_tokens) >= 2 and len(g_tokens) >= 2:
        intersection = m_tokens.intersection(g_tokens)
        if len(intersection) / max(len(m_tokens), len(g_tokens)) >= 0.75:
            return True

    # Similarity ratio >= 0.85 (vd: postgresql vs postgres sql)
    ratio = SequenceMatcher(None, m_canon, g_canon).ratio()
    if ratio >= 0.85:
        return True
        
    # Kiểm tra không dấu cách (vd: "3dmax" vs "3ds max")
    m_nospace = m_canon.replace(" ", "")
    g_nospace = g_canon.replace(" ", "")
    if m_nospace == g_nospace and len(m_nospace) >= 3:
        return True
        
    return False

# =============================================================================
# 2. BỘ ĐIỀU KHIỂN GROQ EXTRACTOR
# =============================================================================

class EvaluationGroqExtractor:
    def __init__(self, api_key: str = config.GROQ_API_KEY):
        self.client = groq.Groq(api_key=api_key, timeout=30.0)
        # Chỉ dùng các model chat hiện hữu và hỗ trợ response_format json
        self.models = ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"]

    def extract_jd_skills(self, title: str, vi_tri: str, desc: str, req: str) -> List[Dict[str, Any]]:
        prompt = f"""Bạn là hệ thống trích xuất kỹ năng từ tin tuyển dụng (JD) hoặc CV tiếng Việt/Anh.
Chỉ trích kỹ năng CÓ RÕ trong văn bản. Không suy diễn, không bịa.

## Output
Trả về DUY NHẤT một JSON object có trường "skills" chứa array các kỹ năng. Mỗi phần tử:
{{
  "skill_name": "tên chuẩn",
  "skill_type": "HARD|SOFT|TOOL|LANGUAGE|CERTIFICATION|KNOWLEDGE",
  "context_snippet": "đoạn nguyên văn ngắn (≤120 ký tự) chứa skill",
  "requirement_level": "required|preferred|mentioned"
}}

Không markdown, không giải thích ngoài JSON.

## skill_type
- HARD: năng lực chuyên môn / nghiệp vụ (Python, Kiểm thử, Kế toán thuế, Phân tích yêu cầu, ETL/ELT, Hải quan…)
- TOOL: phần mềm, nền tảng, thư viện, hệ thống (Excel, MISA, Jira, ERP, Docker, Oracle, Linux, TensorFlow…)
- SOFT: CHỈ một trong 10 tên sau (nếu văn bản có ý tương đương thì gộp về đúng tên này):
  1. Kỹ năng giao tiếp
  2. Làm việc nhóm
  3. Đàm phán & Thuyết phục
  4. Chăm sóc khách hàng
  5. Kỹ năng lãnh đạo
  6. Quản lý thời gian
  7. Giải quyết vấn đề
  8. Tư duy logic & Phản biện
  9. Chủ động & Trách nhiệm
  10. Chịu áp lực công việc
- LANGUAGE: ngoại ngữ (Tiếng Anh, TOEIC, IELTS…)
- CERTIFICATION: chứng chỉ có tên rõ (AWS Certified, TOEIC 600…)
- KNOWLEDGE: chỉ khi là kiến thức chuyên biệt được nêu rõ; KHÔNG dùng cho “kiến thức ngành” chung

## Bắt buộc
1. skill_name ngắn, chuẩn hóa (PostgreSQL không phải Postgres SQL; Tiếng Anh không phải English proficiency).
2. Soft: “teamwork” / “phối hợp nhóm” → "Làm việc nhóm"; “chủ động, trách nhiệm” → "Chủ động & Trách nhiệm"; “problem-solving” → "Giải quyết vấn đề"; “analytical / tư duy logic” → "Tư duy logic & Phản biện".
3. “Kiểm thử” / UAT / manual testing / testing → HARD "Kiểm thử". “ETL/ELT” / etl / elt → HARD "ETL/ELT".
4. Ngôn ngữ lập trình, nghiệp vụ = HARD. Phần mềm / OS / DB product = TOOL (Excel, Jira, SAP, ERP, Docker = TOOL).
5. Mỗi skill một lần; kèm context_snippet nguyên văn từ bài.
6. requirement_level: required nếu “yêu cầu / cần / must / bắt buộc”; preferred nếu “ưu tiên / là lợi thế / plus”; còn lại mentioned.

## Cấm
- Chức danh / vị trí: Business Analyst, Tester, Developer, Kế toán trưởng, Nhân viên… (KHÔNG phải skill).
- Tính cách / thái độ: chăm chỉ, nhiệt tình, trung thực, nhanh nhẹn, hòa đồng, cẩn thận (thuần tính cách).
- Điều kiện: gắn bó lâu dài, đi công tác, làm ca, sức khỏe, ngoại hình, nhận việc ngay.
- Suy ra skill chỉ vì tên nghề. Không tách task con (không tách “phát hiện đối tượng” nếu chỉ nói Computer Vision).
- Cụm quá chung đứng một mình: “phân tích”, “tin học văn phòng”, “kiến thức ngành IT”.
- Skill không có căn cứ trong văn bản.

## Few-shot
Input: "Yêu cầu: Thành thạo Python, SQL; biết Docker; ưu tiên TOEIC 500; làm việc nhóm tốt; chủ động chịu trách nhiệm."
Output:
{{
  "skills": [
    {{"skill_name":"Python","skill_type":"HARD","context_snippet":"Thành thạo Python, SQL","requirement_level":"required"}},
    {{"skill_name":"SQL","skill_type":"HARD","context_snippet":"Thành thạo Python, SQL","requirement_level":"required"}},
    {{"skill_name":"Docker","skill_type":"TOOL","context_snippet":"biết Docker","requirement_level":"required"}},
    {{"skill_name":"TOEIC","skill_type":"CERTIFICATION","context_snippet":"ưu tiên TOEIC 500","requirement_level":"preferred"}},
    {{"skill_name":"Làm việc nhóm","skill_type":"SOFT","context_snippet":"làm việc nhóm tốt","requirement_level":"required"}},
    {{"skill_name":"Chủ động & Trách nhiệm","skill_type":"SOFT","context_snippet":"chủ động chịu trách nhiệm","requirement_level":"required"}}
  ]
}}

Input: "Phối hợp với Tester và BA; hỗ trợ kiểm thử UAT; kinh nghiệm Jira; problem-solving skills."
Output:
{{
  "skills": [
    {{"skill_name":"Kiểm thử","skill_type":"HARD","context_snippet":"hỗ trợ kiểm thử UAT","requirement_level":"mentioned"}},
    {{"skill_name":"Jira","skill_type":"TOOL","context_snippet":"kinh nghiệm Jira","requirement_level":"required"}},
    {{"skill_name":"Giải quyết vấn đề","skill_type":"SOFT","context_snippet":"problem-solving skills","requirement_level":"required"}}
  ]
}}

## Văn bản cần trích xuất (Tin tuyển dụng)
Tiêu đề: {title}
Vị trí: {vi_tri}
Mô tả công việc:
{desc[:3000]}
Yêu cầu ứng viên:
{req[:3000]}
"""
        return self._call_groq_json(prompt)

    def extract_cv_skills(self, category: str, cv_text: str) -> List[Dict[str, Any]]:
        prompt = f"""Bạn là hệ thống trích xuất kỹ năng từ tin tuyển dụng (JD) hoặc CV tiếng Việt/Anh.
Chỉ trích kỹ năng CÓ RÕ trong văn bản. Không suy diễn, không bịa.

## Output
Trả về DUY NHẤT một JSON object có trường "skills" chứa array các kỹ năng. Mỗi phần tử:
{{
  "skill_name": "tên chuẩn",
  "skill_type": "HARD|SOFT|TOOL|LANGUAGE|CERTIFICATION|KNOWLEDGE",
  "context_snippet": "đoạn nguyên văn ngắn (≤120 ký tự) chứa skill",
  "requirement_level": "required|preferred|mentioned"
}}

Không markdown, không giải thích ngoài JSON.

## skill_type
- HARD: năng lực chuyên môn / nghiệp vụ (Python, Kiểm thử, Kế toán thuế, Phân tích yêu cầu, ETL/ELT, Hải quan…)
- TOOL: phần mềm, nền tảng, thư viện, hệ thống (Excel, MISA, Jira, ERP, Docker, Oracle, Linux, TensorFlow…)
- SOFT: CHỈ một trong 10 tên sau (nếu văn bản có ý tương đương thì gộp về đúng tên này):
  1. Kỹ năng giao tiếp
  2. Làm việc nhóm
  3. Đàm phán & Thuyết phục
  4. Chăm sóc khách hàng
  5. Kỹ năng lãnh đạo
  6. Quản lý thời gian
  7. Giải quyết vấn đề
  8. Tư duy logic & Phản biện
  9. Chủ động & Trách nhiệm
  10. Chịu áp lực công việc
- LANGUAGE: ngoại ngữ (Tiếng Anh, TOEIC, IELTS…)
- CERTIFICATION: chứng chỉ có tên rõ (AWS Certified, TOEIC 600…)
- KNOWLEDGE: chỉ khi là kiến thức chuyên biệt được nêu rõ; KHÔNG dùng cho “kiến thức ngành” chung

## Bắt buộc
1. skill_name ngắn, chuẩn hóa (PostgreSQL không phải Postgres SQL; Tiếng Anh không phải English proficiency).
2. Soft: “teamwork” / “phối hợp nhóm” → "Làm việc nhóm"; “chủ động, trách nhiệm” → "Chủ động & Trách nhiệm"; “problem-solving” → "Giải quyết vấn đề"; “analytical / tư duy logic” → "Tư duy logic & Phản biện".
3. “Kiểm thử” / UAT / manual testing / testing → HARD "Kiểm thử". “ETL/ELT” / etl / elt → HARD "ETL/ELT".
4. Ngôn ngữ lập trình, nghiệp vụ = HARD. Phần mềm / OS / DB product = TOOL (Excel, Jira, SAP, ERP, Docker = TOOL).
5. Mỗi skill một lần; kèm context_snippet nguyên văn từ bài.
6. requirement_level: required nếu “yêu cầu / cần / must / bắt buộc”; preferred nếu “ưu tiên / là lợi thế / plus”; còn lại mentioned.

## Cấm
- Chức danh / vị trí: Business Analyst, Tester, Developer, Kế toán trưởng, Nhân viên… (KHÔNG phải skill).
- Tính cách / thái độ: chăm chỉ, nhiệt tình, trung thực, nhanh nhẹn, hòa đồng, cẩn thận (thuần tính cách).
- Điều kiện: gắn bó lâu dài, đi công tác, làm ca, sức khỏe, ngoại hình, nhận việc ngay.
- Suy ra skill chỉ vì tên nghề. Không tách task con (không tách “phát hiện đối tượng” nếu chỉ nói Computer Vision).
- Cụm quá chung đứng một mình: “phân tích”, “tin học văn phòng”, “kiến thức ngành IT”.
- Skill không có căn cứ trong văn bản.

## Few-shot
Input: "Yêu cầu: Thành thạo Python, SQL; biết Docker; ưu tiên TOEIC 500; làm việc nhóm tốt; chủ động chịu trách nhiệm."
Output:
{{
  "skills": [
    {{"skill_name":"Python","skill_type":"HARD","context_snippet":"Thành thạo Python, SQL","requirement_level":"required"}},
    {{"skill_name":"SQL","skill_type":"HARD","context_snippet":"Thành thạo Python, SQL","requirement_level":"required"}},
    {{"skill_name":"Docker","skill_type":"TOOL","context_snippet":"biết Docker","requirement_level":"required"}},
    {{"skill_name":"TOEIC","skill_type":"CERTIFICATION","context_snippet":"ưu tiên TOEIC 500","requirement_level":"preferred"}},
    {{"skill_name":"Làm việc nhóm","skill_type":"SOFT","context_snippet":"làm việc nhóm tốt","requirement_level":"required"}},
    {{"skill_name":"Chủ động & Trách nhiệm","skill_type":"SOFT","context_snippet":"chủ động chịu trách nhiệm","requirement_level":"required"}}
  ]
}}

Input: "Phối hợp với Tester và BA; hỗ trợ kiểm thử UAT; kinh nghiệm Jira; problem-solving skills."
Output:
{{
  "skills": [
    {{"skill_name":"Kiểm thử","skill_type":"HARD","context_snippet":"hỗ trợ kiểm thử UAT","requirement_level":"mentioned"}},
    {{"skill_name":"Jira","skill_type":"TOOL","context_snippet":"kinh nghiệm Jira","requirement_level":"required"}},
    {{"skill_name":"Giải quyết vấn đề","skill_type":"SOFT","context_snippet":"problem-solving skills","requirement_level":"required"}}
  ]
}}

## Văn bản cần trích xuất (CV ứng viên)
Ngành nghề: {category}
Nội dung CV:
{cv_text[:3500]}
"""
        return self._call_groq_json(prompt)


    def _call_groq_json(self, prompt: str) -> List[Dict[str, Any]]:
        for attempt in range(5):
            model_name = self.models[attempt % len(self.models)]
            try:
                resp = self.client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    temperature=0.1
                )
                content = resp.choices[0].message.content.strip()
                parsed = json.loads(content)
                if isinstance(parsed, list):
                    return parsed
                if isinstance(parsed, dict):
                    skills = parsed.get("skills")
                    if isinstance(skills, list):
                        return skills
                    for v in parsed.values():
                        if isinstance(v, list):
                            return v
            except Exception as e:
                err_str = str(e).lower()
                sleep_time = 4.0 if "429" in err_str else 2.0
                time.sleep(sleep_time)
        return []

# =============================================================================
# 3. NẠP DỮ LIỆU VÀ CHẠY PIPELINE
# =============================================================================

def load_gold_jds() -> Tuple[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]:
    """Đọc 80 JD gốc và 80 JD gán nhãn Gold Standard."""
    jd_raw_path = os.path.join(DATA1_DIR, "gold_jd_raw..csv")
    if not os.path.exists(jd_raw_path):
        jd_raw_path = os.path.join(DATA1_DIR, "gold_jd_raw.-2.csv")
    
    raw_jds = []
    with open(jd_raw_path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for r in reader:
            raw_jds.append({
                "job_id": str(r["job_id"]).strip(),
                "title": r.get("title", "").strip(),
                "category": r.get("category", "").strip(),
                "vi_tri": r.get("vi_tri", "").strip(),
                "description": r.get("description", "").strip(),
                "requirements": r.get("requirements", "").strip()
            })

    jd_gold_path = os.path.join(DATA1_DIR, "gold_annotation_CLEAN.xlsx")
    if not os.path.exists(jd_gold_path):
        jd_gold_path = os.path.join(DATA1_DIR, "gold_annotation_CLEAN-2.xlsx")
        
    wb = openpyxl.load_workbook(jd_gold_path, data_only=True)
    sheet = wb["Annotation"]
    
    # Khởi tạo đầy đủ cho tất cả 80 JD (kể cả JD có 0 kỹ năng)
    gold_by_job = {j["job_id"]: [] for j in raw_jds}
    
    for r in list(sheet.iter_rows(values_only=True))[1:]:
        if r[0] is None:
            continue
        jid = str(r[0]).strip()
        skill_name = str(r[2]).strip() if r[2] is not None else ""
        skill_type = str(r[3]).strip().upper() if r[3] is not None else "HARD"
        req_level = str(r[5]).strip().lower() if len(r) > 5 and r[5] is not None else "required"
        snippet = str(r[4]).strip() if len(r) > 4 and r[4] is not None else ""
        
        gold_by_job.setdefault(jid, [])
        if skill_name:
            gold_by_job[jid].append({
                "skill_name": skill_name,
                "skill_type": skill_type,
                "requirement_level": req_level,
                "context_snippet": snippet
            })
            
    return raw_jds, gold_by_job

def load_gold_cvs() -> Tuple[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]:
    """Đọc 40 CV gốc và 40 CV gán nhãn Gold Standard."""
    cv_gold_path = os.path.join(DATA1_DIR, "gold_cv_annotation_DRAFT.xlsx")
    if not os.path.exists(cv_gold_path):
        cv_gold_path = os.path.join(DATA1_DIR, "gold_cv_annotation_DRAFT-2.xlsx")
        
    wb = openpyxl.load_workbook(cv_gold_path, data_only=True)
    
    # 1. Đọc danh sách 40 CV thô từ sheet Raw_CV
    raw_cvs = []
    if "Raw_CV" in wb.sheetnames:
        sheet_raw = wb["Raw_CV"]
        for r in list(sheet_raw.iter_rows(values_only=True))[1:]:
            if r[0] is not None:
                raw_cvs.append({
                    "cv_id": str(r[0]).strip(),
                    "category": str(r[1]).strip() if r[1] else "",
                    "raw_text": str(r[2]).strip() if len(r) > 2 and r[2] else ""
                })
    else:
        cv_raw_path = os.path.join(DATA1_DIR, "gold_cv_raw.csv")
        with open(cv_raw_path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for r in reader:
                raw_cvs.append({
                    "cv_id": str(r["cv_id"]).strip(),
                    "category": r.get("category", "").strip(),
                    "raw_text": r.get("raw_text", "").strip()
                })

    # Khởi tạo đầy đủ cho tất cả 40 CV (kể cả CV có 0 kỹ năng)
    gold_by_cv = {c["cv_id"]: [] for c in raw_cvs}

    # 2. Đọc Annotation
    sheet_anno = wb["Annotation"]
    for r in list(sheet_anno.iter_rows(values_only=True))[1:]:
        if r[0] is None:
            continue
        cid = str(r[0]).strip()
        skill_name = str(r[2]).strip() if r[2] is not None else ""
        skill_type = str(r[3]).strip().upper() if r[3] is not None else "HARD"
        snippet = str(r[4]).strip() if len(r) > 4 and r[4] is not None else ""
        
        gold_by_cv.setdefault(cid, [])
        if skill_name:
            gold_by_cv[cid].append({
                "skill_name": skill_name,
                "skill_type": skill_type,
                "context_snippet": snippet
            })

    return raw_cvs, gold_by_cv

def run_extraction_with_cache(
    items: List[Dict[str, Any]],
    cache_file: str,
    extractor: EvaluationGroqExtractor,
    is_jd: bool = True
) -> Dict[str, List[Dict[str, Any]]]:
    """Chạy trích xuất kỹ năng đa luồng với bộ nhớ cache đệm."""
    cache = {}
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception:
            cache = {}

    to_process = [it for it in items if (it["job_id"] if is_jd else it["cv_id"]) not in cache]
    
    if to_process:
        item_type_str = "JD" if is_jd else "CV"
        print(f"-> Đang chạy trích xuất Groq API cho {len(to_process)} {item_type_str} mới (đã có {len(cache)} trong cache)...", flush=True)
        
        cache_lock = threading.Lock()
        done_cnt = 0

        def process_one(item):
            nonlocal done_cnt
            id_key = item["job_id"] if is_jd else item["cv_id"]
            if is_jd:
                skills = extractor.extract_jd_skills(
                    title=item.get("title", ""),
                    vi_tri=item.get("vi_tri", ""),
                    desc=item.get("description", ""),
                    req=item.get("requirements", "")
                )
            else:
                skills = extractor.extract_cv_skills(
                    category=item.get("category", ""),
                    cv_text=item.get("raw_text", "")
                )
            
            with cache_lock:
                cache[id_key] = skills
                done_cnt += 1
                # Ghi cache liên tục để không bao giờ mất kết quả
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(cache, f, ensure_ascii=False, indent=2)
                if done_cnt % 5 == 0 or done_cnt == len(to_process):
                    print(f"   [{item_type_str} Tiến độ] {done_cnt}/{len(to_process)} hoàn tất ({len(cache)} tổng trong cache).", flush=True)
            return id_key, skills

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            list(executor.map(process_one, to_process))

    return cache

# =============================================================================
# 4. THUẬT TOÁN ĐÁNH GIÁ (PRECISION / RECALL / F1)
# =============================================================================

def evaluate_dataset(
    gold_dict: Dict[str, List[Dict[str, Any]]],
    machine_dict: Dict[str, List[Dict[str, Any]]]
) -> Dict[str, Any]:
    """
    Tính toán đối soát 1-to-1 matching cho toàn bộ và theo từng skill_type.
    """
    all_skill_types = ["HARD", "SOFT", "TOOL", "KNOWLEDGE", "CERTIFICATION", "LANGUAGE"]
    
    total_tp = 0
    total_fp = 0
    total_fn = 0
    
    type_stats = {
        st: {"tp": 0, "fp": 0, "fn": 0, "gold_total": 0, "machine_total": 0}
        for st in all_skill_types
    }
    
    error_analysis_data = {
        "false_positives": [],
        "false_negatives": [],
        "type_mismatches": []
    }

    for item_id, gold_skills in gold_dict.items():
        machine_skills = machine_dict.get(item_id, [])
        
        gold_matched = set()
        machine_matched = set()
        
        # 1. Tìm True Positives (1-to-1 bipartite matching)
        for m_idx, m_item in enumerate(machine_skills):
            if isinstance(m_item, dict):
                m_name = m_item.get("skill_name", "") or m_item.get("name", "")
                m_type = str(m_item.get("skill_type", "HARD")).upper()
                m_snippet = m_item.get("context_snippet", "")
            elif isinstance(m_item, str):
                m_name = m_item.strip()
                m_type = "HARD"
                m_snippet = ""
            else:
                continue
                
            if not m_name:
                continue
            
            best_match_idx = None
            for g_idx, g_item in enumerate(gold_skills):
                if g_idx in gold_matched:
                    continue
                g_name = g_item.get("skill_name", "")
                if is_skill_match(m_name, g_name):
                    best_match_idx = g_idx
                    break
                    
            if best_match_idx is not None:
                gold_matched.add(best_match_idx)
                machine_matched.add(m_idx)
                total_tp += 1
                
                g_item = gold_skills[best_match_idx]
                g_type = g_item.get("skill_type", "HARD").upper()
                
                if m_type == g_type:
                    if g_type in type_stats:
                        type_stats[g_type]["tp"] += 1
                else:
                    error_analysis_data["type_mismatches"].append({
                        "id": item_id,
                        "skill_name": m_name,
                        "machine_type": m_type,
                        "gold_type": g_type,
                        "snippet": m_item.get("context_snippet", "")
                    })
                    if g_type in type_stats:
                        type_stats[g_type]["fn"] += 1
                    if m_type in type_stats:
                        type_stats[m_type]["fp"] += 1
            else:
                total_fp += 1
                if m_type in type_stats:
                    type_stats[m_type]["fp"] += 1
                error_analysis_data["false_positives"].append({
                    "id": item_id,
                    "skill_name": m_name,
                    "skill_type": m_type,
                    "snippet": m_item.get("context_snippet", "")
                })

        # 2. Tìm False Negatives
        for g_idx, g_item in enumerate(gold_skills):
            g_type = g_item.get("skill_type", "HARD").upper()
            if g_type in type_stats:
                type_stats[g_type]["gold_total"] += 1
                
            if g_idx not in gold_matched:
                total_fn += 1
                if g_type in type_stats:
                    type_stats[g_type]["fn"] += 1
                error_analysis_data["false_negatives"].append({
                    "id": item_id,
                    "skill_name": g_item.get("skill_name", ""),
                    "skill_type": g_type,
                    "snippet": g_item.get("context_snippet", "")
                })

        for m_item in machine_skills:
            if isinstance(m_item, dict):
                m_type = str(m_item.get("skill_type", "HARD")).upper()
            else:
                m_type = "HARD"
            if m_type in type_stats:
                type_stats[m_type]["machine_total"] += 1

    def calc_prf(tp: int, fp: int, fn: int) -> Tuple[float, float, float]:
        p = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0
        r = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0
        f1 = round(2 * p * r / (p + r), 4) if (p + r) > 0 else 0.0
        return p, r, f1

    overall_p, overall_r, overall_f1 = calc_prf(total_tp, total_fp, total_fn)

    by_type_results = {}
    for st, st_data in type_stats.items():
        tp = st_data["tp"]
        fp = st_data["fp"]
        fn = st_data["fn"]
        p, r, f1 = calc_prf(tp, fp, fn)
        by_type_results[st] = {
            "true_positive": tp,
            "false_positive": fp,
            "false_negative": fn,
            "precision": p,
            "recall": r,
            "f1_score": f1,
            "gold_count": st_data["gold_total"],
            "machine_count": st_data["machine_total"]
        }

    return {
        "overall": {
            "true_positive": total_tp,
            "false_positive": total_fp,
            "false_negative": total_fn,
            "precision": overall_p,
            "recall": overall_r,
            "f1_score": overall_f1,
            "total_gold_skills": total_tp + total_fn,
            "total_machine_skills": total_tp + total_fp
        },
        "by_skill_type": by_type_results,
        "error_analysis": error_analysis_data
    }

# =============================================================================
# 5. CHƯƠNG TRÌNH CHÍNH & XUẤT BÁO CÁO
# =============================================================================

def main():
    print("=" * 80)
    print("SKILLGAP AI - HỆ THỐNG ĐÁNH GIÁ PIPELINE TRÍCH XUẤT KỸ NĂNG VỚI GOLD STANDARD")
    print("=" * 80)

    # 1. Nạp Gold Standard
    print("\n[BƯỚC 1] Nạp dữ liệu Gold Standard từ thư mục data1...")
    raw_jds, gold_jds = load_gold_jds()
    raw_cvs, gold_cvs = load_gold_cvs()
    
    total_gold_jd_skills = sum(len(v) for v in gold_jds.values())
    total_gold_cv_skills = sum(len(v) for v in gold_cvs.values())
    print(f"  + JD: Đã nạp {len(raw_jds)} JD thô, {len(gold_jds)} JD chuẩn với {total_gold_jd_skills} kỹ năng gán nhãn.")
    print(f"  + CV: Đã nạp {len(raw_cvs)} CV thô, {len(gold_cvs)} CV chuẩn với {total_gold_cv_skills} kỹ năng gán nhãn.")

    # 2. Khởi tạo Groq Extractor và chạy pipeline trích xuất
    print("\n[BƯỚC 2] Khởi chạy Pipeline trích xuất kỹ năng bằng Groq API (qwen/qwen3.8-27b)...")
    extractor = EvaluationGroqExtractor()
    
    machine_jds = run_extraction_with_cache(raw_jds, JD_CACHE_FILE, extractor, is_jd=True)
    machine_cvs = run_extraction_with_cache(raw_cvs, CV_CACHE_FILE, extractor, is_jd=False)
    
    total_machine_jd_skills = sum(len(v) for v in machine_jds.values())
    total_machine_cv_skills = sum(len(v) for v in machine_cvs.values())
    print(f"  + Máy trích xuất được {total_machine_jd_skills} kỹ năng từ {len(machine_jds)} JD.")
    print(f"  + Máy trích xuất được {total_machine_cv_skills} kỹ năng từ {len(machine_cvs)} CV.")

    # 2.1. Hậu xử lý loại bỏ stop-skills, chuẩn hóa tên và Keyword Boost (HARD/TOOL)
    print("\n[BƯỚC 2.1] Hậu xử lý clean_skills và Keyword Boost (HARD/TOOL)...")
    raw_jd_map = {j["job_id"]: j for j in raw_jds}
    raw_cv_map = {c["cv_id"]: c for c in raw_cvs}

    cleaned_machine_jds = {}
    for jid, skills in machine_jds.items():
        cl = clean_skills(skills)
        j_obj = raw_jd_map.get(jid, {})
        full_text = f"{j_obj.get('title','')} {j_obj.get('vi_tri','')} {j_obj.get('description','')} {j_obj.get('requirements','')}"
        cleaned_machine_jds[jid] = boost_hard_tool_skills(full_text, cl)

    cleaned_machine_cvs = {}
    for cid, skills in machine_cvs.items():
        cl = clean_skills(skills)
        c_obj = raw_cv_map.get(cid, {})
        full_text = c_obj.get('raw_text', '')
        cleaned_machine_cvs[cid] = boost_hard_tool_skills(full_text, cl)
    
    total_cleaned_jd = sum(len(v) for v in cleaned_machine_jds.values())
    total_cleaned_cv = sum(len(v) for v in cleaned_machine_cvs.values())
    print(f"  + Sau clean_skills & boost: JD đạt {total_cleaned_jd} kỹ năng.")
    print(f"  + Sau clean_skills & boost: CV đạt {total_cleaned_cv} kỹ năng.")

    # 2.2. Chuẩn hóa Gold Standard về cùng không gian tên (Canonical + Soft-rule)
    print("\n[BƯỚC 2.2] Đồng bộ không gian tên cho Gold Standard (normalize_gold_for_eval)...")
    normalized_gold_jds = {k: normalize_gold_for_eval(v) for k, v in gold_jds.items()}
    normalized_gold_cvs = {k: normalize_gold_for_eval(v) for k, v in gold_cvs.items()}

    # 3. Đánh giá chi tiết
    print("\n[BƯỚC 3] Tiến hành so sánh đối soát 1-to-1 matching (Normalizing + Soft Matching)...")
    jd_eval = evaluate_dataset(normalized_gold_jds, cleaned_machine_jds)
    cv_eval = evaluate_dataset(normalized_gold_cvs, cleaned_machine_cvs)
    
    # Gộp toàn bộ (Overall)
    combined_gold = {}
    for k, v in normalized_gold_jds.items():
        combined_gold[f"JD_{k}"] = v
    for k, v in normalized_gold_cvs.items():
        combined_gold[f"CV_{k}"] = v
        
    combined_machine = {}
    for k, v in cleaned_machine_jds.items():
        combined_machine[f"JD_{k}"] = v
    for k, v in cleaned_machine_cvs.items():
        combined_machine[f"CV_{k}"] = v
        
    overall_eval = evaluate_dataset(combined_gold, combined_machine)

    # 4. Xuất các file JSON & Markdown theo yêu cầu
    print("\n[BƯỚC 4] Lưu trữ kết quả đánh giá vào thư mục gold_standard/evaluation/...")
    
    # 4.1. metrics_overall.json
    overall_metrics_output = {
        "evaluation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_documents_evaluated": len(gold_jds) + len(gold_cvs),
        "total_gold_skills": overall_eval["overall"]["total_gold_skills"],
        "total_machine_skills": overall_eval["overall"]["total_machine_skills"],
        "true_positives": overall_eval["overall"]["true_positive"],
        "false_positives": overall_eval["overall"]["false_positive"],
        "false_negatives": overall_eval["overall"]["false_negative"],
        "precision": overall_eval["overall"]["precision"],
        "recall": overall_eval["overall"]["recall"],
        "f1_score": overall_eval["overall"]["f1_score"]
    }
    with open(os.path.join(EVAL_DIR, "metrics_overall.json"), "w", encoding="utf-8") as f:
        json.dump(overall_metrics_output, f, ensure_ascii=False, indent=2)

    # 4.2. metrics_by_skill_type.json
    with open(os.path.join(EVAL_DIR, "metrics_by_skill_type.json"), "w", encoding="utf-8") as f:
        json.dump(overall_eval["by_skill_type"], f, ensure_ascii=False, indent=2)

    # 4.3. metrics_jd_vs_cv.json
    jd_vs_cv_output = {
        "job_postings_evaluation": {
            "total_jds": len(gold_jds),
            "metrics": jd_eval["overall"],
            "by_skill_type": jd_eval["by_skill_type"]
        },
        "curriculum_vitae_evaluation": {
            "total_cvs": len(gold_cvs),
            "metrics": cv_eval["overall"],
            "by_skill_type": cv_eval["by_skill_type"]
        }
    }
    with open(os.path.join(EVAL_DIR, "metrics_jd_vs_cv.json"), "w", encoding="utf-8") as f:
        json.dump(jd_vs_cv_output, f, ensure_ascii=False, indent=2)

    # 4.4. error_analysis.md
    md_content = f"""# BÁO CÁO PHÂN TÍCH LỖI TRÍCH XUẤT KỸ NĂNG (ERROR ANALYSIS)
*Thời gian đánh giá:* {time.strftime('%Y-%m-%d %H:%M:%S')}  
*Dữ liệu đối chuẩn:* 80 Tin tuyển dụng (JD) & 40 Hồ sơ ứng viên (CV) thuộc bộ Gold Standard.

---

## 1. TỔNG HỢP HIỆU SUẤT MÔ HÌNH (SUMMARY)

| Phân loại | Precision | Recall | F1-Score | Gold Skills | Machine Skills | True Positives (TP) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Toàn bộ (Overall)** | **{overall_eval['overall']['precision'] * 100:.2f}%** | **{overall_eval['overall']['recall'] * 100:.2f}%** | **{overall_eval['overall']['f1_score'] * 100:.2f}%** | {overall_eval['overall']['total_gold_skills']} | {overall_eval['overall']['total_machine_skills']} | {overall_eval['overall']['true_positive']} |
| **Tin tuyển dụng (JD)** | **{jd_eval['overall']['precision'] * 100:.2f}%** | **{jd_eval['overall']['recall'] * 100:.2f}%** | **{jd_eval['overall']['f1_score'] * 100:.2f}%** | {jd_eval['overall']['total_gold_skills']} | {jd_eval['overall']['total_machine_skills']} | {jd_eval['overall']['true_positive']} |
| **Hồ sơ ứng viên (CV)** | **{cv_eval['overall']['precision'] * 100:.2f}%** | **{cv_eval['overall']['recall'] * 100:.2f}%** | **{cv_eval['overall']['f1_score'] * 100:.2f}%** | {cv_eval['overall']['total_gold_skills']} | {cv_eval['overall']['total_machine_skills']} | {cv_eval['overall']['true_positive']} |

---

## 2. HIỆU SUẤT CHI TIẾT THEO TỪNG LOẠI KỸ NĂNG (BY SKILL TYPE)

| Nhóm kỹ năng (Skill Type) | Precision | Recall | F1-Score | Số lượng Gold | Số lượng Máy | TP | FP | FN |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
"""
    for st, v in overall_eval["by_skill_type"].items():
        md_content += f"| **{st}** | {v['precision']*100:.2f}% | {v['recall']*100:.2f}% | {v['f1_score']*100:.2f}% | {v['gold_count']} | {v['machine_count']} | {v['true_positive']} | {v['false_positive']} | {v['false_negative']} |\n"

    md_content += """
---

## 3. PHÂN TÍCH CÁC LỖI TIÊU BIỂU (ERROR SAMPLES)

### 3.1. Lỗi Bỏ sót Kỹ năng (False Negatives - FN)
*Định nghĩa:* Kỹ năng có trong Gold Standard nhưng mô hình không trích xuất được.
*Nguyên nhân chính:*
1. Kỹ năng nằm ẩn trong câu dài hoặc được viết tắt / diễn đạt gián tiếp trong JD / CV.
2. Mô hình bỏ qua các kỹ năng mềm xuất hiện ở phần trách nhiệm công việc chung.

| Tài liệu (ID) | Tên kỹ năng bị bỏ sót | Loại kỹ năng | Trích dẫn ngữ cảnh (Context Snippet) |
| :---: | :--- | :---: | :--- |
"""
    for fn in overall_eval["error_analysis"]["false_negatives"][:15]:
        snip = fn["snippet"].replace("\n", " ")[:90]
        md_content += f"| `{fn['id']}` | **{fn['skill_name']}** | `{fn['skill_type']}` | {snip}... |\n"

    md_content += """
### 3.2. Lỗi Trích xuất Dư thừa / Suy diễn (False Positives - FP)
*Định nghĩa:* Kỹ năng được máy trích xuất nhưng không có trong Gold Standard.
*Nguyên nhân chính:*
1. Máy bóc tách các khái niệm chung chung hoặc phẩm chất cá nhân (như "tự tin", "nhiệt huyết", "chăm chỉ").
2. Trích xuất cả tên vị trí / chức danh thành kỹ năng.
3. Độ chi tiết của máy cao hơn người gán nhãn (ví dụ gán nhãn chỉ lấy "Python", máy bóc tách thêm "Pandas", "NumPy").

| Tài liệu (ID) | Kỹ năng máy trích xuất dư | Loại kỹ năng | Dẫn chứng văn bản (Snippet) |
| :---: | :--- | :---: | :--- |
"""
    for fp in overall_eval["error_analysis"]["false_positives"][:15]:
        snip = fp["snippet"].replace("\n", " ")[:90]
        md_content += f"| `{fp['id']}` | **{fp['skill_name']}** | `{fp['skill_type']}` | {snip}... |\n"

    md_content += """
### 3.3. Lỗi Nhầm lẫn Phân loại Loại Kỹ năng (Skill Type Mismatches)
*Định nghĩa:* Máy tìm đúng kỹ năng nhưng phân loại sai nhóm (ví dụ: Gold gán nhãn là `TOOL`, máy gán là `HARD` hoặc ngược lại).

| Tài liệu (ID) | Tên kỹ năng | Nhãn Máy gán | Nhãn Gold chuẩn | Dẫn chứng ngữ cảnh |
| :---: | :--- | :---: | :---: | :--- |
"""
    for tm in overall_eval["error_analysis"]["type_mismatches"][:12]:
        snip = tm["snippet"].replace("\n", " ")[:90]
        md_content += f"| `{tm['id']}` | **{tm['skill_name']}** | `{tm['machine_type']}` | `{tm['gold_type']}` | {snip}... |\n"

    md_content += """
---

## 4. ĐỀ XUẤT CẢI TIẾN PIPELINE
1. **Tinh chỉnh Prompt phân định HARD vs TOOL:** Bổ sung ví dụ đối sánh cụ thể (ngôn ngữ lập trình -> `HARD`, phần mềm/IDE/thư viện -> `TOOL`).
2. **Cập nhật danh mục Stop-skills:** Loại bỏ triệt để các tính từ tính cách (nhiệt tình, trung thực, chịu khó) ra khỏi nhóm kỹ năng mềm.
3. **Canonical Post-Processing:** Tiếp tục mở rộng từ điển chuẩn hóa đồng nghĩa để tăng độ phủ và độ hội tụ giữa tiếng Anh và tiếng Việt.
"""

    with open(os.path.join(EVAL_DIR, "error_analysis.md"), "w", encoding="utf-8") as f:
        f.write(md_content)

    print("-> Đã ghi nhận xong toàn bộ 4 file báo cáo!")

    # 5. In bảng tổng kết ra console
    print("\n" + "=" * 80)
    print("BẢNG TỔNG KẾT ĐÁNH GIÁ (CONSOLE REPORT)")
    print("=" * 80)
    print(f"{'TẬP DỮ LIỆU':<25} | {'PRECISION':<10} | {'RECALL':<10} | {'F1-SCORE':<10} | {'GOLD':<8} | {'MÁY':<8} | {'TP':<6}")
    print("-" * 85)
    print(f"{'Toàn bộ (Overall)':<25} | {overall_eval['overall']['precision']*100:>8.2f}% | {overall_eval['overall']['recall']*100:>8.2f}% | {overall_eval['overall']['f1_score']*100:>8.2f}% | {overall_eval['overall']['total_gold_skills']:>8} | {overall_eval['overall']['total_machine_skills']:>8} | {overall_eval['overall']['true_positive']:>6}")
    print(f"{'Tin tuyển dụng (JD)':<25} | {jd_eval['overall']['precision']*100:>8.2f}% | {jd_eval['overall']['recall']*100:>8.2f}% | {jd_eval['overall']['f1_score']*100:>8.2f}% | {jd_eval['overall']['total_gold_skills']:>8} | {jd_eval['overall']['total_machine_skills']:>8} | {jd_eval['overall']['true_positive']:>6}")
    print(f"{'Hồ sơ ứng viên (CV)':<25} | {cv_eval['overall']['precision']*100:>8.2f}% | {cv_eval['overall']['recall']*100:>8.2f}% | {cv_eval['overall']['f1_score']*100:>8.2f}% | {cv_eval['overall']['total_gold_skills']:>8} | {cv_eval['overall']['total_machine_skills']:>8} | {cv_eval['overall']['true_positive']:>6}")
    print("-" * 85)
    
    print("\nCHI TIẾT THEO TỪNG LOẠI KỸ NĂNG (OVERALL BY SKILL TYPE):")
    print(f"{'SKILL TYPE':<15} | {'PRECISION':<10} | {'RECALL':<10} | {'F1-SCORE':<10} | {'GOLD':<8} | {'MÁY':<8} | {'TP':<6}")
    print("-" * 75)
    for st, v in overall_eval["by_skill_type"].items():
        print(f"{st:<15} | {v['precision']*100:>8.2f}% | {v['recall']*100:>8.2f}% | {v['f1_score']*100:>8.2f}% | {v['gold_count']:>8} | {v['machine_count']:>8} | {v['true_positive']:>6}")
    print("=" * 80)

if __name__ == "__main__":
    main()
