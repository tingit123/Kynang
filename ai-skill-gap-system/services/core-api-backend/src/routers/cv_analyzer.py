# -*- coding: utf-8 -*-
"""
Router: Autonomous AI CV Analyzer & Personalized Learning Roadmap
(Powered by Gemini AI + Tesseract OCR + ESCO Skill Engine)
"""
import os
import re
import json
import logging
import socket
from typing import Optional, List, Dict, Any

# Ensure IPv4-only resolution to avoid Docker IPv6 network unreachable error on Windows
try:
    _orig_getaddrinfo = socket.getaddrinfo
    def _ipv4_only_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        return [r for r in _orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)]
    socket.getaddrinfo = _ipv4_only_getaddrinfo
except Exception:
    pass

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import date
import uuid

from src.database import get_db
from src.core.security import get_current_user_optional, get_current_user
from src.models.user import User
from src.models.survey import SurveyResponse, SurveySkillRating
from src.models.skill import SkillCatalog

logger = logging.getLogger("cv_analyzer")
router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()


# ── STANDARD ROLES & ESCO PROFILES ─────────────────────────────────
STANDARD_ROLE_PROFILES = {
    "Kế Toán Tổng Hợp": {
        "industry": "Kế Toán & Tài Chính",
        "reqSkills": ["Kế toán", "Báo cáo tài chính", "Thuế", "MISA", "Excel", "FAST"],
        "courses": {
            "Báo cáo tài chính": {"title": "Đọc Hiểu & Lập Báo Cáo Tài Chính Chuẩn VAS", "src": "Viện PACE", "dur": "4 tuần", "price": "1.8tr", "url": "https://pace.edu.vn"},
            "Thuế": {"title": "Chính Sách Thuế & Quyết Toán Thuế Doanh Nghiệp", "src": "Hội Kế Toán Cần Thơ", "dur": "3 tuần", "price": "1.2tr", "url": "https://vcaa.edu.vn"},
            "MISA": {"title": "Kế Toán Máy Thực Hành Trên Phần Mềm MISA SME", "src": "MISA Academy", "dur": "2 tuần", "price": "800K", "url": "https://misa.vn"},
            "FAST": {"title": "Kế Toán Doanh Nghiệp Fast Accounting", "src": "Fast Software", "dur": "2 tuần", "price": "600K", "url": "https://fast.com.vn"},
            "Excel": {"title": "Excel Chuyên Sâu Cho Kế Toán & Tài Chính", "src": "ĐH Cần Thơ (CTU)", "dur": "3 tuần", "price": "900K", "url": "https://ctu.edu.vn"}
        }
    },
    "Kế Toán Thuế & Báo Cáo": {
        "industry": "Kế Toán & Tài Chính",
        "reqSkills": ["Thuế", "Báo cáo tài chính", "Kế toán", "MISA", "Excel"],
        "courses": {
            "Thuế": {"title": "Nghiệp Vụ Kê Khai & Thanh Tra Thuế", "src": "VCCI Cần Thơ", "dur": "4 tuần", "price": "1.5tr", "url": "https://vccicantho.com.vn"},
            "Báo cáo tài chính": {"title": "Lập Báo Cáo Tài Chính Chuẩn VAS", "src": "Viện PACE", "dur": "3 tuần", "price": "1.4tr", "url": "https://pace.edu.vn"}
        }
    },
    "Chuyên Viên Phân Tích Tài Chính": {
        "industry": "Kế Toán & Tài Chính",
        "reqSkills": ["Phân tích tài chính", "Báo cáo tài chính", "Excel", "Power BI", "Tiếng Anh"],
        "courses": {
            "Phân tích tài chính": {"title": "Corporate Financial Modeling & Valuation", "src": "Coursera × Wharton", "dur": "5 tuần", "price": "Miễn phí", "url": "https://coursera.org"},
            "Power BI": {"title": "Financial Dashboarding với Microsoft Power BI", "src": "Microsoft Learn", "dur": "4 tuần", "price": "Miễn phí", "url": "https://learn.microsoft.com"}
        }
    },
    "Python Developer": {
        "industry": "Công nghệ thông tin",
        "reqSkills": ["Python", "SQL", "Git", "FastAPI", "Docker"],
        "courses": {
            "FastAPI": {"title": "FastAPI & RESTful Microservices", "src": "Udemy", "dur": "3 tuần", "price": "299K", "url": "https://udemy.com"},
            "Docker": {"title": "Docker & Containerization Mastery", "src": "Coursera", "dur": "3 tuần", "price": "Miễn phí", "url": "https://coursera.org"},
            "Python": {"title": "Python Backend Engineering", "src": "ĐH Cần Thơ (CTU)", "dur": "6 tuần", "price": "1.5tr", "url": "https://ctu.edu.vn"}
        }
    },
    "Data Analyst": {
        "industry": "Công nghệ thông tin",
        "reqSkills": ["SQL", "Python", "Power BI", "Excel", "Thống kê"],
        "courses": {
            "Power BI": {"title": "Data Visualization & Analytics với Power BI", "src": "Microsoft Learn", "dur": "4 tuần", "price": "Miễn phí", "url": "https://learn.microsoft.com"},
            "SQL": {"title": "SQL for Data Science & Analytics", "src": "Coursera", "dur": "4 tuần", "price": "Miễn phí", "url": "https://coursera.org"}
        }
    },
    "Chuyên Viên Xuất Nhập Khẩu": {
        "industry": "Logistics & Chuỗi cung ứng",
        "reqSkills": ["Logistics", "Xuất nhập khẩu", "Nghiệp vụ hải quan", "Tiếng Anh", "Incoterms 2020"],
        "courses": {
            "Nghiệp vụ hải quan": {"title": "Thủ Tục Hải Quan & Khai Báo VNACCS/VCIS", "src": "VCCI Cần Thơ", "dur": "4 tuần", "price": "1.5tr", "url": "https://vccicantho.com.vn"},
            "Xuất nhập khẩu": {"title": "Nghiệp Vụ Xuất Nhập Khẩu Thực Chiến", "src": "VILAS", "dur": "6 tuần", "price": "2.5tr", "url": "https://vilas.edu.vn"}
        }
    },
    "Hướng Dẫn Viên Du Lịch": {
        "industry": "Du lịch & Khách sạn",
        "reqSkills": ["Hướng dẫn du lịch", "Tiếng Anh", "Customer Service", "Giao tiếp", "Xử lý than phiền"],
        "courses": {
            "Hướng dẫn du lịch": {"title": "Nghiệp Vụ Hướng Dẫn Viên Du Lịch Quốc Tế", "src": "Saigontourist Academy", "dur": "6 tuần", "price": "2.0tr", "url": "https://saigontourist.edu.vn"},
            "Tiếng Anh": {"title": "English for Tourism & Hospitality", "src": "British Council", "dur": "8 tuần", "price": "3.5tr", "url": "https://britishcouncil.vn"}
        }
    }
}


def save_cv_to_database(db: Session, res: Dict[str, Any], current_user: Optional[User]) -> None:
    """
    Lưu trực tiếp hồ sơ CV và kỹ năng của người dùng vào cơ sở dữ liệu của năm 2026.
    Ghi nhận vào survey_responses và survey_skill_ratings để dữ liệu được phản ánh tức thì.
    """
    try:
        if not isinstance(res, dict):
            return

        cand_name = res.get("candidate_name") or "Ứng Viên"
        target_role = res.get("target_role") or "Chuyên viên"

        # Xác định ngành nghề phù hợp
        major = "Công nghệ thông tin"
        for role_name, profile in STANDARD_ROLE_PROFILES.items():
            if role_name.lower() in target_role.lower() or target_role.lower() in role_name.lower():
                major = profile.get("industry", "Công nghệ thông tin")
                break

        # Mốc ngày và năm 2026 (dữ liệu năm 2026)
        today = date.today()
        target_year = 2026 if today.year < 2026 else today.year
        completed_date = date(target_year, today.month, today.day)

        student_code = f"CV26-{uuid.uuid4().hex[:6].upper()}"

        survey = SurveyResponse(
            user_id=current_user.id if current_user else None,
            student_code=student_code,
            full_name=cand_name,
            major=major,
            year_of_study=4,
            institution="Hồ sơ ứng viên thực tế 2026",
            completed_at=completed_date
        )
        db.add(survey)
        db.commit()
        db.refresh(survey)

        # Lưu các kỹ năng thực tế trích xuất từ CV
        skills = res.get("all_detected_skills") or res.get("matched_skills") or []
        for sk_name in skills[:15]:
            sk_clean = str(sk_name).strip()
            if not sk_clean:
                continue
            cat_item = db.query(SkillCatalog).filter(SkillCatalog.skill_name.ilike(sk_clean)).first()
            if not cat_item:
                cat_item = SkillCatalog(
                    skill_name=sk_clean,
                    industry=major,
                    demand_pct=75.0,
                    supply_pct=60.0,
                    gap_pct=15.0,
                    trend_pct="+12%"
                )
                db.add(cat_item)
                db.commit()
                db.refresh(cat_item)

            db.add(SurveySkillRating(
                survey_id=survey.id,
                skill_id=cat_item.id,
                self_rating=85
            ))
        db.commit()

        res["survey_id"] = survey.id
        res["student_code"] = survey.student_code
        res["completed_at"] = completed_date.isoformat()
        res["major"] = major
        logger.info(f"Successfully saved candidate CV '{cand_name}' (ID: {survey.id}, Code: {student_code}) to 2026 database!")
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving CV to database: {e}")

class CVAnalyzeRequest(BaseModel):
    cv_text: str
    target_role: Optional[str] = "auto"
    previous_role: Optional[str] = "auto"
    industry: Optional[str] = "auto"

def auto_detect_candidate_profile(cv_text: str) -> Dict[str, str]:
    """
    AI tự động trích xuất Tên, Chức danh hiện tại/trước đây, và Đề xuất chức vụ mục tiêu tối ưu.
    """
    lines = [l.strip() for l in cv_text.splitlines() if l.strip()]
    cv_lower = cv_text.lower()

    # 1. Trích xuất Họ và Tên
    name = ""
    name_match = re.search(r"(?:họ\s*(?:và|&)?\s*tên|họ\s*tên|name|full\s*name)\s*[:\-]\s*([A-ZÀ-Ỹa-zà-ỹ\s]+)", cv_text, re.IGNORECASE)
    if name_match:
        cand = name_match.group(1).strip().splitlines()[0].strip()
        if 2 <= len(cand.split()) <= 6 and not any(k in cand.lower() for k in ["cv", "curriculum", "hồ sơ", "chức vụ", "vị trí", "kinh nghiệm"]):
            name = cand

    if not name and lines:
        for line in lines[:8]:
            clean_l = re.sub(r"^(cv|curriculum vitae|hồ sơ xin việc|sơ yếu lý lịch)[\s:\-]*", "", line, flags=re.IGNORECASE).strip()
            words = clean_l.split()
            if 2 <= len(words) <= 5 and all(w.replace("-", "").isalpha() for w in words) and len(clean_l) < 35:
                if not any(k in clean_l.lower() for k in ["kinh nghiệm", "kỹ năng", "học vấn", "mục tiêu", "thông tin", "liên hệ", "chức vụ", "vị trí"]):
                    name = clean_l
                    break
    if not name:
        name = "Ứng Viên"

    # 2. Tự động nhận diện Chức danh hiện tại / Chức vụ trước đây
    prev_role = ""
    role_match = re.search(r"(?:vị\s*trí\s*(?:hiện\s*tại|lúc\s*trước|cũ)?|chức\s*vụ(?:\s*trước|\s*hiện\s*tại)?|chức\s*danh)\s*[:\-]\s*([^\n\r,]+)", cv_text, re.IGNORECASE)
    if role_match:
        r = role_match.group(1).strip()
        if len(r) > 2 and len(r) < 60:
            prev_role = r

    if not prev_role:
        if any(k in cv_lower for k in ["thực tập sinh kế toán", "kế toán viên", "kế toán kho", "kế toán nội bộ"]):
            prev_role = "Thực tập sinh Kế toán"
        elif any(k in cv_lower for k in ["thực tập sinh it", "lập trình viên", "web developer", "developer", "backend"]):
            prev_role = "Thực tập sinh Lập trình"
        elif any(k in cv_lower for k in ["thực tập sinh xuất nhập khẩu", "logistics", "kho vận", "giao nhận"]):
            prev_role = "Thực tập sinh Kho vận & Logistics"
        elif any(k in cv_lower for k in ["hướng dẫn viên", "khách sạn", "lễ tân"]):
            prev_role = "Nhân viên Dịch vụ Du lịch"
        elif any(k in cv_lower for k in ["sinh viên", "đại học cần thơ", "tốt nghiệp"]):
            prev_role = "Sinh viên mới tốt nghiệp"
        else:
            prev_role = "Thực tập sinh"

    # 3. Tự động xác định hoặc đề xuất Chức vụ mục tiêu phù hợp nhất
    target_role = ""
    target_match = re.search(r"(?:mục\s*tiêu\s*(?:nghề\s*nghiệp)?|vị\s*trí\s*ứng\s*tuyển|hướng\s*tới|career\s*objective)\s*[:\-]\s*([^\n\r,]+)", cv_text, re.IGNORECASE)
    if target_match:
        t = target_match.group(1).strip()
        for valid_role in STANDARD_ROLE_PROFILES.keys():
            if valid_role.lower() in t.lower():
                target_role = valid_role
                break

    if not target_role:
        # Tự động suy luận từ các từ khóa kỹ năng và ngành
        if any(k in cv_lower for k in ["kế toán", "misa", "báo cáo tài chính", "thuế", "fast", "sổ sách", "hạch toán"]):
            if "phân tích tài chính" in cv_lower or "power bi" in cv_lower:
                target_role = "Chuyên Viên Phân Tích Tài Chính"
            elif "thuế" in cv_lower and "quyết toán" in cv_lower:
                target_role = "Kế Toán Thuế & Báo Cáo"
            else:
                target_role = "Kế Toán Tổng Hợp"
        elif any(k in cv_lower for k in ["python", "sql", "fastapi", "docker", "javascript", "developer", "lập trình"]):
            if "data" in cv_lower or "thống kê" in cv_lower:
                target_role = "Data Analyst"
            else:
                target_role = "Python Developer"
        elif any(k in cv_lower for k in ["logistics", "xuất nhập khẩu", "hải quan", "incoterms", "kho vận"]):
            target_role = "Chuyên Viên Xuất Nhập Khẩu"
        elif any(k in cv_lower for k in ["du lịch", "hướng dẫn", "tour", "khách sạn"]):
            target_role = "Hướng Dẫn Viên Du Lịch"
        else:
            target_role = "Kế Toán Tổng Hợp"

    return {
        "candidate_name": name,
        "previous_role": prev_role,
        "target_role": target_role
    }

def fallback_local_analyzer(cv_text: str, target_role: str = "auto", previous_role: str = "auto") -> Dict[str, Any]:
    """Phân tích CV tự động theo chuẩn kỹ năng ESCO."""
    detected_info = auto_detect_candidate_profile(cv_text)
    
    if not target_role or target_role == "auto":
        target_role = detected_info["target_role"]
    if not previous_role or previous_role == "auto":
        previous_role = detected_info["previous_role"]
    candidate_name = detected_info["candidate_name"]

    profile = STANDARD_ROLE_PROFILES.get(target_role, STANDARD_ROLE_PROFILES["Kế Toán Tổng Hợp"])
    req_skills = profile["reqSkills"]
    
    cv_lower = cv_text.lower()
    matched = []
    for sk in req_skills:
        if sk.lower() in cv_lower or (sk == "MISA" and "phần mềm kế toán" in cv_lower):
            matched.append(sk)
            
    all_vocab = [
        "Excel", "Word", "PowerPoint", "Tiếng Anh", "Giao tiếp", "Làm việc nhóm",
        "Kế toán", "Báo cáo tài chính", "Thuế", "MISA", "FAST", "Kiểm toán", "Phân tích tài chính",
        "Python", "SQL", "Git", "Docker", "FastAPI", "ReactJS",
        "Logistics", "Xuất nhập khẩu", "Nghiệp vụ hải quan", "SAP", "Incoterms 2020",
        "Hướng dẫn du lịch", "Customer Service", "Quản lý khách sạn"
    ]
    detected_all = [v for v in all_vocab if v.lower() in cv_lower]
    for m in matched:
        if m not in detected_all:
            detected_all.append(m)

    missing = [sk for sk in req_skills if sk not in matched]
    match_pct = int((len(matched) / len(req_skills)) * 100) if req_skills else 50

    roadmap = [
        {
            "phase": "Giai đoạn 1: Nền tảng kỹ năng cốt lõi (Tuần 1 – Tuần 2)",
            "goal": f"Khắc phục trực tiếp lỗ hổng kỹ năng cơ bản: {missing[0] if missing else 'Củng cố nghiệp vụ nâng cao'}",
            "actions": [
                f"Hoàn thành chuyên đề thực hành về {missing[0]}" if missing else "Thực hành bài tập tình huống thực tế tại doanh nghiệp",
                "Nghiên cứu quy chuẩn, văn bản nghiệp vụ áp dụng tại vùng ĐBSCL / Cần Thơ"
            ],
            "course": profile["courses"].get(missing[0], {"title": f"Chuyên đề {missing[0]}", "src": "ĐH Cần Thơ (CTU)", "dur": "2 tuần", "price": "Miễn phí", "url": "https://ctu.edu.vn"}) if missing else None
        },
        {
            "phase": "Giai đoạn 2: Nâng cao thực chiến & Công cụ số (Tuần 3 – Tuần 5)",
            "goal": f"Nắm vững kỹ năng: {missing[1] if len(missing) > 1 else 'Nâng cao năng suất và giải quyết bài toán phức tạp'}",
            "actions": [
                f"Thực hành với số liệu thực tế trên phần mềm và công cụ liên quan đến {missing[1] if len(missing) > 1 else 'chuyên môn'}",
                "Xây dựng dự án mẫu / bộ hồ sơ nghiệp vụ hoàn chỉnh đưa vào Portfolio cá nhân"
            ],
            "course": profile["courses"].get(missing[1], {"title": f"Kỹ năng nâng cao {missing[1]}", "src": "Viện PACE / VCCI Cần Thơ", "dur": "3 tuần", "price": "1.2tr", "url": "https://pace.edu.vn"}) if len(missing) > 1 else None
        },
        {
            "phase": "Giai đoạn 3: Tối ưu hồ sơ & Sẵn sàng thăng tiến (Tuần 6 – Tuần 8)",
            "goal": f"Chuyển tiếp thành công từ '{previous_role}' lên vị trí mục tiêu '{target_role}'",
            "actions": [
                "Cập nhật CV với các chứng chỉ mới đạt được và dự án thực hành hoàn thành",
                "Luyện tập trả lời phỏng vấn các câu hỏi tình huống chuyên môn theo chuẩn tuyển dụng"
            ],
            "course": {"title": "Luyện Phỏng Vấn & Định Hướng Nghề Nghiệp", "src": "Trung Tâm Hỗ Trợ Sinh Viên CTU", "dur": "1 tuần", "price": "Miễn phí", "url": "https://ctu.edu.vn"}
        }
    ]

    return {
        "ai_engine": "SkillGap Intelligent ESCO Engine (Auto-Analyzed)",
        "candidate_name": candidate_name,
        "previous_role": previous_role,
        "target_role": target_role,
        "match_percentage": match_pct,
        "all_detected_skills": detected_all,
        "matched_skills": matched,
        "missing_skills": missing,
        "ai_assessment": (
            f"AI đã tự động phân tích CV của {candidate_name}. "
            f"Từ kinh nghiệm/nền tảng '{previous_role}', hồ sơ đã tích lũy tốt các kỹ năng ({', '.join(matched) if matched else 'kỹ năng cơ bản'}). "
            f"Vị trí mục tiêu tối ưu đề xuất là '{target_role}' với mức độ sẵn sàng hiện tại đạt {match_pct}%. "
            f"Để thăng tiến vững chắc, khoảng cách lớn nhất cần bổ sung là: {', '.join(missing) if missing else 'hoàn thiện chứng chỉ nghiệp vụ'}. "
            f"Lộ trình 3 giai đoạn dưới đây được AI thiết kế riêng để bù đắp toàn diện lỗ hổng này."
        ),
        "learning_roadmap": roadmap
    }

def call_multi_provider_llm_analyzer(cv_text: str) -> Optional[Dict[str, Any]]:
    """
    Hệ thống phân tích CV đa tầng:
    1. Ưu tiên Google Gemini Cloud API.
    2. Nếu Gemini hết hạn / lỗi 403 / giới hạn quota -> Tự động chuyển đổi mượt mà sang Groq Cloud LLM (Qwen 27B / GPT 120B).
    3. Nếu cả 2 đều không phản hồi -> Trả về None để kích hoạt Local ESCO NLP Engine.
    """
    import httpx
    prompt = f"""
Bạn là Giám đốc Thẩm định CV & Đào tạo Nhân sự hàng đầu (theo tiêu chuẩn kỹ năng ESCO và thị trường Cần Thơ).
Nhiệm vụ của bạn là TỰ ĐỘNG PHÂN TÍCH TOÀN BỘ CV dưới đây mà người dùng không cần khai báo bất cứ thông tin nào:

[NỘI DUNG CV]:
\"\"\"{cv_text}\"\"\"

[YÊU CẦU TỰ ĐỘNG]:
1. "candidate_name": Tìm chính xác Họ và Tên ứng viên trong CV.
2. "previous_role": Tự động nhận diện Chức danh / Kinh nghiệm hiện tại hoặc gần nhất của ứng viên (ví dụ: 'Thực tập sinh Kế toán', 'Lập trình viên thực tập', 'Nhân viên kinh doanh'...).
3. "target_role": Tự động đề xuất Vị trí mục tiêu thăng tiến phù hợp nhất cho ứng viên (ví dụ: 'Kế Toán Tổng Hợp', 'Python Developer', 'Chuyên Viên Xuất Nhập Khẩu'...).
4. "match_percentage": Mức độ đáp ứng hiện tại (0 - 100%) so với vị trí target_role đó.
5. "all_detected_skills": Toàn bộ kỹ năng AI nhận diện được trong CV.
6. "matched_skills": Các kỹ năng ứng viên đã có đáp ứng yêu cầu của target_role.
7. "missing_skills": Các kỹ năng quan trọng còn thiếu đối với target_role.
8. "ai_assessment": Nhận xét sâu sắc từ 3-4 câu về điểm mạnh, hạn chế và tiềm năng của ứng viên.
9. "learning_roadmap": Lộ trình học 3 giai đoạn bù đắp kỹ năng còn thiếu.

Hãy trả về DUY NHẤT một chuỗi JSON hợp lệ theo định dạng sau (không markdown giải thích):
{{
  "candidate_name": "Họ và tên ứng viên",
  "previous_role": "Vị trí nhận diện được",
  "target_role": "Vị trí mục tiêu đề xuất",
  "match_percentage": 65,
  "all_detected_skills": ["kỹ năng 1", "kỹ năng 2"],
  "matched_skills": ["kỹ năng đã đáp ứng"],
  "missing_skills": ["kỹ năng còn thiếu"],
  "ai_assessment": "Nhận xét chuyên môn...",
  "learning_roadmap": [
    {{
      "phase": "Giai đoạn 1: ...",
      "goal": "Mục tiêu cụ thể",
      "actions": ["hành động 1", "hành động 2"],
      "course": {{"title": "Tên khóa học", "src": "Đơn vị đào tạo", "dur": "Thời gian", "price": "Học phí", "url": "#"}}
    }}
  ]
}}
"""
    # ── 1. Thử gọi Google Gemini Cloud API trước ──
    if GEMINI_API_KEY and len(GEMINI_API_KEY) > 10:
        gemini_models = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-flash-latest", "gemini-pro-latest"]
        for gm in gemini_models:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{gm}:generateContent?key={GEMINI_API_KEY}"
                payload = {"contents": [{"parts": [{"text": prompt}]}]}
                with httpx.Client(timeout=15.0) as client:
                    resp = client.post(url, json=payload)
                    if resp.status_code == 200:
                        raw = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                        if raw.startswith("```"):
                            raw = re.sub(r"^```(?:json)?", "", raw)
                            raw = re.sub(r"```$", "", raw).strip()
                        parsed = json.loads(raw)
                        parsed["ai_engine"] = f"Google Gemini AI ({gm} - Cloud API)"
                        logger.info(f"Gemini {gm} analysis completed successfully")
                        return parsed
                    else:
                        logger.warning(f"Gemini {gm} returned HTTP {resp.status_code}: {resp.text[:120]}")
            except Exception as ge:
                logger.warning(f"Gemini {gm} error: {ge}")

    # ── 2. Nếu Gemini hết quota / lỗi billing 403, tự động chuyển sang Groq Cloud AI ──
    if GROQ_API_KEY and len(GROQ_API_KEY) > 10:
        groq_models = ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"]
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        for qm in groq_models:
            try:
                payload = {
                    "model": qm,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2
                }
                with httpx.Client(timeout=20.0) as client:
                    resp = client.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)
                    if resp.status_code == 200:
                        raw = resp.json()["choices"][0]["message"]["content"].strip()
                        if raw.startswith("```"):
                            raw = re.sub(r"^```(?:json)?", "", raw)
                            raw = re.sub(r"```$", "", raw).strip()
                        parsed = json.loads(raw)
                        parsed["ai_engine"] = f"Groq Cloud AI ({qm} - Siêu Tốc)"
                        logger.info(f"Groq {qm} analysis completed successfully")
                        return parsed
                    else:
                        logger.warning(f"Groq {qm} returned HTTP {resp.status_code}: {resp.text[:120]}")
            except Exception as qe:
                logger.warning(f"Groq {qm} error: {qe}")

    return None

@router.post("/analyze")
async def analyze_cv(
    payload: CVAnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Tự động phân tích toàn diện CV bằng Gemini AI + Groq Cloud LLM kết hợp ESCO Engine.
    Hỗ trợ cả người dùng vãng lai (Public) lẫn người dùng đã đăng nhập (Candidate).
    Nếu đã đăng nhập, tự động lưu kết quả phân tích vào hồ sơ cá nhân.
    """
    cv_text = payload.cv_text.strip()
    if not cv_text:
        raise HTTPException(status_code=400, detail="Nội dung CV không được để trống")

    # Gọi AI đa tầng: Gemini -> Groq -> Local ESCO Fallback
    llm_result = call_multi_provider_llm_analyzer(cv_text)
    final_res = llm_result if llm_result else fallback_local_analyzer(cv_text, payload.target_role or "auto", payload.previous_role or "auto")

    # Lưu snapshot CV cho người dùng đã đăng nhập
    if current_user and isinstance(final_res, dict):
        final_res["user_id"] = current_user.id
        try:
            current_user.latest_cv_analysis = json.dumps(final_res, ensure_ascii=False)
            db.commit()
            logger.info(f"Saved latest_cv_analysis for user #{current_user.id}")
        except Exception as save_err:
            logger.warning(f"Failed to save CV snapshot: {save_err}")

    # Lưu trực tiếp vào Database của năm 2026 (bảng survey_responses & survey_skill_ratings)
    save_cv_to_database(db, final_res, current_user)

    return final_res

@router.post("/upload")
async def upload_cv_file(
    file: UploadFile = File(...),
    target_role: Optional[str] = Form("auto"),
    previous_role: Optional[str] = Form("auto"),
    cv_text: Optional[str] = Form(""),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Nhận file CV tải lên (Ảnh chụp CV: PNG, JPG, JPEG, WEBP hoặc PDF, TXT) và TỰ ĐỘNG PHÂN TÍCH.
    """
    content_bytes = await file.read()
    filename = file.filename.lower()
    
    is_image = any(filename.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".webp"])
    mime_type = "image/png" if filename.endswith(".png") else "image/webp" if filename.endswith(".webp") else "image/jpeg"

    # A. Nếu là file ảnh, thử trực tiếp qua Gemini Vision với Prompt tự động nhận diện
    if is_image and GEMINI_API_KEY and len(GEMINI_API_KEY) > 10:
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=GEMINI_API_KEY)
            prompt = """
Bạn là Giám đốc Thẩm định Nhân sự AI cao cấp. 
Hãy đọc TOÀN BỘ văn bản từ bức ảnh chụp CV này và TỰ ĐỘNG PHÂN TÍCH TOÀN DIỆN mà KHÔNG CẦN người dùng khai báo gì:
1. "candidate_name": Tìm chính xác Họ và Tên ứng viên trong ảnh CV.
2. "previous_role": Nhận diện Chức danh / Kinh nghiệm hiện tại hoặc gần nhất của ứng viên từ ảnh CV (ví dụ: 'Thực tập sinh Kế toán', 'Junior Web Developer', 'Sinh viên ngành Logistics'...).
3. "target_role": Tự động đề xuất Vị trí mục tiêu thăng tiến phù hợp nhất cho ứng viên dựa trên chuyên môn trong CV (ví dụ: 'Kế Toán Tổng Hợp', 'Python Developer', 'Chuyên Viên Xuất Nhập Khẩu'...).
4. "match_percentage": Mức độ sẵn sàng (0 - 100%) cho vị trí target_role.
5. "all_detected_skills": Tất cả kỹ năng đọc được trong CV.
6. "matched_skills": Kỹ năng ứng viên đã có đáp ứng yêu cầu target_role.
7. "missing_skills": Kỹ năng còn thiếu ứng viên cần học để đạt target_role.
8. "ai_assessment": Nhận xét sâu sắc từ 3-4 câu về CV.
9. "learning_roadmap": Lộ trình học 3 giai đoạn kèm khóa học uy tín để đạt target_role.

Hãy trả về duy nhất chuỗi JSON (không kèm markdown):
{
  "candidate_name": "Họ và tên trong ảnh",
  "previous_role": "Vị trí nhận diện từ ảnh",
  "target_role": "Vị trí mục tiêu tối ưu",
  "match_percentage": 65,
  "all_detected_skills": ["kỹ năng 1", "kỹ năng 2"],
  "matched_skills": ["kỹ năng đã đáp ứng"],
  "missing_skills": ["kỹ năng còn thiếu"],
  "ai_assessment": "Nhận xét chuyên sâu...",
  "learning_roadmap": [
    {
      "phase": "Giai đoạn 1: ...",
      "goal": "Mục tiêu cụ thể",
      "actions": ["hành động 1", "hành động 2"],
      "course": {"title": "Tên khóa học", "src": "Đơn vị đào tạo", "dur": "Thời gian", "price": "Học phí", "url": "#"}
    }
  ]
}
"""
            models_to_try = ["gemini-3.1-flash-lite", "gemini-3.5-flash-lite"]
            for m in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=m,
                        contents=[
                            types.Part.from_bytes(data=content_bytes, mime_type=mime_type),
                            prompt
                        ]
                    )
                    raw_text = response.text.strip()
                    if raw_text.startswith("```"):
                        raw_text = re.sub(r"^```(?:json)?", "", raw_text)
                        raw_text = re.sub(r"```$", "", raw_text).strip()
                    res_json = json.loads(raw_text)
                    res_json["ai_engine"] = f"Google Gemini AI ({m} Vision - Trực Tiếp Từ Google Cloud)"
                    logger.info(f"Gemini vision model {m} completed successfully")
                    return res_json
                except Exception as vis_err:
                    logger.warning(f"Gemini vision model {m} failed: {vis_err}")
        except Exception as e:
            logger.warning(f"Gemini vision error: {e}. Falling back to Tesseract OCR.")

    # B. Nếu là ảnh và Gemini Cloud không kết nối được -> Dùng Tesseract OCR đọc chữ thực tế
    extracted_text = ""
    if is_image:
        try:
            import io
            from PIL import Image
            import pytesseract
            img = Image.open(io.BytesIO(content_bytes))
            if img.width > 2200 or img.height > 2200:
                img.thumbnail((2200, 2200))
            extracted_text = pytesseract.image_to_string(img, lang="vie+eng").strip()
            logger.info(f"Tesseract OCR extracted {len(extracted_text)} chars from {file.filename}")
        except Exception as ocr_err:
            logger.warning(f"Tesseract OCR failed: {ocr_err}")

    if not extracted_text:
        if filename.endswith(".pdf"):
            try:
                import io
                from pypdf import PdfReader
                reader = PdfReader(io.BytesIO(content_bytes))
                pdf_texts = []
                for page in reader.pages:
                    t = page.extract_text()
                    if t:
                        pdf_texts.append(t)
                extracted_text = "\n".join(pdf_texts).strip()
                logger.info(f"PdfReader extracted {len(extracted_text)} chars from {file.filename}")
            except Exception as pdf_err:
                logger.warning(f"PDF extraction failed: {pdf_err}")
        elif not is_image:
            try:
                extracted_text = content_bytes.decode("utf-8", errors="ignore").strip()
            except Exception:
                pass

    final_text = extracted_text if extracted_text else (cv_text or "Hồ sơ ứng viên")
    llm_res = call_multi_provider_llm_analyzer(final_text)
    res = llm_res if llm_res else fallback_local_analyzer(final_text, target_role="auto", previous_role="auto")
    if is_image and not llm_res:
        res["ai_engine"] = "AI Vision OCR & ESCO SkillGap Engine (Tự Động Phân Tích)"

    if current_user and isinstance(res, dict):
        res["user_id"] = current_user.id
        try:
            current_user.latest_cv_analysis = json.dumps(res, ensure_ascii=False)
            db.commit()
            logger.info(f"Saved latest_cv_analysis for user #{current_user.id} from upload")
        except Exception as save_err:
            logger.warning(f"Failed to save CV snapshot: {save_err}")

    # Lưu trực tiếp vào Database của năm 2026 (bảng survey_responses & survey_skill_ratings)
    save_cv_to_database(db, res, current_user)

    return res


@router.get("/my-snapshot")
def get_my_cv_snapshot(current_user: User = Depends(get_current_user)):
    """Lấy lại kết quả phân tích CV gần nhất của ứng viên đã đăng nhập."""
    if not current_user.latest_cv_analysis:
        raise HTTPException(status_code=404, detail="Bạn chưa có bản lưu kết quả phân tích CV nào")
    try:
        return json.loads(current_user.latest_cv_analysis)
    except Exception:
        return {"raw": current_user.latest_cv_analysis}
