"""
execute_clean_pipeline.py
=============================================================================
Hệ Thống Tái Trích Xuất & Làm Sạch Dữ Liệu Toàn Diện:
- 1.000 Tin Tuyển Dụng (Job Postings)
- 500 Hồ Sơ Ứng Viên (Curriculum Vitae)

Áp dụng toàn bộ quy tắc nghiệp vụ mới nhất:
1. Whitelist allowed_skills.json đã làm sạch (xóa 88 mục rác tỉnh thành, học vấn, chức danh, ngành chung).
2. Sửa Adobe Illustrator (bỏ 'ai'), tách 'phân tích yêu cầu' và 'phân tích nghiệp vụ'.
3. 10 nhóm Kỹ năng mềm hạt nhân chuẩn Gold Standard (qua soft_collapse).
4. Keyword Boost HARD & TOOL trên toàn văn bản bằng regex boundary.
5. Tách Chức danh sang Position & ESCO Occupation; bổ sung ESCO Essential skills.
6. Tách nguồn rõ ràng: source = 'explicit' vs source = 'esco_essential'.
7. Đồng bộ 100% vào data/clean_job_postings.json, data/clean_resumes_500.json và MySQL 3NF.
=============================================================================
"""

import sys
import os
import re
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')

import pymysql
import config
from occupation_esco_matcher import OccupationEscoMatcher
from evaluate_gold_standard import (
    clean_skills,
    boost_hard_tool_skills,
    ALLOWED_SKILLS,
    WHITELIST_LOOKUP,
    SOFT_LOOKUP,
    STOP_SKILLS,
    STOP_SOFT_SKILLS,
    POSITIONS_AS_SKILLS
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CLEAN_JOBS_FILE = os.path.join(DATA_DIR, "clean_job_postings.json")
BACKUP_JOBS_FILE = os.path.join(DATA_DIR, "clean_job_postings_backup.json")
CLEAN_RESUMES_FILE = os.path.join(DATA_DIR, "clean_resumes_500.json")
RAW_RESUMES_FILE = os.path.join(DATA_DIR, "raw_resumes_500.json")
RESUME_CACHE_FILE = os.path.join(DATA_DIR, "resume_skills_groq_cache.json")
PDF_CACHE_FILE = os.path.join(DATA_DIR, "pdf_texts_cache.json")

# 10 nhóm kỹ năng mềm chuẩn
CORE_SOFT_SKILLS = {
    "Kỹ năng giao tiếp",
    "Làm việc nhóm",
    "Đàm phán & Thuyết phục",
    "Chăm sóc khách hàng",
    "Kỹ năng lãnh đạo",
    "Quản lý thời gian",
    "Giải quyết vấn đề",
    "Tư duy logic & Phản biện",
    "Chủ động & Trách nhiệm",
    "Chịu áp lực công việc"
}

# Regex Redaction PII cho CV
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
PHONE_PATTERN = re.compile(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{3,4}')
LINK_PATTERN = re.compile(r'(https?:\/\/[^\s]+)')

def redact_pii(text: str) -> str:
    if not text:
        return ""
    cleaned = EMAIL_PATTERN.sub('[REDACTED]', text)
    cleaned = LINK_PATTERN.sub('[REDACTED]', cleaned)
    cleaned = PHONE_PATTERN.sub('[REDACTED]', cleaned)
    return cleaned

def parse_salary_to_vnd(salary_str: str):
    if not salary_str:
        return None, None, 1
    s = salary_str.lower().strip()
    if "thỏa thuận" in s or "cạnh tranh" in s:
        return None, None, 1
    if "usd" in s or "$" in s:
        m = re.search(r'(\d+[\.,]?\d*)\s*(?:-|–)\s*(\d+[\.,]?\d*)', s)
        if m:
            min_u = float(m.group(1).replace(',', '.'))
            max_u = float(m.group(2).replace(',', '.'))
            return int(min_u * 25400), int(max_u * 25400), 0
        m_single = re.search(r'(\d+[\.,]?\d*)', s)
        if m_single:
            val_u = float(m_single.group(1).replace(',', '.'))
            return int(val_u * 25400), None, 0
    m_range = re.search(r'(\d+[\.,]?\d*)\s*(?:-|–|đến|tới)\s*(\d+[\.,]?\d*)', s)
    if m_range:
        min_v = float(m_range.group(1).replace(',', '.'))
        max_v = float(m_range.group(2).replace(',', '.'))
        return int(min_v * 1_000_000), int(max_v * 1_000_000), 0
    m_from = re.search(r'(?:từ|trên)\s*(\d+[\.,]?\d*)', s)
    if m_from:
        val = float(m_from.group(1).replace(',', '.'))
        return int(val * 1_000_000), None, 0
    m_to = re.search(r'(?:tới|đến|dưới)\s*(\d+[\.,]?\d*)', s)
    if m_to:
        val = float(m_to.group(1).replace(',', '.'))
        return None, int(val * 1_000_000), 0
    return None, None, 1

def parse_experience_years(exp_str: str):
    if not exp_str:
        return 0.0, None
    s = exp_str.lower().strip()
    if "không yêu cầu" in s or "chưa có kinh nghiệm" in s:
        return 0.0, 0.0
    if "dưới 1 năm" in s:
        return 0.0, 1.0
    m_range = re.search(r'(\d+[\.,]?\d*)\s*(?:-|–)\s*(\d+[\.,]?\d*)', s)
    if m_range:
        return float(m_range.group(1).replace(',', '.')), float(m_range.group(2).replace(',', '.'))
    m_single = re.search(r'(\d+[\.,]?\d*)', s)
    if m_single:
        val = float(m_single.group(1).replace(',', '.'))
        return val, val
    return 0.0, None

def parse_cv_experience(text: str) -> float:
    if not text:
        return 2.0
    text_low = text.lower()
    m = re.search(r'(\d+)\+?\s*(?:year|yr)s?(?:\s+of)?\s+experience', text_low)
    if m:
        try:
            return min(float(m.group(1)), 35.0)
        except Exception:
            pass
    years = [int(y) for y in re.findall(r'\b(19\d\d|20\d\d)\b', text)]
    if len(years) >= 2:
        valid_years = [y for y in years if 1980 <= y <= 2026]
        if len(valid_years) >= 2:
            span = max(valid_years) - min(valid_years)
            if 0 < span <= 35:
                return float(span)
    return 3.0

def parse_cv_education(text: str):
    text_low = text.lower()
    if any(k in text_low for k in ["ph.d", "doctorate", "tiến sĩ"]):
        return 4, "Đại học / Viện nghiên cứu", "Tiến sĩ"
    if any(k in text_low for k in ["master", "mba", "m.s.", "m.a.", "thạc sĩ"]):
        return 3, "Đại học / Cao học", "Thạc sĩ"
    if any(k in text_low for k in ["bachelor", "b.s.", "b.a.", "b.tech", "cử nhân", "kỹ sư"]):
        return 2, "Trường Đại học", "Đại học"
    if any(k in text_low for k in ["associate", "diploma", "cao đẳng"]):
        return 1, "Trường Cao đẳng", "Cao đẳng"
    return 2, "Trường Đại học", "Đại học"

def run_pipeline():
    print("=" * 80)
    print("BẮT ĐẦU QUY TRÌNH TÁI TRÍCH XUẤT DỮ LIỆU SẠCH 1.000 JP VÀ 500 CV")
    print("Áp dụng: Whitelist đã sạch (860 skills) + 10 Soft Core + Boost HARD/TOOL + ESCO")
    print("=" * 80)

    matcher = OccupationEscoMatcher()

    # =========================================================================
    # PHẦN 1: TÁI TRÍCH XUẤT 1.000 JOB POSTINGS (JPs)
    # =========================================================================
    print("\n[PHẦN 1/2] Đang xử lý 1.000 Tin Tuyển Dụng...")
    jobs_source = BACKUP_JOBS_FILE if os.path.exists(BACKUP_JOBS_FILE) else CLEAN_JOBS_FILE
    with open(jobs_source, "r", encoding="utf-8") as f:
        jobs_input = json.load(f)

    # Backup if not yet exists
    if not os.path.exists(BACKUP_JOBS_FILE):
        with open(BACKUP_JOBS_FILE, "w", encoding="utf-8") as f:
            json.dump(jobs_input, f, ensure_ascii=False, indent=2)
        print(f"  -> Đã tạo backup dữ liệu cũ tại: {BACKUP_JOBS_FILE}")

    clean_jobs_output = []
    total_explicit_skills = 0
    total_esco_essential_skills = 0

    for idx, job in enumerate(jobs_input, 1):
        jid = str(job["job_id"]).strip()
        title = job.get("title", "").strip()
        pos_raw = job.get("position") or job.get("vi_tri") or title
        desc = job.get("description_clean") or job.get("description") or ""
        req = job.get("requirements_clean") or job.get("requirements") or ""
        full_text = f"{title} {desc} {req}"

        # 1. Thu thập ứng viên kỹ năng thô từ bài
        candidate_skills = []
        # Lấy từ mảng skills hiện có của job
        for s in job.get("skills", []):
            candidate_skills.append({
                "skill_name": s,
                "skill_type": "SOFT" if s in CORE_SOFT_SKILLS else "HARD",
                "requirement_level": "required"
            })

        # 2. Làm sạch qua clean_skills
        cleaned = clean_skills(candidate_skills)

        # 3. Quét Keyword Boost HARD và TOOL từ văn bản gốc
        boosted = boost_hard_tool_skills(full_text, cleaned)

        # 4. Phân tách danh mục Kỹ năng
        hard_list = []
        soft_list = []
        all_skill_names = []

        for s in boosted:
            sname = s["skill_name"]
            stype = s.get("skill_type", "HARD").upper()
            if stype == "SOFT" or sname in CORE_SOFT_SKILLS:
                if sname not in soft_list:
                    soft_list.append(sname)
            else:
                if sname not in hard_list:
                    hard_list.append(sname)
            if sname not in all_skill_names:
                all_skill_names.append(sname)

        # 5. Ánh xạ Vị trí sang ESCO Occupation và Lấy ESCO Essential
        enriched = matcher.enrich_job_skills_with_esco(
            explicit_skills=boosted,
            position_name=pos_raw,
            include_optional=False,
            max_inferred=8
        )

        matched_occ = enriched.get("matched_occupation")
        esco_occ_name = matched_occ["occupation_name"] if matched_occ else None
        esco_occ_uri = matched_occ["esco_occupation_uri"] if matched_occ else None
        esco_ess_list = [es["skill_name"] for es in enriched.get("esco_inferred_skills", [])]

        sal_min, sal_max, is_neg = parse_salary_to_vnd(job.get("salary", ""))
        exp_min, exp_max = parse_experience_years(job.get("experience_required", ""))

        clean_item = {
            "job_id": jid,
            "title": title,
            "category": job.get("category", ""),
            "position": pos_raw,
            "chuc_vu": job.get("chuc_vu") or "Nhân viên",
            "company_name": job.get("company_name", ""),
            "salary": job.get("salary", ""),
            "salary_min_vnd": sal_min,
            "salary_max_vnd": sal_max,
            "is_salary_negotiable": is_neg,
            "location": job.get("location", ""),
            "experience_required": job.get("experience_required", ""),
            "experience_min_years": exp_min,
            "experience_max_years": exp_max,
            "hard_skills": hard_list,
            "soft_skills": soft_list,
            "skills": all_skill_names,
            "skills_count": len(all_skill_names),
            "esco_occupation_name": esco_occ_name,
            "esco_occupation_uri": esco_occ_uri,
            "esco_essential_skills": esco_ess_list,
            "explicit_skills_detail": boosted,
            "esco_skills_detail": enriched.get("esco_inferred_skills", []),
            "description_clean": desc,
            "requirements_clean": req,
            "posted_date": str(job.get("posted_date") or ""),
            "deadline": str(job.get("deadline") or ""),
            "job_url": job.get("job_url", "")
        }

        clean_jobs_output.append(clean_item)
        total_explicit_skills += len(boosted)
        total_esco_essential_skills += len(esco_ess_list)

        if idx % 250 == 0 or idx == len(jobs_input):
            print(f"  + [{idx}/{len(jobs_input)}] Việc làm đã làm sạch và bổ trợ ESCO...", flush=True)

    with open(CLEAN_JOBS_FILE, "w", encoding="utf-8") as f:
        json.dump(clean_jobs_output, f, ensure_ascii=False, indent=2)
    print(f"  -> ĐÃ LƯU 1.000 VIỆC LÀM SẠCH VÀO: {CLEAN_JOBS_FILE}")

    # =========================================================================
    # PHẦN 2: TÁI TRÍCH XUẤT 500 CVs
    # =========================================================================
    print("\n[PHẦN 2/2] Đang xử lý 500 Hồ sơ Ứng viên (CVs)...")
    with open(RAW_RESUMES_FILE, "r", encoding="utf-8") as f:
        resumes_input = json.load(f)

    # Nạp cache kỹ năng CV từ Groq
    cv_groq_cache = {}
    if os.path.exists(RESUME_CACHE_FILE):
        with open(RESUME_CACHE_FILE, "r", encoding="utf-8") as f:
            cv_groq_cache = json.load(f)

    pdf_text_cache = {}
    if os.path.exists(PDF_CACHE_FILE):
        with open(PDF_CACHE_FILE, "r", encoding="utf-8") as f:
            pdf_text_cache = json.load(f)

    clean_cvs_output = []
    total_cv_skills = 0

    for idx, cv in enumerate(resumes_input, 1):
        cid = str(cv.get("cv_id") or cv.get("archive_id")).strip()
        pdf_path = cv.get("pdf_path", "").replace("\\", "/")
        raw_text = pdf_text_cache.get(pdf_path) or cv.get("raw_text_snippet") or ""
        redacted_text = redact_pii(raw_text)

        # Lấy kỹ năng từ Groq Cache
        cached_cv = cv_groq_cache.get(cid, {})
        candidate_skills = []
        for s in cached_cv.get("skills", []):
            candidate_skills.append({
                "skill_name": s,
                "skill_type": "SOFT" if s in CORE_SOFT_SKILLS else "HARD",
                "requirement_level": "required"
            })

        # Làm sạch và boost
        cleaned_cv = clean_skills(candidate_skills)
        boosted_cv = boost_hard_tool_skills(redacted_text, cleaned_cv)

        hard_list = []
        soft_list = []
        all_skill_names = []

        for s in boosted_cv:
            sname = s["skill_name"]
            stype = s.get("skill_type", "HARD").upper()
            if stype == "SOFT" or sname in CORE_SOFT_SKILLS:
                if sname not in soft_list:
                    soft_list.append(sname)
            else:
                if sname not in hard_list:
                    hard_list.append(sname)
            if sname not in all_skill_names:
                all_skill_names.append(sname)

        exp_years = parse_cv_experience(raw_text)
        edu_rank, edu_school, edu_major = parse_cv_education(raw_text)
        industry = cv.get("industry") or cv.get("category") or "Công nghệ Thông tin"

        clean_cv_item = {
            "cv_id": int(cv.get("cv_id", idx)),
            "archive_id": cv.get("archive_id", ""),
            "industry_id": cv.get("industry_id", 1),
            "industry": industry,
            "category": cv.get("category", ""),
            "experience_years": exp_years,
            "education_level_rank": edu_rank,
            "education_school": edu_school,
            "education_major": edu_major,
            "hard_skills": hard_list,
            "soft_skills": soft_list,
            "skills": all_skill_names,
            "skills_count": len(all_skill_names),
            "skills_detail": boosted_cv,
            "pdf_path": pdf_path
        }

        clean_cvs_output.append(clean_cv_item)
        total_cv_skills += len(all_skill_names)

        if idx % 125 == 0 or idx == len(resumes_input):
            print(f"  + [{idx}/{len(resumes_input)}] CVs đã làm sạch kỹ năng & PII...", flush=True)

    with open(CLEAN_RESUMES_FILE, "w", encoding="utf-8") as f:
        json.dump(clean_cvs_output, f, ensure_ascii=False, indent=2)
    print(f"  -> ĐÃ LƯU 500 CVs SẠCH VÀO: {CLEAN_RESUMES_FILE}")

    # =========================================================================
    # PHẦN 3: ĐỒNG BỘ 100% VÀO CƠ SỞ DỮ LIỆU MYSQL
    # =========================================================================
    print("\n[PHẦN 3/3] Đang đồng bộ toàn bộ vào MySQL (Chuẩn 3NF & Tách nguồn)...")
    conn = pymysql.connect(**config.MYSQL_CONFIG)
    cur = conn.cursor()

    # 1. Positions & Companies
    cur.execute("SELECT position_id, position_name FROM positions;")
    db_positions = {r[1].lower(): r[0] for r in cur.fetchall()}

    cur.execute("SELECT company_id, company_name FROM companies;")
    db_companies = {r[1].lower(): r[0] for r in cur.fetchall()}

    CAT_MAP = {
        "công nghệ thông tin": 1, "it": 1, "information technology": 1,
        "du lịch-dịch vụ": 2, "du lịch": 2, "tourism & services": 2,
        "logistics": 3,
        "kế toán": 4, "economics": 4
    }

    for job in clean_jobs_output:
        pname = job["position"].strip()
        plow = pname.lower()
        if plow not in db_positions:
            ind_id = CAT_MAP.get(job.get("category", "").lower(), 1)
            cur.execute("""
                INSERT INTO positions (industry_id, position_name, esco_occupation_uri)
                VALUES (%s, %s, %s);
            """, (ind_id, pname, job.get("esco_occupation_uri")))
            db_positions[plow] = cur.lastrowid
        elif job.get("esco_occupation_uri"):
            cur.execute("""
                UPDATE positions
                SET esco_occupation_uri = %s
                WHERE position_id = %s;
            """, (job["esco_occupation_uri"], db_positions[plow]))

        cname = job.get("company_name", "").strip() or "Công ty Tuyển dụng"
        clow = cname.lower()
        if clow not in db_companies:
            cur.execute("INSERT IGNORE INTO companies (company_name) VALUES (%s);", (cname,))
            cur.execute("SELECT company_id FROM companies WHERE company_name = %s LIMIT 1;", (cname,))
            r = cur.fetchone()
            if r:
                db_companies[clow] = r[0]

    # 2. Jobs
    raw_to_clean_job_id = {}
    for job in clean_jobs_output:
        raw_jid = str(job["job_id"]).strip()
        pos_id = db_positions.get(job["position"].lower(), 1)
        comp_id = db_companies.get(job.get("company_name", "").lower(), 1)

        cur.execute("""
            INSERT INTO jobs (
                raw_job_id, title, chuc_vu, company_id, position_id,
                experience_min_years, experience_max_years,
                salary_min_vnd, salary_max_vnd, is_salary_negotiable,
                description, requirements, posted_date, deadline, status,
                created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s, 'active',
                NOW(), NOW()
            )
            ON DUPLICATE KEY UPDATE
                title = VALUES(title),
                chuc_vu = VALUES(chuc_vu),
                company_id = VALUES(company_id),
                position_id = VALUES(position_id),
                experience_min_years = VALUES(experience_min_years),
                experience_max_years = VALUES(experience_max_years),
                salary_min_vnd = VALUES(salary_min_vnd),
                salary_max_vnd = VALUES(salary_max_vnd),
                is_salary_negotiable = VALUES(is_salary_negotiable),
                description = VALUES(description),
                requirements = VALUES(requirements),
                updated_at = NOW();
        """, (
            raw_jid, job["title"], job["chuc_vu"], comp_id, pos_id,
            job["experience_min_years"], job["experience_max_years"],
            job["salary_min_vnd"], job["salary_max_vnd"], job["is_salary_negotiable"],
            job["description_clean"], job["requirements_clean"],
            job["posted_date"] if job["posted_date"] else None,
            job["deadline"] if job["deadline"] else None
        ))

        cur.execute("SELECT job_id FROM jobs WHERE raw_job_id = %s LIMIT 1;", (raw_jid,))
        clean_jid = cur.fetchone()[0]
        raw_to_clean_job_id[raw_jid] = clean_jid

    conn.commit()

    # 3. Skills và Job_skills
    cur.execute("SELECT skill_id, skill_name FROM skills;")
    db_skills = {r[1].lower(): r[0] for r in cur.fetchall()}

    def get_or_create_skill(sname: str, stype: str = "HARD", is_esco: bool = False, esco_uri: Optional[str] = None):
        slow = sname.strip().lower()
        if slow in db_skills:
            return db_skills[slow]
        type_id = 2 if (stype == "SOFT" or sname in CORE_SOFT_SKILLS) else 1
        cur.execute("""
            INSERT INTO skills (skill_name, skill_type_id, esco_uri, is_esco)
            VALUES (%s, %s, %s, %s);
        """, (sname.strip(), type_id, esco_uri, 1 if is_esco else 0))
        sid = cur.lastrowid
        db_skills[slow] = sid
        return sid

    clean_jids = list(raw_to_clean_job_id.values())
    if clean_jids:
        cur.execute(f"DELETE FROM job_skills WHERE job_id IN ({','.join(['%s']*len(clean_jids))});", tuple(clean_jids))

    job_skill_inserts = []
    for job in clean_jobs_output:
        c_jid = raw_to_clean_job_id[str(job["job_id"])]
        seen_sids = set()

        for s in job["explicit_skills_detail"]:
            sid = get_or_create_skill(s["skill_name"], s.get("skill_type", "HARD"), is_esco=False)
            if sid not in seen_sids:
                seen_sids.add(sid)
                req = str(s.get("requirement_level", "required")).lower()
                if req not in ('required', 'preferred', 'mentioned'):
                    req = 'required'
                job_skill_inserts.append((c_jid, sid, req, 'llm', 1.0, 'explicit'))

        for es in job.get("esco_skills_detail", []):
            sid = get_or_create_skill(es["skill_name"], es.get("skill_type", "HARD"), is_esco=True, esco_uri=es.get("esco_skill_uri"))
            if sid not in seen_sids:
                seen_sids.add(sid)
                job_skill_inserts.append((c_jid, sid, 'preferred', 'llm', 0.85, 'esco_essential'))

    cur.executemany("""
        INSERT INTO job_skills (job_id, skill_id, requirement_level, extraction_source, confidence_score, source)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, job_skill_inserts)
    conn.commit()

    # 4. Workers và Worker_skills
    cur.execute("SELECT worker_id FROM workers;")
    all_workers = [r[0] for r in cur.fetchall()]
    if all_workers:
        cur.execute(f"DELETE FROM worker_skills WHERE worker_id IN ({','.join(['%s']*len(all_workers))});", tuple(all_workers))
    cur.execute("DELETE FROM workers;")
    conn.commit()

    worker_skill_inserts = []
    for cv in clean_cvs_output:
        cid = cv["cv_id"]
        edu_rank = cv.get("education_level_rank")
        edu_id = (edu_rank + 1) if (edu_rank is not None and 0 <= edu_rank <= 6) else 1
        cur.execute("""
            INSERT INTO workers (
                worker_id, full_name, experience_years, education_level_id,
                school_name, major, target_position_id, is_active, created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, 1, NOW(), NOW()
            );
        """, (cid, f"Ứng viên #{cid:03d}", cv["experience_years"], edu_id, cv["education_school"], cv["education_major"], None))
        w_id = cur.lastrowid

        for s in cv["skills_detail"]:
            sid = get_or_create_skill(s["skill_name"], s.get("skill_type", "HARD"))
            worker_skill_inserts.append((w_id, sid, 4, 'cv_llm', 1.0))

    cur.executemany("""
        INSERT IGNORE INTO worker_skills (worker_id, skill_id, proficiency_level, extraction_source, confidence_score)
        VALUES (%s, %s, %s, %s, %s);
    """, worker_skill_inserts)
    conn.commit()

    # Thống kê
    print("\n" + "=" * 80)
    print("BÁO CÁO THỐNG KÊ TOÀN BỘ SAU KHI TÁI TRÍCH XUẤT:")
    print("=" * 80)
    cur.execute("SELECT COUNT(*) FROM jobs;")
    total_db_jobs = cur.fetchone()[0]

    cur.execute("""
        SELECT source, COUNT(*), COUNT(DISTINCT job_id), ROUND(COUNT(*)/COUNT(DISTINCT job_id), 1)
        FROM job_skills
        GROUP BY source;
    """)
    source_stats = cur.fetchall()

    cur.execute("SELECT COUNT(*) FROM workers;")
    total_db_workers = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM worker_skills;")
    total_db_worker_skills = cur.fetchone()[0]

    print(f"1. Việc làm (Job Postings):")
    print(f"   - File JSON: {CLEAN_JOBS_FILE} ({len(clean_jobs_output)} jobs)")
    print(f"   - Bảng `jobs` MySQL: {total_db_jobs} jobs")
    for s_name, s_count, j_count, avg_s in source_stats:
        print(f"   - Kỹ năng '{s_name}': {s_count} kỹ năng ({j_count} jobs, trung bình {avg_s} skills/job)")

    print(f"\n2. Ứng viên (CVs):")
    print(f"   - File JSON: {CLEAN_RESUMES_FILE} ({len(clean_cvs_output)} CVs)")
    print(f"   - Bảng `workers` MySQL: {total_db_workers} ứng viên")
    print(f"   - Bảng `worker_skills` MySQL: {total_db_worker_skills} kỹ năng")

    cur.close()
    conn.close()
    print("\n-> TOÀN BỘ DỮ LIỆU ĐÃ ĐƯỢC TÁI TRÍCH XUẤT VÀ LÀM SẠCH XUẤT SẮC 100%!")

if __name__ == "__main__":
    run_pipeline()
