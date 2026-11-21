"""
Service: Unified Dashboard Analytics Engine (Skill Lens Lab)
100% dữ liệu thực tế từ MySQL (job_postings, extracted_skills, survey_responses, survey_skill_ratings, skill_catalog).
Nguyên tắc bắt buộc:
- Không hardcode dữ liệu theo quý hoặc địa phương.
- Không tạo dữ liệu giả, không lấy dữ liệu quý khác hay địa phương khác để thay thế.
- Toàn quốc = Tổng hợp (SUM) từ các đơn vị địa lý độc lập (tỉnh/thành) có dữ liệu trong kỳ, không cộng trùng vùng.
- Mọi tỷ lệ % (Demand, Supply) được tính lại từ tổng tử số và tổng mẫu số, không lấy trung bình cộng % các tỉnh.
- Gap = Demand - Supply (chỉ tính khi có đủ cả dữ liệu Demand và Supply; nếu thiếu giữ null, không gán 0 tùy tiện).
"""
from __future__ import annotations

import unicodedata
from datetime import date
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text

# ── Danh mục 63 Tỉnh/Thành phố độc lập (khớp mã select box trên Dashboard) ──
PROVINCE_NAMES: Dict[str, str] = {
    "all": "Toàn quốc (Cả nước)",
    "HN": "Hà Nội",
    "HCM": "TP. Hồ Chí Minh",
    "CT": "Cần Thơ",
    "DN_CITY": "Đà Nẵng",
    "HP": "Hải Phòng",
    # ĐBSCL
    "AG": "An Giang", "DT": "Đồng Tháp", "TG": "Tiền Giang", "KG": "Kiên Giang",
    "BT": "Bến Tre", "VL": "Vĩnh Long", "TV": "Trà Vinh", "ST": "Sóc Trăng",
    "BL": "Bạc Liêu", "CM": "Cà Mau", "HG": "Hậu Giang", "LA": "Long An",
    # Đông Nam Bộ
    "BD": "Bình Dương", "DN": "Đồng Nai", "BRVT": "Bà Rịa - Vũng Tàu",
    "TN": "Tây Ninh", "BP": "Bình Phước",
    # Đồng bằng Sông Hồng
    "QN": "Quảng Ninh", "BN": "Bắc Ninh", "HD": "Hải Dương", "HY": "Hưng Yên",
    "TB": "Thái Bình", "ND": "Nam Định", "NB": "Ninh Bình", "HNA": "Hà Nam",
    "VP": "Vĩnh Phúc",
    # Miền Trung
    "TTH": "Thừa Thiên Huế", "QNA": "Quảng Nam", "QNG": "Quảng Ngãi",
    "BDH": "Bình Định", "PY": "Phú Yên", "KH": "Khánh Hòa", "NT": "Ninh Thuận",
    "BTU": "Bình Thuận", "TH": "Thanh Hóa", "NA": "Nghệ An", "HT": "Hà Tĩnh",
    "QB": "Quảng Bình", "QT": "Quảng Trị",
    # Tây Nguyên
    "DL": "Đắk Lắk", "LD": "Lâm Đồng", "GL": "Gia Lai", "KT": "Kon Tum", "DKN": "Đắk Nông",
    # Trung du & Miền núi phía Bắc
    "TN_PR": "Thái Nguyên", "BG": "Bắc Giang", "PT": "Phú Thọ", "TQ": "Tuyên Quang",
    "LS": "Lạng Sơn", "HG_PR": "Hà Giang", "CB": "Cao Bằng", "BK": "Bắc Kạn",
    "LC": "Lào Cai", "YB": "Yên Bái", "DB": "Điện Biên", "LC_PR": "Lai Châu",
    "SL": "Sơn La", "HB": "Hòa Bình",
}

# Các nhãn vùng/tổng hợp không được cộng trùng vào Toàn quốc
AGGREGATE_REGION_KEYWORDS = [
    "toan quoc", "ca nuoc", "dbscl", "dong bang song cuu long",
    "mien nam", "mien bac", "mien trung", "tay nguyen", "dong nam bo",
    "dong bang song hong", "nationwide", "vietnam", "viet nam"
]

# Bản đồ từ khóa nhận diện địa bàn độc lập (không dấu)
PROVINCE_MATCH_RULES: List[Tuple[str, List[str]]] = [
    ("CT", ["can tho", "tra noc", "ninh kieu", "binh thuy", "cai rang", "o mon", "ctu", "dnc", "ctut"]),
    ("HN", ["ha noi", "hanoi", "cau giay", "dong da", "ba dinh", "thanh xuan", "hoan kiem", "bach khoa ha noi"]),
    ("HCM", ["ho chi minh", "tp.hcm", "tphcm", "sai gon", "saigon", "thu duc", "hcm"]),
    ("DN_CITY", ["da nang", "danang", "hai chau", "ngu hanh son"]),
    ("HP", ["hai phong"]),
    ("AG", ["an giang", "long xuyen", "chau doc"]),
    ("DT", ["dong thap", "cao lanh", "sa dec"]),
    ("TG", ["tien giang", "my tho"]),
    ("KG", ["kien giang", "rach gia", "phu quoc"]),
    ("BT", ["ben tre"]),
    ("VL", ["vinh long"]),
    ("TV", ["tra vinh"]),
    ("ST", ["soc trang"]),
    ("BL", ["bac lieu"]),
    ("CM", ["ca mau"]),
    ("HG", ["hau giang", "vi thanh"]),
    ("LA", ["long an", "tan an"]),
    ("BD", ["binh duong", "thu dau mot"]),
    ("DN", ["dong nai", "bien hoa"]),
    ("BRVT", ["ba ria", "vung tau"]),
    ("TN", ["tay ninh"]),
    ("BP", ["binh phuoc"]),
    ("QN", ["quang ninh", "ha long"]),
    ("BN", ["bac ninh"]),
    ("HD", ["hai duong"]),
    ("HY", ["hung yen"]),
    ("TB", ["thai binh"]),
    ("ND", ["nam dinh"]),
    ("NB", ["ninh binh"]),
    ("HNA", ["ha nam"]),
    ("VP", ["vinh phuc"]),
    ("TTH", ["thua thien hue", "tp hue", "hue"]),
    ("QNA", ["quang nam", "tam ky", "hoi an"]),
    ("QNG", ["quang ngai"]),
    ("BDH", ["binh dinh", "quy nhon"]),
    ("PY", ["phu yen", "tuy hoa"]),
    ("KH", ["khanh hoa", "nha trang"]),
    ("NT", ["ninh thuan", "phan rang"]),
    ("BTU", ["binh thuan", "phan thiet"]),
    ("TH", ["thanh hoa"]),
    ("NA", ["nghe an", "tp vinh"]),
    ("HT", ["ha tinh"]),
    ("QB", ["quang binh", "dong hoi"]),
    ("QT", ["quang tri"]),
    ("DL", ["dak lak", "buon ma thuot"]),
    ("LD", ["lam dong", "da lat"]),
    ("GL", ["gia lai", "pleiku"]),
    ("KT", ["kon tum"]),
    ("DKN", ["dak nong"]),
    ("TN_PR", ["thai nguyen"]),
    ("BG", ["bac giang"]),
    ("PT", ["phu tho", "viet tri"]),
    ("TQ", ["tuyen quang"]),
    ("LS", ["lang son"]),
    ("HG_PR", ["ha giang"]),
    ("CB", ["cao bang"]),
    ("BK", ["bac kan"]),
    ("LC", ["lao cai", "sapa"]),
    ("YB", ["yen bai"]),
    ("DB", ["dien bien"]),
    ("LC_PR", ["lai chau"]),
    ("SL", ["son la"]),
    ("HB", ["hoa binh"]),
]

# Chuẩn hóa ngành nghề (DB -> 5 nhóm chuẩn trên Dashboard)
INDUSTRY_META = [
    {"key": "IT", "db_names": ["IT", "Công nghệ thông tin", "CNTT"], "label": "IT & Công nghệ", "color": "#0fa39e"},
    {"key": "tourism", "db_names": ["Du lịch", "Du lịch & Khách sạn"], "label": "Du lịch & Khách sạn", "color": "#10b981"},
    {"key": "logistics", "db_names": ["Logistics", "Logistics & XNK"], "label": "Logistics & XNK", "color": "#f59e0b"},
    {"key": "economics", "db_names": ["Kinh tế", "Kinh tế & Tài chính"], "label": "Kinh tế & Tài chính", "color": "#dc2626"},
    {"key": "agriculture", "db_names": ["Nông nghiệp", "Nông nghiệp CNC"], "label": "Nông nghiệp CNC", "color": "#7c3aed"},
]

# Map chuyên ngành khảo sát sinh viên -> nhóm ngành chuẩn
SURVEY_MAJOR_TO_INDUSTRY = {
    "IT": [
        "công nghệ thông tin", "kỹ thuật phần mềm", "khoa học máy tính",
        "hệ thống thông tin", "mạng máy tính", "trí tuệ nhân tạo", "ai", "cntt"
    ],
    "tourism": [
        "du lịch", "khách sạn", "nhà hàng", "lữ hành", "việt nam học"
    ],
    "logistics": [
        "logistics", "chuỗi cung ứng", "kinh tế vận tải", "khai thác cảng", "ngoại thương", "xuất nhập khẩu"
    ],
    "economics": [
        "kế toán", "kiểm toán", "quản trị kinh doanh", "tài chính", "ngân hàng", "kinh doanh thương mại", "kinh tế"
    ],
    "agriculture": [
        "nông nghiệp", "thủy sản", "nông học", "công nghệ sinh học"
    ],
}

PROFICIENCY_THRESHOLD = 65  # Khớp 100% chuẩn tính supply_pct của hệ thống skill_catalog


def _strip_accents(text_val: str) -> str:
    if not text_val:
        return ""
    s = unicodedata.normalize("NFD", str(text_val))
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return s.replace("đ", "d").replace("Đ", "D").lower().strip()


def normalize_province_code(raw_location: Optional[str], fallback_for_cv_platform: bool = False) -> Tuple[Optional[str], bool]:
    """
    Trả về (province_code, is_aggregate_region).
    - Nếu là tên tỉnh/thành cụ thể -> (code, False)
    - Nếu là nhãn vùng tổng hợp (Toàn quốc, ĐBSCL, Miền Nam...) -> (None, True) để không cộng trùng.
    - Nếu không rõ địa bàn: với hồ sơ CV tự phân tích của nền tảng Cần Thơ -> ('CT', False) khi fallback_for_cv_platform=True.
    """
    norm = _strip_accents(raw_location or "")
    if not norm:
        return ("CT", False) if fallback_for_cv_platform else (None, False)

    # Kiểm tra trùng khớp mã trực tiếp (ví dụ 'CT', 'HN', 'HCM', 'DN_CITY')
    raw_up = (raw_location or "").strip().upper()
    if raw_up in PROVINCE_NAMES and raw_up != "ALL":
        return (raw_up, False)

    # Kiểm tra địa bàn tỉnh/thành độc lập trước (ví dụ "Cần Thơ (ĐBSCL)" vẫn thuộc tỉnh CT độc lập)
    for code, keywords in PROVINCE_MATCH_RULES:
        for kw in keywords:
            if kw in norm:
                return (code, False)

    # Nếu chỉ chứa tên vùng tổng hợp mà không gắn tỉnh cụ thể -> đánh dấu aggregate để tránh cộng trùng
    for agg_kw in AGGREGATE_REGION_KEYWORDS:
        if agg_kw in norm:
            return (None, True)

    if fallback_for_cv_platform and ("ho so ung vien" in norm or "skill" in norm):
        return ("CT", False)

    return (None, False)


def normalize_industry_key(raw_industry: Optional[str]) -> str:
    norm = _strip_accents(raw_industry or "")
    if not norm:
        return "other"
    if any(k in norm for k in ["it", "cong nghe thong tin", "cntt", "phan mem"]):
        return "IT"
    if any(k in norm for k in ["du lich", "khach san", "lu hanh", "nha hang"]):
        return "tourism"
    if any(k in norm for k in ["logistics", "xuat nhap khau", "xnk", "kho van", "chuoi cung ung", "van tai", "cang"]):
        return "logistics"
    if any(k in norm for k in ["nong nghiep", "agritech", "thuy san"]):
        return "agriculture"
    if any(k in norm for k in ["kinh te", "tai chinh", "ke toan", "kiem toan", "ngan hang", "thuong mai", "quan tri"]):
        return "economics"
    return "other"


def map_survey_major_to_industry(raw_major: Optional[str]) -> str:
    norm = _strip_accents(raw_major or "")
    if not norm:
        return "other"
    # Kiểm tra nông nghiệp trước kinh tế vì có ngành "Kinh tế nông nghiệp"
    if "nong nghiep" in norm:
        return "agriculture"
    for ind_key in ["IT", "tourism", "logistics", "economics"]:
        for kw in SURVEY_MAJOR_TO_INDUSTRY[ind_key]:
            if _strip_accents(kw) in norm:
                return ind_key
    return "other"


def parse_period_params(
    period: Optional[str] = None,
    period_type: Optional[str] = None,
    year: Optional[int] = None,
    quarter: Optional[int] = None,
) -> Dict[str, Any]:
    """Chuẩn hóa tham số kỳ báo cáo và tính chính xác khoảng ngày [start_date, end_date]."""
    resolved_year = year or 2026
    resolved_type = (period_type or "").lower().strip()
    resolved_quarter = quarter

    if period:
        p = period.strip().upper()
        parts = p.split("_")
        if len(parts) == 2 and parts[0].isdigit():
            resolved_year = int(parts[0])
            if parts[1] == "ALL":
                resolved_type = "year"
                resolved_quarter = None
            elif parts[1].startswith("Q") and parts[1][1:].isdigit():
                q_num = int(parts[1][1:])
                if 1 <= q_num <= 4:
                    resolved_type = "quarter"
                    resolved_quarter = q_num

    if not resolved_type:
        resolved_type = "quarter" if resolved_quarter in (1, 2, 3, 4) else "year"

    if resolved_type == "quarter":
        q = resolved_quarter if resolved_quarter in (1, 2, 3, 4) else 3
        resolved_quarter = q
        q_ranges = {
            1: (date(resolved_year, 1, 1), date(resolved_year, 3, 31)),
            2: (date(resolved_year, 4, 1), date(resolved_year, 6, 30)),
            3: (date(resolved_year, 7, 1), date(resolved_year, 9, 30)),
            4: (date(resolved_year, 10, 1), date(resolved_year, 12, 31)),
        }
        start_d, end_d = q_ranges[q]
        period_code = f"{resolved_year}_Q{q}"
        period_label = f"Quý {q}/{resolved_year}"
    else:
        resolved_type = "year"
        resolved_quarter = None
        start_d, end_d = date(resolved_year, 1, 1), date(resolved_year, 12, 31)
        period_code = f"{resolved_year}_ALL"
        period_label = f"Toàn năm {resolved_year}"

    return {
        "period_type": resolved_type,
        "year": resolved_year,
        "quarter": resolved_quarter,
        "period_code": period_code,
        "period_label": period_label,
        "start_date": start_d,
        "end_date": end_d,
    }


def _date_in_range(d: Optional[date], start_d: date, end_d: date) -> bool:
    if d is None:
        return False
    if hasattr(d, "date") and callable(getattr(d, "date")):
        d = d.date()
    return start_d <= d <= end_d


def _quarter_of_date(d: Optional[date]) -> Tuple[Optional[int], Optional[int]]:
    if d is None:
        return (None, None)
    if hasattr(d, "date") and callable(getattr(d, "date")):
        d = d.date()
    return (d.year, (d.month - 1) // 3 + 1)


def compute_dashboard_analytics(
    db: Session,
    location_id: str = "all",
    period: Optional[str] = None,
    period_type: Optional[str] = None,
    year: Optional[int] = None,
    quarter: Optional[int] = None,
    industry: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Tính toán toàn bộ dữ liệu Dashboard thống nhất từ MySQL thật cho cặp (location_id, period).
    Đảm bảo:
    - Toàn quốc ('all') = SUM chính xác của tất cả tỉnh/thành độc lập có dữ liệu trong kỳ.
    - Tỉnh/thành hoặc quý không có dữ liệu -> trả về rỗng (has_data=False), không fallback.
    - Không gán 0 cho chỉ số thiếu dữ liệu (Supply/Gap = None khi không có khảo sát cung trong kỳ).
    """
    loc_id = (location_id or "all").strip()
    if loc_id.lower() == "all":
        loc_id = "all"
    loc_name = PROVINCE_NAMES.get(loc_id, loc_id)

    pinfo = parse_period_params(period=period, period_type=period_type, year=year, quarter=quarter)
    start_d: date = pinfo["start_date"]
    end_d: date = pinfo["end_date"]
    sel_year: int = pinfo["year"]
    sel_quarter: Optional[int] = pinfo["quarter"]

    # ── 1. Tải danh mục kỹ năng mềm (skill_catalog) để nhận diện chuẩn nhóm kỹ năng ──
    catalog_rows = db.execute(
        text("SELECT id, skill_name, industry FROM skill_catalog")
    ).fetchall()
    skill_id_to_info: Dict[int, Dict[str, str]] = {}
    soft_skill_names_lower = set()
    skill_name_to_industry: Dict[str, str] = {}
    canonical_skill_names: Dict[str, str] = {}
    for row in catalog_rows:
        sid, sname, sind = row[0], (row[1] or "").strip(), (row[2] or "").strip()
        skill_id_to_info[sid] = {"skill_name": sname, "industry": sind}
        sl = sname.lower()
        canonical_skill_names[sl] = sname
        if sind == "Tất cả":
            soft_skill_names_lower.add(sl)
        if sl not in skill_name_to_industry or skill_name_to_industry[sl] == "Tất cả":
            skill_name_to_industry[sl] = sind

    # ── 2. Đọc tất cả job_postings (kèm ngày thực tế, địa bàn, ngành, lương) ──
    # Lưu ý: 1.000 tin tuyển dụng thu thập phục vụ phân tích thị trường có is_deleted=1 để tách khỏi danh sách quản lý tin nhà tuyển dụng;
    # cả 1.032 bản ghi đều là dữ liệu tuyển dụng thực tế trong DB.
    job_rows = db.execute(
        text("""
            SELECT id, location, industry, COALESCE(posted_date, DATE(created_at)) AS eff_date,
                   salary_min, salary_max
            FROM job_postings
        """)
    ).fetchall()

    # Phân loại job theo tỉnh độc lập & thời gian
    jobs_by_id: Dict[int, Dict[str, Any]] = {}
    # Thống kê theo từng tỉnh độc lập trong kỳ được chọn (để chứng minh Toàn quốc = SUM các tỉnh)
    province_stats: Dict[str, Dict[str, Any]] = {}
    # Chuỗi thời gian theo 4 quý trong năm sel_year (cho địa bàn được chọn)
    quarterly_industry_counts: Dict[int, Dict[str, int]] = {
        q: {m["key"]: 0 for m in INDUSTRY_META} for q in (1, 2, 3, 4)
    }
    quarterly_total_jobs: Dict[int, int] = {1: 0, 2: 0, 3: 0, 4: 0}

    # Chuẩn bị kỳ so sánh trước đó (để xây biểu đồ so sánh tỷ trọng từ dữ liệu thực)
    if pinfo["period_type"] == "quarter" and sel_quarter is not None:
        if sel_quarter > 1:
            prev_pinfo = parse_period_params(period_type="quarter", year=sel_year, quarter=sel_quarter - 1)
        else:
            prev_pinfo = parse_period_params(period_type="quarter", year=sel_year - 1, quarter=4)
    else:
        prev_pinfo = parse_period_params(period_type="year", year=sel_year - 1)

    prev_industry_counts: Dict[str, int] = {m["key"]: 0 for m in INDUSTRY_META}
    prev_total_jobs = 0

    selected_job_ids = set()
    selected_year_job_ids_by_q: Dict[int, set] = {1: set(), 2: set(), 3: set(), 4: set()}

    for row in job_rows:
        jid, raw_loc, raw_ind, eff_date, sal_min, sal_max = row
        prov_code, is_agg = normalize_province_code(raw_loc, fallback_for_cv_platform=False)
        # Bỏ qua các dòng nhãn vùng tổng hợp nếu có để không bao giờ cộng trùng
        if is_agg or not prov_code:
            continue

        ind_key = normalize_industry_key(raw_ind)
        jobs_by_id[jid] = {
            "id": jid,
            "province": prov_code,
            "industry_key": ind_key,
            "eff_date": eff_date,
            "salary_min": sal_min,
            "salary_max": sal_max,
        }

        loc_matches = (loc_id == "all") or (prov_code == loc_id)

        # Cập nhật chuỗi 4 quý trong năm sel_year cho địa bàn được chọn
        dy, dq = _quarter_of_date(eff_date)
        if loc_matches and dy == sel_year and dq in (1, 2, 3, 4):
            quarterly_total_jobs[dq] += 1
            selected_year_job_ids_by_q[dq].add(jid)
            if ind_key in quarterly_industry_counts[dq]:
                quarterly_industry_counts[dq][ind_key] += 1

        # Cập nhật kỳ trước để so sánh tỷ trọng
        if loc_matches and _date_in_range(eff_date, prev_pinfo["start_date"], prev_pinfo["end_date"]):
            prev_total_jobs += 1
            if ind_key in prev_industry_counts:
                prev_industry_counts[ind_key] += 1

        # Cập nhật trong kỳ báo cáo đang chọn
        if _date_in_range(eff_date, start_d, end_d):
            if prov_code not in province_stats:
                province_stats[prov_code] = {
                    "location_id": prov_code,
                    "location_name": PROVINCE_NAMES.get(prov_code, prov_code),
                    "job_count": 0,
                    "survey_count": 0,
                    "industry_counts": {m["key"]: 0 for m in INDUSTRY_META},
                    "industry_surveys": {m["key"]: 0 for m in INDUSTRY_META},
                    "salaries": [],
                    "industry_salaries": {m["key"]: [] for m in INDUSTRY_META},
                }
            if loc_matches:
                selected_job_ids.add(jid)
                pstat = province_stats[prov_code]
                pstat["job_count"] += 1
                if ind_key in pstat["industry_counts"]:
                    pstat["industry_counts"][ind_key] += 1
                if sal_min and sal_max and sal_min > 0 and sal_max >= sal_min:
                    pstat["salaries"].append((sal_min, sal_max))
                    if ind_key in pstat["industry_salaries"]:
                        pstat["industry_salaries"][ind_key].append((sal_min, sal_max))

    # ── 3. Đọc tất cả survey_responses ──
    survey_rows = db.execute(
        text("""
            SELECT id, major, institution, COALESCE(completed_at, DATE(created_at)) AS eff_date
            FROM survey_responses
        """)
    ).fetchall()

    selected_survey_ids = set()
    selected_year_survey_ids_by_q: Dict[int, set] = {1: set(), 2: set(), 3: set(), 4: set()}
    surveys_by_id: Dict[int, Dict[str, Any]] = {}

    for row in survey_rows:
        sid, raw_major, raw_inst, eff_date = row
        prov_code, is_agg = normalize_province_code(raw_inst, fallback_for_cv_platform=True)
        if is_agg or not prov_code:
            continue

        ind_key = map_survey_major_to_industry(raw_major)
        surveys_by_id[sid] = {
            "id": sid,
            "province": prov_code,
            "industry_key": ind_key,
            "eff_date": eff_date,
        }

        loc_matches = (loc_id == "all") or (prov_code == loc_id)
        dy, dq = _quarter_of_date(eff_date)
        if loc_matches and dy == sel_year and dq in (1, 2, 3, 4):
            selected_year_survey_ids_by_q[dq].add(sid)

        if _date_in_range(eff_date, start_d, end_d):
            if prov_code not in province_stats:
                province_stats[prov_code] = {
                    "location_id": prov_code,
                    "location_name": PROVINCE_NAMES.get(prov_code, prov_code),
                    "job_count": 0,
                    "survey_count": 0,
                    "industry_counts": {m["key"]: 0 for m in INDUSTRY_META},
                    "industry_surveys": {m["key"]: 0 for m in INDUSTRY_META},
                    "salaries": [],
                    "industry_salaries": {m["key"]: [] for m in INDUSTRY_META},
                }
            if loc_matches:
                selected_survey_ids.add(sid)
                pstat = province_stats[prov_code]
                pstat["survey_count"] += 1
                if ind_key in pstat["industry_surveys"]:
                    pstat["industry_surveys"][ind_key] += 1

    # Lọc province_breakdown chỉ gồm các tỉnh phù hợp với loc_id và thực sự có dữ liệu (>0)
    active_provinces = [
        p for code, p in province_stats.items()
        if ((loc_id == "all") or (code == loc_id)) and (p["job_count"] > 0 or p["survey_count"] > 0)
    ]
    active_provinces.sort(key=lambda x: (x["job_count"], x["survey_count"]), reverse=True)

    # ── 4. TỔNG HỢP TỪ TỔNG SỐ LIỆU CÁC TỈNH ĐỘC LẬP (Toàn quốc = SUM các tỉnh) ──
    total_jobs = sum(p["job_count"] for p in active_provinces)
    total_surveys = sum(p["survey_count"] for p in active_provinces)

    industry_job_totals: Dict[str, int] = {
        m["key"]: sum(p["industry_counts"][m["key"]] for p in active_provinces)
        for m in INDUSTRY_META
    }
    industry_survey_totals: Dict[str, int] = {
        m["key"]: sum(p["industry_surveys"][m["key"]] for p in active_provinces)
        for m in INDUSTRY_META
    }

    has_job_data = total_jobs > 0
    has_survey_data = total_surveys > 0
    has_data = has_job_data or has_survey_data
    has_gap_data = has_job_data and has_survey_data

    # ── 5. Tính toán Demand (từ extracted_skills) và Supply (từ survey_skill_ratings) ──
    # Demand counts: tổng thể và theo từng ngành (đếm DISTINCT job_id cho từng kỹ năng)
    skill_demand_jobs: Dict[str, set] = {}
    industry_skill_demand_jobs: Dict[str, Dict[str, set]] = {m["key"]: {} for m in INDUSTRY_META}
    quarterly_soft_demand: Dict[int, Dict[str, set]] = {q: {} for q in (1, 2, 3, 4)}

    all_year_job_ids = set().union(*selected_year_job_ids_by_q.values())
    relevant_job_ids = selected_job_ids | all_year_job_ids

    if relevant_job_ids:
        es_rows = db.execute(
            text("SELECT job_id, skill_name FROM extracted_skills")
        ).fetchall()
        for jid, raw_sname in es_rows:
            if jid not in relevant_job_ids:
                continue
            sname = (raw_sname or "").strip()
            if not sname:
                continue
            sl = sname.lower()
            canon = canonical_skill_names.get(sl, sname)
            canonical_skill_names.setdefault(sl, canon)

            jinfo = jobs_by_id.get(jid)
            if not jinfo:
                continue

            if jid in selected_job_ids:
                skill_demand_jobs.setdefault(sl, set()).add(jid)
                ik = jinfo["industry_key"]
                if ik in industry_skill_demand_jobs:
                    industry_skill_demand_jobs[ik].setdefault(sl, set()).add(jid)

            # Chuỗi kỹ năng mềm theo quý trong năm sel_year
            if sl in soft_skill_names_lower:
                dy, dq = _quarter_of_date(jinfo["eff_date"])
                if dy == sel_year and dq in (1, 2, 3, 4):
                    quarterly_soft_demand[dq].setdefault(sl, set()).add(jid)

    # Supply counts: tổng thể và theo từng ngành (đếm DISTINCT survey_id đạt self_rating >= 65)
    skill_supply_surveys: Dict[str, set] = {}
    industry_skill_supply_surveys: Dict[str, Dict[str, set]] = {m["key"]: {} for m in INDUSTRY_META}
    quarterly_soft_supply: Dict[int, Dict[str, set]] = {q: {} for q in (1, 2, 3, 4)}

    all_year_survey_ids = set().union(*selected_year_survey_ids_by_q.values())
    relevant_survey_ids = selected_survey_ids | all_year_survey_ids

    if relevant_survey_ids:
        ssr_rows = db.execute(
            text("SELECT survey_id, skill_id, self_rating FROM survey_skill_ratings")
        ).fetchall()
        for sid, skill_id, rating in ssr_rows:
            if sid not in relevant_survey_ids:
                continue
            if rating is None or rating < PROFICIENCY_THRESHOLD:
                continue
            sinfo = skill_id_to_info.get(skill_id)
            if not sinfo:
                continue
            sl = sinfo["skill_name"].lower()
            sr_info = surveys_by_id.get(sid)
            if not sr_info:
                continue

            if sid in selected_survey_ids:
                skill_supply_surveys.setdefault(sl, set()).add(sid)
                ik = sr_info["industry_key"]
                if ik in industry_skill_supply_surveys:
                    industry_skill_supply_surveys[ik].setdefault(sl, set()).add(sid)

            if sl in soft_skill_names_lower:
                dy, dq = _quarter_of_date(sr_info["eff_date"])
                if dy == sel_year and dq in (1, 2, 3, 4):
                    quarterly_soft_supply[dq].setdefault(sl, set()).add(sid)

    # ── 6. Tính danh sách kỹ năng tổng quan (Demand, Supply, Gap từ TỔNG tử số & mẫu số) ──
    all_skill_keys = set(skill_demand_jobs.keys()) | set(skill_supply_surveys.keys())
    all_skills_list: List[Dict[str, Any]] = []
    for sl in all_skill_keys:
        d_cnt = len(skill_demand_jobs.get(sl, set()))
        s_cnt = len(skill_supply_surveys.get(sl, set()))
        demand_pct = round((d_cnt / total_jobs) * 100.0, 1) if total_jobs > 0 else None
        supply_pct = round((s_cnt / total_surveys) * 100.0, 1) if total_surveys > 0 else None
        gap_pct = round(demand_pct - supply_pct, 1) if (demand_pct is not None and supply_pct is not None) else None

        all_skills_list.append({
            "skill": canonical_skill_names.get(sl, sl.title()),
            "demand": demand_pct,
            "supply": supply_pct,
            "gap": gap_pct,
            "demand_count": d_cnt,
            "supply_count": s_cnt if total_surveys > 0 else None,
            "demand_denom": total_jobs,
            "supply_denom": total_surveys,
            "industry": skill_name_to_industry.get(sl, "Khác"),
        })

    # Sắp xếp Top 5 kỹ năng thiếu hụt: ưu tiên theo gap giảm dần nếu có đủ dữ liệu gap, ngược lại theo demand giảm dần
    if has_gap_data:
        all_skills_list.sort(
            key=lambda x: (
                x["gap"] if x["gap"] is not None else -9999.0,
                x["demand"] if x["demand"] is not None else -9999.0,
            ),
            reverse=True,
        )
    elif has_job_data:
        all_skills_list.sort(
            key=lambda x: (x["demand"] if x["demand"] is not None else -9999.0, x["demand_count"]),
            reverse=True,
        )
    else:
        all_skills_list.sort(
            key=lambda x: (x["supply"] if x["supply"] is not None else -9999.0),
            reverse=True,
        )

    # Nếu có job data: ưu tiên các kỹ năng thực sự có nhu cầu tuyển dụng (demand_count > 0)
    if has_job_data:
        top_shortage_skills = [s for s in all_skills_list if s["demand_count"] > 0][:5]
    else:
        top_shortage_skills = [s for s in all_skills_list if (s["supply_count"] or 0) > 0][:5]

    # Tính Gap trung bình trên các kỹ năng có nhu cầu tuyển dụng (Demand > 0) khi đủ dữ liệu
    avg_gap_pct: Optional[float] = None
    if has_gap_data and top_shortage_skills:
        valid_gaps = [s["gap"] for s in top_shortage_skills if s["gap"] is not None]
        if valid_gaps:
            avg_gap_pct = round(sum(valid_gaps) / len(valid_gaps), 1)

    # Tính khoảng lương thực tế từ job_postings trong bộ lọc
    all_salaries = [s for p in active_provinces for s in p["salaries"]]
    avg_salary_str = _format_salary_range(all_salaries)

    # ── 7. Phân bổ ngành nghề (Pie/Doughnut) ──
    industry_distribution: List[Dict[str, Any]] = []
    if has_job_data:
        for m in INDUSTRY_META:
            cnt = industry_job_totals[m["key"]]
            share = round((cnt / total_jobs) * 100.0, 1) if total_jobs > 0 else None
            industry_distribution.append({
                "key": m["key"],
                "label": m["label"],
                "count": cnt,
                "share_pct": share,
                "color": m["color"],
            })

    # ── 8. Chuỗi thời gian 4 Quý trong năm sel_year (từ dữ liệu thực tế DB) ──
    year_has_any_jobs = sum(quarterly_total_jobs.values()) > 0
    quarterly_trend = {
        "year": sel_year,
        "has_data": year_has_any_jobs,
        "labels": [f"Q{q}/{sel_year}" for q in (1, 2, 3, 4)],
        "totals": [quarterly_total_jobs[q] for q in (1, 2, 3, 4)],
        "datasets": [
            {
                "key": m["key"],
                "label": m["label"],
                "color": m["color"],
                "data": [quarterly_industry_counts[q][m["key"]] for q in (1, 2, 3, 4)],
            }
            for m in INDUSTRY_META
        ] if year_has_any_jobs else [],
    }

    # ── 9. So sánh cơ cấu tỷ trọng (Kỳ hiện tại vs Kỳ liền trước từ DB thực tế) ──
    comparison_industries = []
    if has_job_data or prev_total_jobs > 0:
        for m in INDUSTRY_META:
            cur_c = industry_job_totals[m["key"]]
            prv_c = prev_industry_counts[m["key"]]
            cur_pct = round((cur_c / total_jobs) * 100.0, 1) if total_jobs > 0 else None
            prv_pct = round((prv_c / prev_total_jobs) * 100.0, 1) if prev_total_jobs > 0 else None
            growth_pct = (
                round(((cur_c - prv_c) / prv_c) * 100.0, 1)
                if (prv_c > 0 and total_jobs > 0)
                else None
            )
            share_diff_pp = (
                round(cur_pct - prv_pct, 1)
                if (cur_pct is not None and prv_pct is not None)
                else None
            )
            comparison_industries.append({
                "key": m["key"],
                "label": m["label"],
                "color": m["color"],
                "count_from": prv_c,
                "pct_from": prv_pct,
                "count_to": cur_c,
                "pct_to": cur_pct,
                "growth_pct": growth_pct,
                "share_diff_pp": share_diff_pp,
            })

    period_comparison = {
        "from_label": prev_pinfo["period_label"],
        "to_label": pinfo["period_label"],
        "from_total_jobs": prev_total_jobs,
        "to_total_jobs": total_jobs,
        "has_data": has_job_data,
        "has_prev_data": prev_total_jobs > 0,
        "industries": comparison_industries if has_job_data else [],
    }

    # ── 10. Kỹ năng mềm / chuyển giao (Soft Skills) theo bộ lọc ──
    soft_skills_list: List[Dict[str, Any]] = []
    if has_data:
        for sl in soft_skill_names_lower:
            d_cnt = len(skill_demand_jobs.get(sl, set()))
            s_cnt = len(skill_supply_surveys.get(sl, set()))
            if d_cnt == 0 and s_cnt == 0:
                continue
            d_pct = round((d_cnt / total_jobs) * 100.0, 1) if total_jobs > 0 else None
            s_pct = round((s_cnt / total_surveys) * 100.0, 1) if total_surveys > 0 else None
            g_pct = round(d_pct - s_pct, 1) if (d_pct is not None and s_pct is not None) else None
            soft_skills_list.append({
                "skill": canonical_skill_names.get(sl, sl.title()),
                "demand": d_pct,
                "supply": s_pct,
                "gap": g_pct,
                "demand_count": d_cnt,
                "supply_count": s_cnt if total_surveys > 0 else None,
                "industry": "Tất cả ngành",
                "shortIndustry": "Liên ngành",
            })
        soft_skills_list.sort(
            key=lambda x: (
                x["demand"] if x["demand"] is not None else -999.0,
                x["gap"] if x["gap"] is not None else -999.0,
            ),
            reverse=True,
        )

    # Chuỗi xu hướng kỹ năng mềm theo 4 quý trong năm sel_year
    top_soft_keys = [s["skill"].lower() for s in soft_skills_list[:5]]
    soft_colors = ["#0fa39e", "#dc2626", "#f59e0b", "#7c3aed", "#2563eb"]
    soft_quarterly_series = []
    if year_has_any_jobs and top_soft_keys:
        for idx, sl in enumerate(top_soft_keys):
            demand_series = []
            gap_series = []
            for q in (1, 2, 3, 4):
                qj = quarterly_total_jobs[q]
                qs = len(selected_year_survey_ids_by_q[q])
                dc = len(quarterly_soft_demand[q].get(sl, set()))
                sc = len(quarterly_soft_supply[q].get(sl, set()))
                dp = round((dc / qj) * 100.0, 1) if qj > 0 else None
                sp = round((sc / qs) * 100.0, 1) if qs > 0 else None
                gp = round(dp - sp, 1) if (dp is not None and sp is not None) else None
                demand_series.append(dp)
                gap_series.append(gp)
            soft_quarterly_series.append({
                "name": canonical_skill_names.get(sl, sl.title()),
                "color": soft_colors[idx % len(soft_colors)],
                "demand_series": demand_series,
                "gap_series": gap_series,
            })

    # ── 11. Chi tiết từng ngành nghề (cho Khám phá ngành, Admin, Nhà tuyển dụng) ──
    industries_detail: Dict[str, Dict[str, Any]] = {}
    for m in INDUSTRY_META:
        ik = m["key"]
        ij = industry_job_totals[ik]
        isur = industry_survey_totals[ik]
        ind_sals = [s for p in active_provinces for s in p["industry_salaries"][ik]]
        ind_skill_keys = set(industry_skill_demand_jobs[ik].keys()) | set(industry_skill_supply_surveys[ik].keys())
        ind_skills: List[Dict[str, Any]] = []
        for sl in ind_skill_keys:
            dc = len(industry_skill_demand_jobs[ik].get(sl, set()))
            sc = len(industry_skill_supply_surveys[ik].get(sl, set()))
            if dc == 0 and sc == 0:
                continue
            dp = round((dc / ij) * 100.0, 1) if ij > 0 else None
            sp = round((sc / isur) * 100.0, 1) if isur > 0 else None
            gp = round(dp - sp, 1) if (dp is not None and sp is not None) else None
            ind_skills.append({
                "skill": canonical_skill_names.get(sl, sl.title()),
                "demand": dp,
                "supply": sp,
                "gap": gp,
                "demand_count": dc,
                "supply_count": sc if isur > 0 else None,
            })

        if ij > 0 and isur > 0:
            ind_skills.sort(
                key=lambda x: (
                    x["gap"] if x["gap"] is not None else -9999.0,
                    x["demand"] if x["demand"] is not None else -9999.0,
                ),
                reverse=True,
            )
        else:
            ind_skills.sort(
                key=lambda x: (
                    x["demand"] if x["demand"] is not None else -9999.0,
                    x["supply"] if x["supply"] is not None else -9999.0,
                ),
                reverse=True,
            )

        industries_detail[ik] = {
            "key": ik,
            "label": m["label"],
            "has_data": (ij > 0 or isur > 0),
            "has_job_data": ij > 0,
            "has_survey_data": isur > 0,
            "has_gap_data": (ij > 0 and isur > 0),
            "jobs": ij,
            "surveys": isur,
            "avg_salary": _format_salary_range(ind_sals),
            "top_missing": ind_skills[0]["skill"] if ind_skills else None,
            "skills": ind_skills[:10],
        }

    # ── 12. Thông báo trạng thái dữ liệu (phân biệt rõ: rỗng vs thiếu 1 vế vs đầy đủ) ──
    empty_message = None
    partial_notice = None
    if not has_data:
        empty_message = f"Chưa có dữ liệu cho địa bàn {loc_name} trong kỳ {pinfo['period_label']}."
    elif has_job_data and not has_survey_data:
        partial_notice = (
            f"Kỳ {pinfo['period_label']} ({loc_name}) có {total_jobs:,} tin tuyển dụng nhưng chưa có dữ liệu "
            f"khảo sát nguồn cung (CV), nên chỉ hiển thị Nhu cầu (Demand) — chưa đủ dữ liệu tính Supply và Gap."
        )
    elif has_survey_data and not has_job_data:
        partial_notice = (
            f"Kỳ {pinfo['period_label']} ({loc_name}) có {total_surveys:,} hồ sơ khảo sát nhưng chưa có dữ liệu "
            f"tin tuyển dụng, nên chưa đủ dữ liệu tính Demand và Gap."
        )

    return {
        "filters": {
            "location_id": loc_id,
            "location_name": loc_name,
            "period_type": pinfo["period_type"],
            "year": sel_year,
            "quarter": sel_quarter,
            "period_code": pinfo["period_code"],
            "period_label": pinfo["period_label"],
            "start_date": start_d.isoformat(),
            "end_date": end_d.isoformat(),
        },
        "data_availability": {
            "has_data": has_data,
            "has_job_data": has_job_data,
            "has_survey_data": has_survey_data,
            "has_gap_data": has_gap_data,
            "empty_message": empty_message,
            "partial_notice": partial_notice,
            "provinces_included_count": len(active_provinces),
            "provinces_included": [
                {
                    "location_id": p["location_id"],
                    "location_name": p["location_name"],
                    "job_count": p["job_count"],
                    "survey_count": p["survey_count"],
                }
                for p in active_provinces
            ],
        },
        "kpi": {
            "total_jobs": total_jobs,
            "total_surveys": total_surveys,
            "avg_gap_pct": avg_gap_pct,
            "active_skills_count": len([s for s in all_skills_list if s["demand_count"] > 0 or (s["supply_count"] or 0) > 0]),
            "avg_salary": avg_salary_str,
        },
        "top_shortage_skills": top_shortage_skills,
        "all_skills": all_skills_list[:25],
        "industry_distribution": industry_distribution,
        "quarterly_trend": quarterly_trend,
        "period_comparison": period_comparison,
        "soft_skills": soft_skills_list,
        "soft_skills_quarterly_trend": {
            "year": sel_year,
            "has_data": bool(soft_quarterly_series),
            "quarters": [f"Q{q}/{sel_year}" for q in (1, 2, 3, 4)],
            "skills": soft_quarterly_series,
        },
        "industries_detail": industries_detail,
    }


def _format_salary_range(salaries: List[Tuple[int, int]]) -> Optional[str]:
    if not salaries:
        return None
    avg_min = sum(s[0] for s in salaries) / len(salaries)
    avg_max = sum(s[1] for s in salaries) / len(salaries)
    # Tự nhận diện đơn vị VND (>= 100.000) hay triệu đồng
    if avg_min >= 100000:
        avg_min /= 1_000_000.0
        avg_max /= 1_000_000.0
    return f"{avg_min:.0f}–{avg_max:.0f}tr"
