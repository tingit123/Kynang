"""
extract_positions_groq.py
Sử dụng Groq API (qwen/qwen3.8-27b) để trích xuất và chuẩn hóa:
1. "chuc_vu": Cấp bậc / Chức vụ trong tổ chức (Thực tập sinh, Fresher, Nhân viên, Chuyên viên, Senior, Trưởng nhóm, Trưởng phòng, Quản lý, Giám đốc, Trợ lý...)
2. "position" / "vi_tri": Vị trí công việc chuẩn hóa theo từng ngành nghề (IT, Du lịch, Logistics, Kế toán)

Sau khi xử lý:
- Ghi vào data/clean_job_postings.json
- Nạp danh mục vị trí chuẩn hóa vào bảng positions trong MySQL
- Cập nhật foreign key position_id trong bảng jobs của MySQL
- Đồng bộ lại dữ liệu phân tích và Dashboard
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import re
import time
import json
import pymysql
import groq
from config import GROQ_API_KEY, GROQ_MODEL, MYSQL_CONFIG

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CLEAN_JOBS_FILE = os.path.join(DATA_DIR, "clean_job_postings.json")
CACHE_FILE = os.path.join(DATA_DIR, "job_positions_groq_cache.json")

FALLBACK_LEVELS = [
    (r"(thực tập|intern|trainee)", "Thực tập sinh"),
    (r"(fresher|mới tốt nghiệp)", "Fresher"),
    (r"(giám đốc|director|general manager|head of)", "Giám đốc"),
    (r"(phó giám đốc|deputy director)", "Phó Giám đốc"),
    (r"(trưởng phòng|manager|chỉ huy)", "Trưởng phòng"),
    (r"(phó phòng|deputy manager)", "Phó Trưởng phòng"),
    (r"(quản lý|store manager|restaurant manager|hotel manager)", "Quản lý"),
    (r"(trưởng nhóm|team leader|leader|supervisor|tổ trưởng|giám sát)", "Trưởng nhóm"),
    (r"(senior|chuyên viên cao cấp|lead |principal|chủ nhiệm)", "Senior"),
    (r"(trợ lý|assistant)", "Trợ lý"),
    (r"(chuyên viên|specialist|officer|kỹ sư|developer)", "Chuyên viên"),
    (r"(nhân viên|staff|phụ trách|thợ)", "Nhân viên"),
]

def fallback_extract(title: str, category: str):
    title_lower = title.lower()
    chuc_vu = "Nhân viên"
    for pattern, lvl in FALLBACK_LEVELS:
        if re.search(pattern, title_lower):
            chuc_vu = lvl
            break
            
    clean_p = re.sub(r"\[.*?\]|\(.*?\)", "", title)
    clean_p = re.sub(r"(tuyển dụng|tuyển gấp|thu nhập khủng|lương cao|đi làm ngay|tại đà nẵng|ở hà nội|tại hcm|cần tuyển|nam/nữ|nam|nữ)", "", clean_p, flags=re.IGNORECASE)
    clean_p = re.sub(r"\s+", " ", clean_p).strip(" -:–|")
    if not clean_p or len(clean_p) < 3:
        clean_p = title.strip()
    return {"chuc_vu": chuc_vu, "vi_tri": clean_p}

def get_position_esco_enrichment(position_name: str, industry: str = None, include_optional: bool = False):
    """
    Ánh xạ chức danh/vị trí sang ESCO occupation và trích xuất kỹ năng bổ trợ (Part B).
    QUY TẮC: Chức danh ≠ Kỹ năng; Kỹ năng ESCO inferred chỉ dùng cho gợi ý nghề/đào tạo,
    KHÔNG gộp vào explicit demand của tin tuyển dụng.
    """
    from occupation_esco_matcher import OccupationEscoMatcher
    matcher = OccupationEscoMatcher()
    return matcher.get_esco_skills_for_position(position_name, include_optional=include_optional)

def robust_parse_json(text: str):
    text = text.strip()
    m = re.search(r'\[\s*\{.*\}\s*\]', text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    last_brace = text.rfind('}')
    first_bracket = text.find('[')
    if first_bracket != -1 and last_brace > first_bracket:
        try:
            salvaged = text[first_bracket:last_brace+1] + ']'
            return json.loads(salvaged)
        except Exception:
            pass
    return json.loads(text)

def run_groq_extraction():
    print("=" * 70, flush=True)
    print("BẮT ĐẦU TRÍCH XUẤT CHỨC VỤ & VỊ TRÍ BẰNG GROQ API CHO DỮ LIỆU SẠCH", flush=True)
    print("=" * 70, flush=True)

    if not os.path.exists(CLEAN_JOBS_FILE):
        raise FileNotFoundError(f"Không tìm thấy file: {CLEAN_JOBS_FILE}")

    with open(CLEAN_JOBS_FILE, "r", encoding="utf-8") as f:
        clean_jobs = json.load(f)

    print(f"-> Đã nạp {len(clean_jobs)} tin từ {CLEAN_JOBS_FILE}", flush=True)

    cache = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache = json.load(f)
            print(f"-> Đã tải {len(cache)} kết quả từ cache đã xử lý trước đó.", flush=True)
        except Exception:
            pass

    client = groq.Groq(api_key=GROQ_API_KEY, timeout=25.0)

    jobs_to_process = [j for j in clean_jobs if j["job_id"] not in cache]
    print(f"-> Cần xử lý qua Groq: {len(jobs_to_process)} tin", flush=True)

    BATCH_SIZE = 8
    total_batches = (len(jobs_to_process) + BATCH_SIZE - 1) // BATCH_SIZE if jobs_to_process else 0

    for b_idx in range(total_batches):
        batch = jobs_to_process[b_idx * BATCH_SIZE : (b_idx + 1) * BATCH_SIZE]
        batch_input = [
            {
                "id": str(j["job_id"]),
                "title": str(j.get("title", "")).strip()
            }
            for j in batch
        ]

        prompt = f"""Dưới đây là danh sách {len(batch_input)} tin tuyển dụng:
{json.dumps(batch_input, ensure_ascii=False)}

Yêu cầu phân tách chính xác cho từng tin:
- "chuc_vu": Cấp bậc / chức vụ, CHỈ CHỌN 1 TRONG CÁC GIÁ TRỊ: [Thực tập sinh, Fresher, Nhân viên, Chuyên viên, Senior, Trưởng nhóm, Trưởng phòng, Quản lý, Giám đốc, Trợ lý].
- "vi_tri": Tên nghề nghiệp/vị trí chuẩn hóa ngắn gọn từ 2-4 từ (VD: Frontend Developer, Backend Developer, Nhân viên Lễ tân, Bartender / Pha chế, Kế toán tổng hợp, Kế toán thuế, Nhân viên Xuất nhập khẩu, Kỹ sư DevOps, Trưởng phòng Marketing...).

Trả về DUY NHẤT một JSON array thuần túy:
[
  {{"id": "...", "chuc_vu": "...", "vi_tri": "..."}},
  ...
]"""

        success = False
        for attempt in range(3):
            try:
                resp = client.chat.completions.create(
                    model="qwen/qwen3.8-27b",
                    messages=[
                        {"role": "system", "content": "Bạn là chuyên gia phân loại chức vụ và vị trí nhân sự, chỉ trả lời JSON array chuẩn."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=600
                )
                raw_text = resp.choices[0].message.content.strip()
                items = robust_parse_json(raw_text)

                for it in items:
                    jid = str(it.get("id"))
                    cv = str(it.get("chuc_vu") or "Nhân viên").strip()
                    vt = str(it.get("vi_tri") or "").strip()
                    if not vt:
                        t_item = next((j for j in batch if str(j["job_id"]) == jid), None)
                        if t_item:
                            fb = fallback_extract(t_item["title"], t_item.get("category", ""))
                            vt = fb["vi_tri"]
                    cache[jid] = {"chuc_vu": cv, "vi_tri": vt}

                success = True
                print(f"[{b_idx+1}/{total_batches}] Batch #{b_idx+1}: Trích xuất thành công {len(items)} tin bằng Groq", flush=True)
                break
            except Exception as e:
                err_str = str(e)
                wait_sec = 6.0 if "429" in err_str else 2.5
                print(f"[{b_idx+1}/{total_batches}] Thử lần {attempt+1} gặp lỗi: {e}. Tạm dừng {wait_sec}s...", flush=True)
                time.sleep(wait_sec)

        if not success:
            print(f"[{b_idx+1}/{total_batches}] Batch #{b_idx+1} dùng fallback cho {len(batch)} tin.", flush=True)
            for j in batch:
                jid = str(j["job_id"])
                cache[jid] = fallback_extract(j.get("title", ""), j.get("category", ""))

        # Lưu cache sau mỗi batch
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)

        time.sleep(2.0)

    # Cập nhật kết quả vào clean_jobs
    print("\n" + "=" * 70, flush=True)
    print("-> Cập nhật chức vụ và vị trí vào clean_job_postings.json...", flush=True)
    for j in clean_jobs:
        jid = str(j["job_id"])
        c_info = cache.get(jid, fallback_extract(j.get("title", ""), j.get("category", "")))
        j["chuc_vu"] = c_info["chuc_vu"]
        j["vi_tri"] = c_info["vi_tri"]
        j["position"] = c_info["vi_tri"]

    with open(CLEAN_JOBS_FILE, "w", encoding="utf-8") as f:
        json.dump(clean_jobs, f, ensure_ascii=False, indent=2)

    print(f"-> ĐÃ GHI FILE DỮ LIỆU SẠCH HOÀN TẤT: {CLEAN_JOBS_FILE}", flush=True)

    # =========================================================================
    # CẬP NHẬT VÀO MYSQL (BẢNG positions VÀ BẢNG jobs)
    # =========================================================================
    print("\n" + "=" * 70, flush=True)
    print("CẬP NHẬT DANH MỤC POSITIONS VÀ JOBS TRONG CƠ SỞ DỮ LIỆU MYSQL 3NF", flush=True)
    print("=" * 70, flush=True)

    try:
        conn = pymysql.connect(**MYSQL_CONFIG)
        cur = conn.cursor()

        cur.execute("SELECT industry_id, industry_code, industry_name_vi FROM industries")
        ind_rows = cur.fetchall()
        ind_map = {}
        for i_id, i_code, i_name in ind_rows:
            ind_map[i_code] = i_id
            ind_map[i_name] = i_id

        category_to_ind_id = {
            "Công nghệ Thông tin": ind_map.get("IT", 1),
            "Du lịch - Dịch vụ": ind_map.get("TOURISM", 2),
            "Du lịch - Nhà hàng - Khách sạn": ind_map.get("TOURISM", 2),
            "Logistics": ind_map.get("LOGISTICS", 3),
            "Logistics - Kho vận - Chuỗi cung ứng": ind_map.get("LOGISTICS", 3),
            "Kế toán": ind_map.get("ACCOUNTING", 4),
            "Kế toán - Kiểm toán - Tài chính - Thuế": ind_map.get("ACCOUNTING", 4)
        }

        distinct_positions = set()
        for j in clean_jobs:
            cat = j.get("category", "")
            ind_id = category_to_ind_id.get(cat, 1)
            pos_name = j.get("position", "").strip()
            if pos_name:
                distinct_positions.add((ind_id, pos_name))

        print(f"-> Chuẩn bị nạp {len(distinct_positions)} vị trí công việc vào bảng positions...", flush=True)

        for ind_id, pos_name in distinct_positions:
            cur.execute("""
                INSERT INTO positions (industry_id, position_name)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE position_name = VALUES(position_name)
            """, (ind_id, pos_name))

        conn.commit()

        cur.execute("SELECT position_id, industry_id, position_name FROM positions")
        pos_id_map = {}
        for pid, ind_id, pname in cur.fetchall():
            pos_id_map[(ind_id, pname)] = pid

        updated_jobs_count = 0
        for j in clean_jobs:
            jid = str(j["job_id"])
            cat = j.get("category", "")
            ind_id = category_to_ind_id.get(cat, 1)
            pos_name = j.get("position", "").strip()
            pid = pos_id_map.get((ind_id, pos_name))
            if pid:
                cur.execute("""
                    UPDATE jobs
                    SET position_id = %s
                    WHERE raw_job_id = %s
                """, (pid, jid))
                updated_jobs_count += cur.rowcount

        conn.commit()
        conn.close()

        print(f"-> Đã đồng bộ thành công vào MySQL:", flush=True)
        print(f"   * Bảng positions: {len(pos_id_map)} vị trí công việc phân bổ theo 4 ngành.", flush=True)
        print(f"   * Bảng jobs: Đã cập nhật {updated_jobs_count} tin với position_id chuẩn xác.", flush=True)
    except Exception as e:
        print(f"-> Gặp lỗi khi đồng bộ MySQL: {e}", flush=True)

    # Thống kê phân bố chức vụ
    chuc_vu_counts = {}
    for j in clean_jobs:
        cv = j.get("chuc_vu", "Nhân viên")
        chuc_vu_counts[cv] = chuc_vu_counts.get(cv, 0) + 1

    print("\n" + "=" * 70, flush=True)
    print("THỐNG KÊ PHÂN BỐ CẤP BẬC / CHỨC VỤ SAU KHI LÀM SẠCH BẰNG GROQ:", flush=True)
    print("=" * 70, flush=True)
    for cv, cnt in sorted(chuc_vu_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {cv}: {cnt} tin ({cnt/len(clean_jobs)*100:.1f}%)", flush=True)

    print("\nVí dụ 5 tin sau khi bổ sung chức vụ & vị trí:", flush=True)
    for j in clean_jobs[:5]:
        print(f"   * [{j['job_id']}] Tiêu đề: {j['title'][:35]}... -> Chức vụ: {j['chuc_vu']} | Vị trí: {j['position']}", flush=True)

    print("\n=> HOÀN TẤT 100% QUÁ TRÌNH TRÍCH XUẤT VÀ CẬP NHẬT!", flush=True)

if __name__ == "__main__":
    run_groq_extraction()
