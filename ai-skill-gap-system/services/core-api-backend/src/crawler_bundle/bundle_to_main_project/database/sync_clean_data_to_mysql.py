"""
sync_clean_data_to_mysql.py - Đồng bộ 100% dữ liệu làm sạch từ clean_job_postings.json vào MySQL
Mục tiêu: Đưa dữ liệu sạch vào đúng các bảng chuẩn 3NF của hệ thống (KHÔNG phải bảng thô jobs_raw):
1. Bảng `positions`: Nạp đầy đủ 543 vị trí chuẩn hóa gắn với đúng 4 ngành.
2. Bảng `companies`: Chuẩn hóa tên doanh nghiệp.
3. Bảng `jobs` (BẢNG DỮ LIỆU SẠCH):
   - Cột `chuc_vu`: Chức vụ/Cấp bậc chuẩn hóa (Senior, Trưởng phòng, Nhân viên,...)
   - Cột `position_id`: Trỏ đúng vị trí chuẩn hóa trong bảng `positions`
   - Cột `salary_min_vnd`, `salary_max_vnd`, `is_salary_negotiable`: Chuẩn hóa số học tiền tệ VND
   - Cột `experience_min_years`, `experience_max_years`: Chuẩn hóa số năm kinh nghiệm (DECIMAL)
   - Cột `description`, `requirements`: Văn bản đã làm sạch HTML
4. Bảng `skills`: Danh mục kỹ năng chuẩn hóa.
5. Bảng `job_skills`: Liên kết chính xác 100% các kỹ năng thực tế từ clean_job_postings.json (không random).
"""

import json
import os
import re
import sys
import pymysql
import config

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLEAN_JSON = os.path.join(BASE_DIR, "data", "clean_job_postings.json")

def parse_salary_to_vnd(salary_str: str):
    """Chuyển chuỗi lương thành min_vnd, max_vnd, is_negotiable."""
    if not salary_str:
        return None, None, 1
    
    s = salary_str.lower().strip()
    if "thỏa thuận" in s or "cạnh tranh" in s:
        return None, None, 1

    # Đơn vị USD
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

    # Đơn vị Triệu VND
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
    """Chuyển chuỗi kinh nghiệm thành min_years, max_years."""
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

def main():
    print("=" * 70)
    print("BẮT ĐẦU ĐỒNG BỘ 100% DỮ LIỆU SẠCH TỪ clean_job_postings.json VÀO MYSQL")
    print("=" * 70)

    if not os.path.exists(CLEAN_JSON):
        print(f"Lỗi: Không tìm thấy file {CLEAN_JSON}")
        return

    with open(CLEAN_JSON, "r", encoding="utf-8") as f:
        clean_jobs = json.load(f)

    print(f"-> Đã đọc {len(clean_jobs)} bản ghi từ {CLEAN_JSON}")

    conn = pymysql.connect(**config.MYSQL_CONFIG)
    cur = conn.cursor()

    # 1. Ánh xạ ngành chuẩn (industries)
    ind_map = {
        "Công nghệ Thông tin": 1,
        "Du lịch - Dịch vụ": 2,
        "Du lịch-Dịch vụ": 2,
        "Du lịch - Nhà hàng - Khách sạn": 2,
        "Logistics": 3,
        "Logistics - Kho vận - Chuỗi cung ứng": 3,
        "Kế toán": 4,
        "Kế toán - Kiểm toán - Tài chính - Thuế": 4
    }

    # 2. ĐỒNG BỘ CÁC VỊ TRÍ CHUẨN HÓA VÀO BẢNG `positions`
    print("\n[1/5] Đồng bộ danh mục vị trí vào bảng `positions`...")
    # Lấy các vị trí hiện có
    cur.execute("SELECT position_id, position_name, industry_id FROM positions")
    db_positions = {(r[1].lower().strip(), r[2]): r[0] for r in cur.fetchall()}

    new_pos_count = 0
    for job in clean_jobs:
        pos_name = (job.get("position") or job.get("vi_tri") or "Chưa phân loại").strip()
        cat = job.get("category", "")
        ind_id = ind_map.get(cat, 1)

        key = (pos_name.lower(), ind_id)
        if key not in db_positions:
            cur.execute("""
                INSERT INTO positions (position_name, industry_id)
                VALUES (%s, %s)
            """, (pos_name, ind_id))
            pos_id = cur.lastrowid
            db_positions[key] = pos_id
            new_pos_count += 1

    conn.commit()
    print(f"  -> Đã thêm mới {new_pos_count} vị trí vào bảng `positions` (Tổng vị trí trong DB: {len(db_positions)})")

    # 3. ĐỒNG BỘ DOANH NGHIỆP VÀO BẢNG `companies`
    print("\n[2/5] Đồng bộ doanh nghiệp vào bảng `companies`...")
    cur.execute("SELECT company_id, company_name FROM companies")
    db_companies = {r[1].lower().strip(): r[0] for r in cur.fetchall()}

    new_comp_count = 0
    for job in clean_jobs:
        c_name = (job.get("company_name") or "Doanh nghiệp tuyển dụng").strip()
        key = c_name.lower()
        if key not in db_companies:
            cur.execute("INSERT INTO companies (company_name) VALUES (%s)", (c_name,))
            comp_id = cur.lastrowid
            db_companies[key] = comp_id
            new_comp_count += 1

    conn.commit()
    print(f"  -> Đã thêm mới {new_comp_count} doanh nghiệp vào bảng `companies` (Tổng: {len(db_companies)})")

    # 4. ĐỒNG BỘ BẢNG DỮ LIỆU VIỆC LÀM SẠCH `jobs`
    print("\n[3/5] Đồng bộ 1.000 tin tuyển dụng sạch vào bảng `jobs`...")
    # Đảm bảo bảng jobs có cột chuc_vu
    cur.execute("SHOW COLUMNS FROM jobs LIKE 'chuc_vu'")
    if not cur.fetchone():
        cur.execute("ALTER TABLE jobs ADD COLUMN chuc_vu VARCHAR(100) NULL AFTER position_id")

    updated_jobs_count = 0
    raw_to_clean_job_id = {} # raw_job_id -> job_id trong bảng jobs

    for job in clean_jobs:
        raw_jid = str(job["job_id"]).strip()
        title = str(job.get("title", "")).strip()
        chuc_vu = str(job.get("chuc_vu", "Nhân viên")).strip()
        pos_name = str(job.get("position") or job.get("vi_tri") or "Chưa phân loại").strip()
        cat = job.get("category", "")
        ind_id = ind_map.get(cat, 1)
        pos_id = db_positions.get((pos_name.lower(), ind_id), 1)

        c_name = (job.get("company_name") or "Doanh nghiệp tuyển dụng").strip()
        comp_id = db_companies.get(c_name.lower(), 1)

        sal_min, sal_max, is_neg = parse_salary_to_vnd(job.get("salary"))
        exp_min, exp_max = parse_experience_years(job.get("experience_required"))

        desc = str(job.get("description_clean", "")).strip()
        reqs = str(job.get("requirements_clean", "")).strip()
        p_date = job.get("posted_date") or None
        d_line = job.get("deadline") or None

        # Upsert vào bảng jobs
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
                posted_date = VALUES(posted_date),
                deadline = VALUES(deadline),
                updated_at = NOW()
        """, (
            raw_jid, title, chuc_vu, comp_id, pos_id,
            exp_min, exp_max,
            sal_min, sal_max, is_neg,
            desc, reqs, p_date, d_line
        ))

        # Lấy job_id thực tế trong bảng jobs
        cur.execute("SELECT job_id FROM jobs WHERE raw_job_id = %s", (raw_jid,))
        clean_jid = cur.fetchone()[0]
        raw_to_clean_job_id[raw_jid] = clean_jid
        updated_jobs_count += 1

    conn.commit()
    print(f"  -> Đã cập nhật thành công {updated_jobs_count} việc làm vào bảng `jobs`!")

    # 5. ĐỒNG BỘ DANH MỤC KỸ NĂNG VÀO BẢNG `skills`
    print("\n[4/5] Đồng bộ danh mục kỹ năng chuẩn hóa vào bảng `skills`...")
    cur.execute("SELECT skill_id, skill_name FROM skills")
    db_skills = {r[1].lower().strip(): r[0] for r in cur.fetchall()}

    all_clean_skills = set()
    for job in clean_jobs:
        for s in job.get("skills", []):
            all_clean_skills.add(s.strip())

    new_skill_count = 0
    for s_name in all_clean_skills:
        key = s_name.lower()
        if key not in db_skills:
            cur.execute("""
                INSERT INTO skills (skill_name, skill_type_id)
                VALUES (%s, 1)
            """, (s_name,))
            s_id = cur.lastrowid
            db_skills[key] = s_id
            new_skill_count += 1

    conn.commit()
    print(f"  -> Đã có đủ {len(all_clean_skills)} kỹ năng chuẩn trong bảng `skills` (Thêm mới: {new_skill_count})")

    # 6. ĐỒNG BỘ LIÊN KẾT KỸ NĂNG VÀO BẢNG `job_skills` (100% SẠCH, KHÔNG RANDOM)
    print("\n[5/5] Đồng bộ liên kết kỹ năng vào bảng `job_skills`...")
    # Xóa các liên kết cũ của 1.000 job này để nạp dữ liệu sạch 100%
    clean_job_ids = list(raw_to_clean_job_id.values())
    if clean_job_ids:
        format_strings = ','.join(['%s'] * len(clean_job_ids))
        cur.execute(f"DELETE FROM job_skills WHERE job_id IN ({format_strings})", tuple(clean_job_ids))

    job_skill_inserts = []
    for job in clean_jobs:
        raw_jid = str(job["job_id"]).strip()
        clean_jid = raw_to_clean_job_id[raw_jid]
        
        for s_name in job.get("skills", []):
            s_id = db_skills.get(s_name.lower().strip())
            if s_id:
                job_skill_inserts.append((clean_jid, s_id, 'required', 'llm', 1.0))

    cur.executemany("""
        INSERT INTO job_skills (job_id, skill_id, requirement_level, extraction_source, confidence_score)
        VALUES (%s, %s, %s, %s, %s)
    """, job_skill_inserts)

    conn.commit()
    print(f"  -> Đã nạp chính xác {len(job_skill_inserts)} liên kết kỹ năng thực tế vào bảng `job_skills`!")

    # 7. KIỂM TRA TỔNG THỂ DỮ LIỆU SẠCH TRONG MYSQL
    print("\n" + "=" * 70)
    print("KIỂM TRA DỮ LIỆU SẠCH TRONG CƠ SỞ DỮ LIỆU MYSQL:")
    print("=" * 70)

    cur.execute("""
        SELECT 
            COUNT(*) AS total_jobs,
            COUNT(chuc_vu) AS have_chuc_vu,
            COUNT(position_id) AS have_position,
            COUNT(salary_min_vnd) AS have_salary_num,
            SUM(is_salary_negotiable) AS negotiable_jobs
        FROM jobs;
    """)
    res = cur.fetchone()
    print(f"Bảng `jobs` (Dữ liệu việc làm sạch):")
    print(f"  - Tổng số việc làm: {res[0]}")
    print(f"  - Đã có Chức vụ (chuc_vu): {res[1]} / {res[0]}")
    print(f"  - Đã có Vị trí chuẩn hóa (position_id): {res[2]} / {res[0]}")
    print(f"  - Có mức lương số hóa (VND): {res[3]} việc làm")
    print(f"  - Mức lương thỏa thuận: {res[4]} việc làm")

    print(f"\nBảng `job_skills` (Liên kết kỹ năng sạch): {len(job_skill_inserts)} bản ghi.")

    print("\nMẫu 5 bản ghi sạch từ bảng `jobs` kết hợp `positions` & `companies`:")
    cur.execute("""
        SELECT j.job_id, j.title, j.chuc_vu, p.position_name, c.company_name, 
               j.salary_min_vnd, j.salary_max_vnd, j.is_salary_negotiable
        FROM jobs j
        JOIN positions p ON p.position_id = j.position_id
        JOIN companies c ON c.company_id = j.company_id
        LIMIT 5;
    """)
    for r in cur.fetchall():
        sal_display = "Thỏa thuận" if r[7] else f"{r[5]/1000000:.0f} - {r[6]/1000000:.0f} triệu VND" if r[6] else f"Từ {r[5]/1000000:.0f} triệu VND"
        print(f"  [{r[0]}] {r[1][:28]:<28} | Chức vụ: {r[2]:<10} | Vị trí: {r[3]:<22} | Lương: {sal_display}")

    conn.close()
    print("\n=== HOÀN TẤT ĐỒNG BỘ VÀO BẢNG DỮ LIỆU SẠCH MYSQL ===")

if __name__ == "__main__":
    main()
