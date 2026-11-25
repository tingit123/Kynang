"""
skill_extractor.py - Module trích xuất và chuẩn hóa kỹ năng từ tin tuyển dụng
Dự án: Skill Gap Analysis (Đà Nẵng & miền Trung) - Skill Intelligence 3NF

Chức năng chính:
  1. Trích xuất kỹ năng từ văn bản tin tuyển dụng (JD) dùng Groq API (ưu tiên llama-3.3-70b-versatile,
     tự động chuyển fallback sang model chat sẵn có nếu model chỉ định không tồn tại).
  2. Tuyệt đối KHÔNG tự suy diễn kỹ năng không có trong văn bản gốc (Strict Factuality / Grounding).
  3. Chuẩn hóa tên kỹ năng về tên phổ biến nhất (VD: reactjs -> React, nodejs -> Node.js).
  4. Sử dụng mô hình embedding đa ngôn ngữ (paraphrase-multilingual-MiniLM-L12-v2) để so sánh ngữ nghĩa
     giữa kỹ năng tiếng Việt (LLM trích xuất) và kỹ năng tiếng Anh trong từ điển chuẩn ESCO v1.2.1.
  5. Đối sánh ngưỡng tương đồng (Cosine Similarity Threshold >= 0.75):
     - Nếu khớp đủ (>= 0.75): Ánh xạ sang kỹ năng chuẩn ESCO (lưu esco_uri, chuẩn hóa tên, lưu alias vào skill_aliases).
     - Nếu không khớp đủ (< 0.75): Giữ nguyên tên kỹ năng tiếng Việt (đây là kỹ năng đặc thù Việt Nam / địa phương),
       lưu vào danh mục "vietnam_local_skills" trong tệp skill_taxonomy_model_4nganh_FINAL.json để phục vụ báo cáo.
  6. Ghi trực tiếp kết quả vào cơ sở dữ liệu MySQL chuẩn 3NF:
     - Bảng skills: định danh kỹ năng, phân loại (skill_type_id), category_id, esco_uri.
     - Bảng skill_aliases: lưu tên gọi biến thể tiếng Việt của kỹ năng chuẩn.
     - Bảng job_skills: liên kết jobs (job_id) với skills (skill_id), requirement_level (required/preferred),
       extraction_source ('llm'), confidence_score.
     - Bảng jobs_raw: cập nhật cờ llm_processed = 1.
"""

import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import re
import uuid
import time
import argparse
import logging
import threading
import concurrent.futures
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

import pymysql
from pymysql.cursors import DictCursor
import torch
from sentence_transformers import SentenceTransformer, util
import groq
from tqdm import tqdm

from config import (
    MYSQL_CONFIG,
    GROQ_API_KEY,
    GROQ_MODEL,
    EMBEDDING_MODEL_NAME,
    SIMILARITY_THRESHOLD,
    ERROR_LOG_PATH,
    GROQ_RPM,
    GROQ_MAX_WORKERS
)


class RateLimiter:
    """
    Bộ điều phối tần suất Request (Token / Leaky bucket)
    Đảm bảo tần suất không vượt quá ngưỡng rpm (mặc định 100 request/phút)
    """
    def __init__(self, rpm: int = 100):
        self.rpm = rpm
        self.interval = 60.0 / float(rpm) if rpm > 0 else 0.0
        self.lock = threading.Lock()
        self.last_call = 0.0

    def wait(self):
        if self.interval <= 0:
            return
        with self.lock:
            now = time.time()
            elapsed = now - self.last_call
            if elapsed < self.interval:
                time.sleep(self.interval - elapsed)
            self.last_call = time.time()


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

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

def clean_skills(skills: list[dict]) -> list[dict]:
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

        # 1. Bỏ qua nếu thuộc STOP_SKILLS hoặc chức danh công việc
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

os.makedirs(DATA_DIR, exist_ok=True)

TAXONOMY_FILE = os.path.join(BASE_DIR, "skill_taxonomy_model_4nganh_FINAL.json")
ESCO_CACHE_FILE = os.path.join(DATA_DIR, "esco_skills_cache.pt")

# Từ điển chuẩn hóa tên công nghệ và kỹ năng phổ biến
COMMON_SKILL_ALIASES = {
    "reactjs": "React",
    "react.js": "React",
    "react js": "React",
    "react native": "React Native",
    "reactnative": "React Native",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "node js": "Node.js",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "vue js": "Vue.js",
    "angularjs": "Angular",
    "angular.js": "Angular",
    "angular": "Angular",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "nuxtjs": "Nuxt.js",
    "nuxt.js": "Nuxt.js",
    "nest.js": "NestJS",
    "nestjs": "NestJS",
    "expressjs": "Express.js",
    "express.js": "Express.js",
    "golang": "Go",
    "c#": "C#",
    "c++": "C++",
    "c/c++": "C/C++",
    "python3": "Python",
    "python": "Python",
    "java": "Java",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "php": "PHP",
    "html/css": "HTML/CSS",
    "html5/css3": "HTML/CSS",
    "html": "HTML",
    "css": "CSS",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "bootstrap": "Bootstrap",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "sql server": "SQL Server",
    "sqlserver": "SQL Server",
    "mssql": "SQL Server",
    "ms sql": "SQL Server",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "oracle": "Oracle Database",
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "docker": "Docker",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "GCP",
    "google cloud": "GCP",
    "azure": "Microsoft Azure",
    "ci/cd": "CI/CD",
    "restful api": "RESTful API",
    "rest api": "RESTful API",
    "graphql": "GraphQL",
    "linux": "Linux",
    "photoshop": "Adobe Photoshop",
    "illustrator": "Adobe Illustrator",
    "figma": "Figma",
    "canva": "Canva",
    "excel": "Microsoft Excel",
    "ms excel": "Microsoft Excel",
    "word": "Microsoft Word",
    "ms word": "Microsoft Word",
    "powerpoint": "Microsoft PowerPoint",
    "power bi": "Power BI",
    "powerbi": "Power BI",
    "misa": "Phần mềm MISA",
    "phần mềm misa": "Phần mềm MISA",
    "fast": "Phần mềm Fast",
    "phần mềm fast": "Phần mềm Fast",
    "bravo": "Phần mềm BRAVO",
    "sap": "SAP",
    "sap erp": "SAP ERP",
    "tiếng anh": "Tiếng Anh",
    "english": "Tiếng Anh",
    "tiếng trung": "Tiếng Trung Quốc",
    "tiếng nhật": "Tiếng Nhật Bản",
    "tiếng hàn": "Tiếng Hàn Quốc",
}

# Ánh xạ mã loại kỹ năng sang skill_type_id trong bảng skill_types (MySQL 3NF)
SKILL_TYPE_MAPPING = {
    "HARD": 1,           # Kỹ năng chuyên môn
    "SOFT": 2,           # Kỹ năng mềm
    "TOOL": 3,           # Công cụ / Công nghệ
    "KNOWLEDGE": 4,      # Kiến thức
    "CERTIFICATION": 5,  # Chứng chỉ
    "LANGUAGE": 6        # Ngoại ngữ
}

# Ánh xạ nhóm loại kỹ năng sang category_id trong bảng skill_categories
SKILL_CATEGORY_MAPPING = {
    "SOFT": 1,           # Nhóm Kỹ năng mềm
    "HARD": 2,           # Nhóm Kỹ năng chuyên môn
    "TOOL": 3,           # Nhóm Công cụ & Công nghệ
    "LANGUAGE": 4,       # Nhóm Ngoại ngữ
    "CERTIFICATION": 5,  # Nhóm Chứng chỉ
    "KNOWLEDGE": 2       # Nhóm Kỹ năng chuyên môn / Kiến thức
}


def normalize_skill_name(raw_name: str) -> str:
    """Chuẩn hóa tên kỹ năng về tên phổ biến nhất."""
    if not raw_name:
        return ""
    clean = re.sub(r"\s+", " ", str(raw_name).strip())
    # Loại bỏ dấu câu dư thừa ở đầu và cuối chuỗi
    clean = clean.strip(".,;:*-_`'\"()[]{}")
    low = clean.lower()
    if low in COMMON_SKILL_ALIASES:
        return COMMON_SKILL_ALIASES[low]
    # Viết hoa chữ cái đầu cho các kỹ năng thông thường
    return clean[0].upper() + clean[1:] if len(clean) > 1 else clean.upper()


class EscoSemanticMatcher:
    """
    Module so sánh ngữ nghĩa đa ngôn ngữ giữa kỹ năng tiếng Việt và kỹ năng chuẩn ESCO (tiếng Anh)
    Sử dụng model embedding paraphrase-multilingual-MiniLM-L12-v2
    """
    def __init__(self, taxonomy_path: str = TAXONOMY_FILE, cache_path: str = ESCO_CACHE_FILE):
        self.taxonomy_path = taxonomy_path
        self.cache_path = cache_path
        self.lock = threading.Lock()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[EscoMatcher] Đang khởi tạo embedding model '{EMBEDDING_MODEL_NAME}' trên thiết bị '{self.device}'...")
        self.embed_model = SentenceTransformer(EMBEDDING_MODEL_NAME, device=self.device)
        self.esco_skills: List[Dict[str, Any]] = []
        self.esco_embeddings: Optional[torch.Tensor] = None
        self._load_or_build_esco_index()

    def _load_or_build_esco_index(self):
        """Tải danh mục 3.592 skill ESCO và vector embeddings từ cache hoặc tính mới."""
        if os.path.exists(self.cache_path):
            try:
                print(f"[EscoMatcher] Đang nạp ESCO embeddings từ bộ nhớ cache: {self.cache_path}...")
                data = torch.load(self.cache_path, map_location=self.device)
                self.esco_skills = data["skills"]
                self.esco_embeddings = data["embeddings"].to(self.device)
                print(f"[EscoMatcher] Đã nạp thành công {len(self.esco_skills)} kỹ năng chuẩn ESCO từ cache.")
                return
            except Exception as e:
                print(f"[EscoMatcher] Lỗi đọc cache ({e}), tiến hành tính toán lại...")

        # Đọc từ tệp taxonomy JSON gốc
        print(f"[EscoMatcher] Đang trích xuất danh mục kỹ năng ESCO từ {self.taxonomy_path}...")
        if not os.path.exists(self.taxonomy_path):
            raise FileNotFoundError(f"Không tìm thấy tệp taxonomy: {self.taxonomy_path}")

        with open(self.taxonomy_path, "r", encoding="utf-8") as f:
            tax_data = json.load(f)

        unique_dict: Dict[str, Dict[str, Any]] = {}
        for item in tax_data.get("transversal_skills", []):
            name = item.get("skill_name", "").strip()
            if name:
                unique_dict[name.lower()] = item

        for occ in tax_data.get("occupations", []):
            for sk in occ.get("essential_skills", []) + occ.get("optional_skills", []):
                name = sk.get("skill_name", "").strip()
                if name:
                    unique_dict[name.lower()] = sk

        self.esco_skills = list(unique_dict.values())
        skill_names = [s["skill_name"] for s in self.esco_skills]
        print(f"[EscoMatcher] Bắt đầu mã hóa embeddings cho {len(skill_names)} kỹ năng ESCO (chỉ chạy lần đầu)...")
        self.esco_embeddings = self.embed_model.encode(
            skill_names,
            convert_to_tensor=True,
            show_progress_bar=True,
            device=self.device,
            batch_size=64
        )

        # Lưu cache để các lần sau nạp ngay lập tức (< 0.2s)
        torch.save({
            "skills": self.esco_skills,
            "embeddings": self.esco_embeddings.cpu()
        }, self.cache_path)
        print(f"[EscoMatcher] Đã lưu cache ESCO embeddings vào: {self.cache_path}")

    def match(self, skill_name: str, threshold: float = SIMILARITY_THRESHOLD) -> Tuple[bool, Optional[Dict[str, Any]], float]:
        """
        So khớp ngữ nghĩa một kỹ năng với toàn bộ kho ESCO.
        Trả về: (is_matched, matched_esco_skill, cosine_similarity_score)
        """
        if not skill_name or not self.esco_skills or self.esco_embeddings is None:
            return False, None, 0.0

        clean_name = skill_name.strip()
        name_lower = clean_name.lower()

        # 1. Kiểm tra so khớp chính xác tên (case-insensitive)
        for s in self.esco_skills:
            if s.get("skill_name", "").strip().lower() == name_lower:
                return True, s, 1.0

        # 2. So khớp ngữ nghĩa đa ngôn ngữ bằng mô hình embedding
        with self.lock:
            emb = self.embed_model.encode(clean_name, convert_to_tensor=True, device=self.device)
            cos_scores = util.cos_sim(emb, self.esco_embeddings)[0]
            best_idx = int(torch.argmax(cos_scores).item())
            best_score = float(cos_scores[best_idx].item())
            candidate_skill = self.esco_skills[best_idx]

        is_matched = (best_score >= threshold)
        return is_matched, candidate_skill, best_score


class LocalTaxonomyManager:
    """
    Quản lý việc lưu các kỹ năng đặc thù Việt Nam / địa phương (khi không khớp đủ với ESCO)
    vào tệp skill_taxonomy_model_4nganh_FINAL.json
    """
    def __init__(self, taxonomy_path: str = TAXONOMY_FILE):
        self.taxonomy_path = taxonomy_path
        self.lock = threading.Lock()
        self.taxonomy_data: Dict[str, Any] = {}
        self.local_skills_map: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self):
        """Nạp dữ liệu taxonomy và khởi tạo danh mục kỹ năng đặc thù Việt Nam."""
        if os.path.exists(self.taxonomy_path):
            with open(self.taxonomy_path, "r", encoding="utf-8") as f:
                self.taxonomy_data = json.load(f)
        else:
            self.taxonomy_data = {}

        if "vietnam_local_skills" not in self.taxonomy_data:
            self.taxonomy_data["vietnam_local_skills"] = []

        for item in self.taxonomy_data["vietnam_local_skills"]:
            self.local_skills_map[item["skill_name"].lower()] = item

    def add_or_update_local_skill(
        self,
        skill_name: str,
        skill_type: str,
        industry: str,
        candidate_esco: Optional[Dict[str, Any]],
        similarity_score: float,
        context_snippet: str = ""
    ) -> Dict[str, Any]:
        """Ghi nhận một kỹ năng đặc thù Việt Nam mới hoặc tăng tần suất nếu đã xuất hiện."""
        with self.lock:
            low = skill_name.strip().lower()
            if low in self.local_skills_map:
                entry = self.local_skills_map[low]
                entry["frequency"] = entry.get("frequency", 1) + 1
                if industry and industry not in entry.get("industries", []):
                    entry.setdefault("industries", []).append(industry)
                return entry

            new_entry = {
                "skill_id": f"vn-local-{uuid.uuid4().hex[:8]}",
                "skill_name": skill_name.strip(),
                "skill_type": skill_type,
                "is_soft_skill": (skill_type == "SOFT"),
                "industries": [industry] if industry else [],
                "source": "job_posting_extracted",
                "esco_skill_uri": None,
                "best_esco_match_attempt": {
                    "esco_skill_name": candidate_esco.get("skill_name") if candidate_esco else None,
                    "similarity_score": round(similarity_score, 4)
                },
                "sample_snippet": context_snippet[:200] if context_snippet else "",
                "frequency": 1,
                "first_detected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.taxonomy_data["vietnam_local_skills"].append(new_entry)
            self.local_skills_map[low] = new_entry
            return new_entry

    def save(self):
        """Ghi an toàn lại tệp taxonomy JSON."""
        with self.lock:
            with open(self.taxonomy_path, "w", encoding="utf-8") as f:
                json.dump(self.taxonomy_data, f, ensure_ascii=False, indent=2)


class GroqSkillExtractor:
    """
    Module gọi Groq API để bóc tách kỹ năng từ văn bản tin tuyển dụng.
    Áp dụng ràng buộc nghiêm ngặt: KHÔNG tự suy diễn, phải có dẫn chứng trong bài.
    """
    def __init__(self, api_key: str = GROQ_API_KEY, preferred_model: str = GROQ_MODEL, rate_limiter: Optional[RateLimiter] = None):
        self.api_key = api_key or GROQ_API_KEY
        self.client = groq.Groq(api_key=self.api_key)
        self.preferred_model = preferred_model or "llama-3.3-70b-versatile"
        self.active_model: Optional[str] = None
        self.rate_limiter = rate_limiter
        self._model_lock = threading.Lock()
        # Danh sách các model fallback theo thứ tự ưu tiên
        self.fallback_models = [
            "qwen/qwen3.8-27b",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b"
        ]
        self._determine_working_model()

    def _determine_working_model(self) -> str:
        """Kiểm tra và tự động chọn model hoạt động tốt nhất trên tài khoản Groq."""
        with self._model_lock:
            if self.active_model:
                return self.active_model

            models_to_try = [self.preferred_model] + [m for m in self.fallback_models if m != self.preferred_model]
            for m in models_to_try:
                try:
                    resp = self.client.chat.completions.create(
                        model=m,
                        messages=[{"role": "user", "content": "ping"}],
                        max_tokens=2
                    )
                    self.active_model = m
                    print(f"[GroqExtractor] Model đang hoạt động: {self.active_model}")
                    return self.active_model
                except Exception as e:
                    pass

            raise RuntimeError("[GroqExtractor] Không có model chat nào khả dụng với API key hiện tại.")

    def extract_skills_from_text(self, title: str, description: str, requirements: str) -> List[Dict[str, Any]]:
        """
        Gửi yêu cầu tới Groq API để trích xuất các kỹ năng từ nội dung tin tuyển dụng.
        """
        model = self._determine_working_model()

        # Cắt bớt văn bản nếu quá dài để tối ưu token
        desc_clean = (description or "")[:3000].strip()
        req_clean = (requirements or "")[:3000].strip()
        title_clean = (title or "")[:255].strip()

        if not desc_clean and not req_clean:
            return []

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

## Văn bản cần trích xuất
Tiêu đề: {title_clean}
Mô tả: {desc_clean}
Yêu cầu: {req_clean}
"""

        models_to_try = [model] + [m for m in self.fallback_models if m != model]
        for current_model in models_to_try:
            for attempt in range(3):
                try:
                    # Điều phối nhịp độ request theo giới hạn RPM (100 request/phút)
                    if self.rate_limiter:
                        self.rate_limiter.wait()

                    resp = self.client.chat.completions.create(
                        model=current_model,
                        messages=[{"role": "user", "content": prompt}],
                        response_format={"type": "json_object"},
                        temperature=0.1  # Nhiệt độ thấp đảm bảo tính trung thực và ổn định
                    )
                    raw_content = resp.choices[0].message.content
                    if not raw_content:
                        continue
                    parsed = json.loads(raw_content)
                    if isinstance(parsed, list):
                        skills = parsed
                    elif isinstance(parsed, dict):
                        skills = parsed.get("skills", [])
                        if not skills:
                            for v in parsed.values():
                                if isinstance(v, list):
                                    skills = v
                                    break
                    else:
                        skills = []
                    cleaned = clean_skills(skills)
                    full_text = f"{title_clean} {desc_clean} {req_clean}"
                    return boost_hard_tool_skills(full_text, cleaned)
                except Exception as e:
                    err_str = str(e).lower()
                    if "rate limit" in err_str or "429" in err_str:
                        wait_time = (attempt + 1) * 8
                        print(f"\n[GroqExtractor] Model {current_model} rate limit 429, tạm dừng {wait_time}s rồi thử lại...")
                        time.sleep(wait_time)
                        continue
                    else:
                        # Lỗi khác (VD: 400 format) -> Thử model fallback tiếp theo
                        logging.warning(f"[GroqExtractor] Model {current_model} gặp lỗi: {e}. Đang chuyển model dự phòng...")
                        break
        return []


class SkillIntelligenceDatabaseWriter:
    """
    Module phụ trách đọc dữ liệu thô và ghi kết quả kỹ năng sạch vào cơ sở dữ liệu MySQL 3NF:
    - Bảng skills
    - Bảng skill_aliases
    - Bảng job_skills
    - Cập nhật jobs_raw (llm_processed = 1)
    """
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or MYSQL_CONFIG
        self.conn = None
        self.lock = threading.Lock()
        self._connect()

    def _connect(self):
        try:
            self.conn = pymysql.connect(
                host=self.config.get("host", "localhost"),
                user=self.config.get("user", "root"),
                password=self.config.get("password", ""),
                database=self.config.get("database", "skill_intelligence"),
                port=self.config.get("port", 3306),
                charset=self.config.get("charset", "utf8mb4"),
                autocommit=True,
                cursorclass=DictCursor
            )
        except pymysql.MySQLError as e:
            err_msg = f"[DBWriter] Lỗi kết nối MySQL: {e}"
            print(err_msg)
            logging.error(err_msg)
            raise e

    def ensure_connected(self):
        try:
            if self.conn is None or not self.conn.open:
                self._connect()
            else:
                self.conn.ping()
        except Exception:
            self._connect()

    def close(self):
        with self.lock:
            if self.conn and self.conn.open:
                try:
                    self.conn.close()
                except Exception:
                    pass

    def get_or_create_skill(
        self,
        skill_name: str,
        skill_type_code: str,
        esco_uri: Optional[str] = None
    ) -> int:
        """
        Tìm hoặc chèn mới kỹ năng vào bảng skills.
        Đảm bảo không trùng lặp và tương thích hoàn toàn chuẩn 3NF.
        """
        with self.lock:
            self.ensure_connected()
            skill_type_id = SKILL_TYPE_MAPPING.get(skill_type_code, 1)
            category_id = SKILL_CATEGORY_MAPPING.get(skill_type_code, 2)

            with self.conn.cursor() as cur:
                # 1. Tra cứu theo esco_uri nếu có
                if esco_uri:
                    cur.execute("SELECT skill_id FROM skills WHERE esco_uri = %s LIMIT 1;", (esco_uri,))
                    row = cur.fetchone()
                    if row:
                        return int(row["skill_id"])

                # 2. Tra cứu theo skill_name
                cur.execute("SELECT skill_id, esco_uri FROM skills WHERE skill_name = %s LIMIT 1;", (skill_name,))
                row = cur.fetchone()
                if row:
                    sid = int(row["skill_id"])
                    # Nếu trước đây chưa có esco_uri mà giờ có thì cập nhật bổ sung
                    if esco_uri and not row.get("esco_uri"):
                        cur.execute("UPDATE skills SET esco_uri = %s WHERE skill_id = %s;", (esco_uri, sid))
                    return sid

                # 3. Chèn mới vào bảng skills
                insert_sql = """
                    INSERT INTO skills (skill_name, skill_type_id, category_id, esco_uri)
                    VALUES (%s, %s, %s, %s);
                """
                cur.execute(insert_sql, (skill_name, skill_type_id, category_id, esco_uri))
                return int(cur.lastrowid)

    def add_skill_alias(self, skill_id: int, alias_text: str, language_code: str = "vi"):
        """Chèn alias của kỹ năng vào bảng skill_aliases nếu chưa có."""
        if not alias_text or not skill_id:
            return
        with self.lock:
            self.ensure_connected()
            try:
                with self.conn.cursor() as cur:
                    sql = """
                        INSERT IGNORE INTO skill_aliases (skill_id, alias_text, language_code)
                        VALUES (%s, %s, %s);
                    """
                    cur.execute(sql, (skill_id, alias_text.strip(), language_code))
            except Exception as e:
                pass

    def link_job_skill(
        self,
        job_id: int,
        skill_id: int,
        requirement_level: str,
        confidence_score: float
    ):
        """
        Liên kết tin tuyển dụng (jobs.job_id) với kỹ năng (skills.skill_id) trong bảng job_skills.
        """
        with self.lock:
            self.ensure_connected()
            req_level = "preferred" if requirement_level.lower() == "preferred" else "required"
            score = min(max(float(confidence_score), 0.0), 1.0)

            with self.conn.cursor() as cur:
                sql = """
                    INSERT INTO job_skills (job_id, skill_id, requirement_level, extraction_source, confidence_score)
                    VALUES (%s, %s, %s, 'llm', %s)
                    ON DUPLICATE KEY UPDATE
                        requirement_level = VALUES(requirement_level),
                        confidence_score = GREATEST(COALESCE(confidence_score, 0), VALUES(confidence_score));
                """
                cur.execute(sql, (job_id, skill_id, req_level, score))

    def mark_job_raw_processed(self, raw_job_id: str):
        """Cập nhật cờ llm_processed = 1 trong bảng jobs_raw."""
        with self.lock:
            self.ensure_connected()
            with self.conn.cursor() as cur:
                cur.execute("UPDATE jobs_raw SET llm_processed = 1 WHERE job_id = %s;", (str(raw_job_id),))

    def fetch_unprocessed_jobs(self, limit: Optional[int] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Đọc các tin tuyển dụng cần xử lý kỹ năng (kết hợp bảng jobs và jobs_raw).
        """
        self.ensure_connected()
        sql = """
            SELECT 
                j.job_id,
                j.raw_job_id,
                j.title,
                j.description,
                j.requirements,
                r.category,
                r.skills_required_tags
            FROM jobs j
            JOIN jobs_raw r ON r.job_id = j.raw_job_id
            WHERE r.llm_processed = 0 OR r.llm_processed IS NULL
        """
        params = []
        if category:
            sql += " AND r.category = %s"
            params.append(category)

        sql += " ORDER BY j.job_id ASC"
        if limit and limit > 0:
            sql += f" LIMIT {int(limit)}"

        with self.conn.cursor() as cur:
            cur.execute(sql, tuple(params))
            return cur.fetchall()


class SkillExtractionPipeline:
    """
    Toàn bộ luồng điều phối: Đọc tin -> Groq trích xuất -> So khớp ESCO -> Lưu DB 3NF & Cập nhật Taxonomy
    """
    def __init__(self, threshold: float = SIMILARITY_THRESHOLD, rpm: int = GROQ_RPM, workers: int = GROQ_MAX_WORKERS):
        self.threshold = threshold
        self.rpm = rpm
        self.workers = workers
        self.rate_limiter = RateLimiter(rpm=rpm)
        self.matcher = EscoSemanticMatcher()
        self.taxonomy_mgr = LocalTaxonomyManager()
        self.extractor = GroqSkillExtractor(rate_limiter=self.rate_limiter)
        self.db = SkillIntelligenceDatabaseWriter()

    def _extract_fallback_from_tags(self, tags_raw: Any, industry: str) -> List[Dict[str, Any]]:
        """
        Trích xuất kỹ năng từ mảng skills_required_tags của TopCV khi Groq gặp lỗi hoặc trả về rỗng.
        Loại bỏ các tag không phải kỹ năng (địa điểm, chế độ, kinh nghiệm, tuổi tác).
        """
        if not tags_raw:
            return []
        tags = json.loads(tags_raw) if isinstance(tags_raw, str) else tags_raw
        if not isinstance(tags, list):
            return []

        non_skill_patterns = [
            'hà nội', 'hồ chí minh', 'đà nẵng', 'hải phòng', 'cần thơ', 'hưng yên',
            'thái bình', 'bình dương', 'đồng nai', 'bà rịa', 'quảng nam', 'thừa thiên huế',
            'huế', 'quảng ngãi', 'bắc ninh', 'vĩnh phúc', 'long an', 'tiền giang',
            'phường ', 'xã ', 'quận ', 'huyện ', 'tại ',
            'bảo hiểm', 'bhxh', 'khám sức khỏe', 'thưởng', 'lương', 'chế độ', 'phúc lợi',
            'team building', 'thiết bị', 'đồng phục', 'cơm trưa',
            'nam', 'nữ', 'tuổi', 'ngoại hình', 'ưa nhìn', 'đi làm ngay',
            'đại học', 'cao đẳng', 'trung cấp', 'thpt', 'cử nhân',
            'năm kinh nghiệm', 'kinh nghiệm', 'chưa kinh nghiệm',
            'việc làm', 'tuyển dụng', 'lao động phổ thông'
        ]

        extracted = []
        for t in tags:
            t_str = str(t).strip()
            t_low = t_str.lower()
            if len(t_str) < 2:
                continue
            if any(p in t_low for p in non_skill_patterns):
                continue

            skill_type = "HARD"
            if any(kw in t_low for kw in ["tiếng anh", "tiếng trung", "tiếng nhật", "tiếng hàn", "ngoại ngữ"]):
                skill_type = "LANGUAGE"
            elif any(kw in t_low for kw in ["excel", "word", "misa", "fast", "bravo", "git", "docker", "react", "node", "python", "sql", "photoshop"]):
                skill_type = "TOOL"
            elif any(kw in t_low for kw in ["giao tiếp", "nhóm", "thuyết trình", "đàm phán", "giải quyết vấn đề", "chịu áp lực", "cẩn thận", "trung thực"]):
                skill_type = "SOFT"
            elif any(kw in t_low for kw in ["chứng chỉ", "bằng cấp", "ielts", "toeic", "cpa", "acca"]):
                skill_type = "CERTIFICATION"
            elif any(kw in t_low for kw in ["luật", "thông tư", "nguyên lý", "quy định", "tiêu chuẩn"]):
                skill_type = "KNOWLEDGE"

            extracted.append({
                "skill_name": t_str,
                "requirement_level": "required",
                "skill_type": skill_type,
                "context_snippet": f"Tag tuyển dụng TopCV: {t_str}"
            })
        return clean_skills(extracted)

    def process_single_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Xử lý trích xuất và chuẩn hóa kỹ năng cho một tin tuyển dụng (Cơ chế Hybrid Groq + Tags Fallback)."""
        clean_job_id = int(job["job_id"])
        raw_job_id = str(job["raw_job_id"])
        title = job.get("title") or ""
        desc = job.get("description") or ""
        reqs = job.get("requirements") or ""
        industry = job.get("category") or ""

        # 1. Gọi LLM bóc tách kỹ năng từ văn bản
        extracted_skills = self.extractor.extract_skills_from_text(title, desc, reqs)
        
        # 1b. Fallback tầng 2: Nếu LLM trả về rỗng (do rate limit hoặc lỗi), dùng tags TopCV
        if not extracted_skills:
            tags_raw = job.get("skills_required_tags")
            extracted_skills = self._extract_fallback_from_tags(tags_raw, industry)
            if extracted_skills:
                print(f"[Fallback-Tags] Job #{clean_job_id} ({title[:30]}) bóc tách được {len(extracted_skills)} kỹ năng từ tags!")

        results = []

        for item in extracted_skills:
            raw_skill_name = item.get("skill_name", "").strip()
            if not raw_skill_name:
                continue

            # Chuẩn hóa tên phổ biến
            norm_name = normalize_skill_name(raw_skill_name)
            req_level = item.get("requirement_level", "required")
            skill_type = item.get("skill_type", "HARD").upper()
            snippet = item.get("context_snippet", "")

            # 2. So khớp ngữ nghĩa với ESCO (3.592 kỹ năng chuẩn của 4 ngành)
            is_matched, esco_cand, score = self.matcher.match(norm_name, threshold=self.threshold)

            if is_matched and esco_cand:
                # ==============================================================
                # TRƯỜNG HỢP 1: KHỚP VỚI ESCO (QUỐC TẾ)
                # ==============================================================
                target_skill_name = esco_cand["skill_name"]
                esco_uri = esco_cand.get("esco_skill_uri")
                skill_id = self.db.get_or_create_skill(target_skill_name, skill_type, esco_uri=esco_uri)

                # Lưu alias tiếng Việt vào skill_aliases
                if norm_name.lower() != target_skill_name.lower():
                    self.db.add_skill_alias(skill_id, norm_name, language_code="vi")
                if raw_skill_name.lower() != norm_name.lower():
                    self.db.add_skill_alias(skill_id, raw_skill_name, language_code="vi")

                confidence = round(score, 3)
                is_local = False
            else:
                # ==============================================================
                # TRƯỜNG HỢP 2: KỸ NĂNG ĐẶC THÙ VIỆT NAM (KHÔNG KHỚP ĐỦ VỚI ESCO)
                # Giữ nguyên tên tiếng Việt, lưu vào taxonomy model & DB với esco_uri=NULL
                # ==============================================================
                target_skill_name = norm_name
                esco_uri = None
                skill_id = self.db.get_or_create_skill(target_skill_name, skill_type, esco_uri=None)

                # Ghi nhận vào taxonomy JSON phục vụ phân tích thị trường nội địa
                self.taxonomy_mgr.add_or_update_local_skill(
                    skill_name=target_skill_name,
                    skill_type=skill_type,
                    industry=industry,
                    candidate_esco=esco_cand,
                    similarity_score=score,
                    context_snippet=snippet
                )
                confidence = round(score, 3)
                is_local = True

            # 3. Liên kết vào bảng job_skills (MySQL 3NF)
            self.db.link_job_skill(
                job_id=clean_job_id,
                skill_id=skill_id,
                requirement_level=req_level,
                confidence_score=confidence
            )

            results.append({
                "skill_id": skill_id,
                "skill_name": target_skill_name,
                "original_extracted": raw_skill_name,
                "requirement_level": req_level,
                "skill_type": skill_type,
                "is_matched_esco": is_matched,
                "esco_uri": esco_uri,
                "similarity_score": score,
                "is_local_vietnam": is_local
            })

        # 4. CHỈ đánh dấu tin đã được xử lý trong jobs_raw khi đã có kỹ năng thực tế lưu thành công
        if len(results) > 0:
            self.db.mark_job_raw_processed(raw_job_id)
        else:
            logging.warning(f"Job {clean_job_id} ({title}) không có kỹ năng nào sau cả LLM và Fallback!")

        return {
            "job_id": clean_job_id,
            "raw_job_id": raw_job_id,
            "title": title,
            "skills_count": len(results),
            "skills": results
        }

    def run_batch(self, limit: Optional[int] = None, category: Optional[str] = None):
        """Chạy xử lý hàng loạt tin tuyển dụng từ MySQL đa luồng với rate limiter."""
        jobs = self.db.fetch_unprocessed_jobs(limit=limit, category=category)
        total_jobs = len(jobs)
        print(f"\n=================================================================")
        print(f"BẮT ĐẦU TRÍCH XUẤT KỸ NĂNG CHO {total_jobs} TIN TUYỂN DỤNG THÔ")
        print(f"Tần suất điều phối: {self.rpm} request/phút | Số luồng song song: {self.workers}")
        print(f"Ngưỡng tương đồng ESCO: {self.threshold}")
        print(f"=================================================================")

        if total_jobs == 0:
            print("Tất cả các tin tuyển dụng đã được xử lý xong (llm_processed = 1).")
            return

        total_skills_extracted = 0
        total_esco_matched = 0
        total_vietnam_local = 0
        stats_lock = threading.Lock()

        pbar = tqdm(total=total_jobs, desc=f"Xử lý Skill Extraction ({self.rpm} req/m)")

        def process_job_worker(job):
            nonlocal total_skills_extracted, total_esco_matched, total_vietnam_local
            try:
                res = self.process_single_job(job)
                with stats_lock:
                    total_skills_extracted += res["skills_count"]
                    total_esco_matched += sum(1 for s in res["skills"] if s["is_matched_esco"])
                    total_vietnam_local += sum(1 for s in res["skills"] if s["is_local_vietnam"])
                    pbar.update(1)
                    if pbar.n % 20 == 0:
                        self.taxonomy_mgr.save()
            except Exception as e:
                err_msg = f"Lỗi xử lý job_id {job.get('job_id')}: {e}"
                print(err_msg)
                logging.error(err_msg)
                with stats_lock:
                    pbar.update(1)

        if self.workers > 1:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.workers) as executor:
                futures = [executor.submit(process_job_worker, job) for job in jobs]
                concurrent.futures.wait(futures)
        else:
            for job in jobs:
                process_job_worker(job)

        pbar.close()
        self.taxonomy_mgr.save()

        print(f"\n=================================================================")
        print(f"HOÀN THÀNH BATCH TRÍCH XUẤT KỸ NĂNG:")
        print(f"- Số tin tuyển dụng đã xử lý: {total_jobs}")
        print(f"- Tổng số kỹ năng trích xuất: {total_skills_extracted}")
        print(f"- Số kỹ năng khớp chuẩn ESCO: {total_esco_matched} ({total_esco_matched*100/max(total_skills_extracted, 1):.1f}%)")
        print(f"- Số kỹ năng đặc thù Việt Nam: {total_vietnam_local} (đã lưu vào taxonomy JSON & MySQL)")
        print(f"=================================================================\n")


def main():
    parser = argparse.ArgumentParser(description="Skill Extraction Pipeline sử dụng Groq API và Embedding Đa Ngôn Ngữ")
    parser.add_argument("--limit", type=int, default=10, help="Số lượng tin tuyển dụng cần xử lý (mặc định: 10, đặt 0 để chạy hết)")
    parser.add_argument("--category", type=str, default=None, help="Chỉ xử lý nhóm ngành cụ thể (VD: 'Công nghệ Thông tin')")
    parser.add_argument("--threshold", type=float, default=SIMILARITY_THRESHOLD, help="Ngưỡng Cosine Similarity để so khớp ESCO (mặc định: 0.75)")
    parser.add_argument("--rpm", type=int, default=GROQ_RPM, help="Tần suất tối đa qua Groq API (request/phút, mặc định: 100)")
    parser.add_argument("--workers", type=int, default=GROQ_MAX_WORKERS, help="Số luồng song song (mặc định: 4)")
    parser.add_argument("--test-text", type=str, default=None, help="Chạy thử nghiệm trích xuất một đoạn văn bản tùy ý không ghi DB")
    parser.add_argument("--test-job-id", type=str, default=None, help="Chạy thử nghiệm trên một job_id cụ thể từ DB")
    args = parser.parse_args()

    pipeline = SkillExtractionPipeline(threshold=args.threshold, rpm=args.rpm, workers=args.workers)

    # Chế độ thử nghiệm với đoạn text tùy ý
    if args.test_text:
        print("\n--- CHẠY THỬ NGHIỆM VỚI ĐOẠN VĂN BẢN TÙY Ý ---")
        skills = pipeline.extractor.extract_skills_from_text(
            title="Tin thử nghiệm",
            description=args.test_text,
            requirements=""
        )
        print(f"Trích xuất được {len(skills)} kỹ năng:")
        for s in skills:
            norm = normalize_skill_name(s.get("skill_name", ""))
            matched, esco_cand, score = pipeline.matcher.match(norm, threshold=args.threshold)
            print(f"- {s.get('skill_name')} -> Chuẩn hóa: '{norm}' ({s.get('skill_type')}, {s.get('requirement_level')})")
            if matched:
                print(f"  + KHỚP ESCO: '{esco_cand['skill_name']}' | Similarity: {score:.4f} | URI: {esco_cand.get('esco_skill_uri')}")
            else:
                print(f"  + ĐẶC THÙ VIỆT NAM (Không khớp ESCO) | Best match: '{esco_cand.get('skill_name') if esco_cand else 'None'}' ({score:.4f})")
        return

    # Chế độ thử nghiệm trên 1 job_id cụ thể
    if args.test_job_id:
        print(f"\n--- CHẠY THỬ NGHIỆM TRÊN RAW JOB ID: {args.test_job_id} ---")
        conn = pymysql.connect(**MYSQL_CONFIG, cursorclass=DictCursor)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT j.job_id, j.raw_job_id, j.title, j.description, j.requirements, r.category, r.skills_required_tags
                FROM jobs j
                JOIN jobs_raw r ON r.job_id = j.raw_job_id
                WHERE j.raw_job_id = %s OR j.job_id = %s
                LIMIT 1;
            """, (args.test_job_id, args.test_job_id))
            job = cur.fetchone()
        conn.close()

        if not job:
            print(f"Không tìm thấy job_id: {args.test_job_id}")
            return

        res = pipeline.process_single_job(job)
        pipeline.taxonomy_mgr.save()
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return

    # Chế độ xử lý batch thông thường
    limit_val = None if args.limit <= 0 else args.limit
    pipeline.run_batch(limit=limit_val, category=args.category)


if __name__ == "__main__":
    main()
