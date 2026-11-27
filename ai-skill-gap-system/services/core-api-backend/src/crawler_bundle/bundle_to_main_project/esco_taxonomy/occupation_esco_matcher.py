"""
occupation_esco_matcher.py
=============================================================================
Module Ánh xạ Vị trí/Chức danh sang Nghề nghiệp Chuẩn ESCO & Bổ sung Kỹ năng

NGUYÊN TẮC KIẾN TRÚC QUAN TRỌNG:
1. CHỨC DANH ≠ KỸ NĂNG (Position/Occupation ≠ Skill):
   - Chức danh (Business Analyst, Tester, Kế toán trưởng...) là thực thể Vị trí/Nghề nghiệp.
   - Tuyệt đối không lưu tên chức danh vào danh mục kỹ năng (skills).
   - Chức danh được trích xuất và ánh xạ sang chuẩn nghề nghiệp ESCO (occupations).

2. PHÂN TÁCH NGUỒN KỸ NĂNG MINH BẠCH:
   - explicit: Kỹ năng xuất hiện trực tiếp trong văn bản tin tuyển dụng / CV (do LLM trích xuất).
   - esco_essential: Kỹ năng cốt lõi bắt buộc theo chuẩn ESCO của nghề nghiệp đó.
   - esco_optional: Kỹ năng bổ trợ / tự chọn theo chuẩn ESCO của nghề nghiệp đó.

3. QUY TẮC PHÂN TÍCH THỊ TRƯỜNG & ĐÁNH GIÁ:
   - Tính toán Skill Demand, Skill Supply, Skill Gap, MSPS: MẶC ĐỊNH CHỈ DÙNG source='explicit'.
   - evaluate_gold_standard.py: CHỈ so khớp explicit skills với Gold Standard (không đưa ESCO inferred vào TP/FP).
   - Kỹ năng ESCO inferred chỉ dùng cho: Gợi ý nghề nghiệp (Career Pathway), Gợi ý khóa học đào tạo (Course Recommendation), và Hệ thống ontology hỗ trợ.
=============================================================================
"""

import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
import csv
import json
from typing import Dict, List, Any, Optional, Tuple
from difflib import SequenceMatcher

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TAXONOMY_FILE = os.path.join(BASE_DIR, "skill_taxonomy_model_4nganh_FINAL.json")
OCCUPATIONS_CSV = os.path.join(BASE_DIR, "occupations_en.csv")
RELATIONS_CSV = os.path.join(BASE_DIR, "occupationSkillRelations_en.csv")


def clean_label(text: str) -> str:
    """Chuẩn hóa chuỗi văn bản phục vụ so khớp."""
    if not text:
        return ""
    t = str(text).lower().strip()
    t = re.sub(r"\[.*?\]|\(.*?\)", "", t)
    t = re.sub(r"[\r\n\t]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t.strip(".,;:*-_`'\"")


class OccupationEscoMatcher:
    """
    Module quản lý việc ánh xạ Vị trí công việc (Position) sang nghề nghiệp ESCO
    và truy xuất các kỹ năng bổ trợ (Essential & Optional Skills) theo chuẩn EU.
    """

    def __init__(
        self,
        taxonomy_path: str = TAXONOMY_FILE,
        occupations_csv: str = OCCUPATIONS_CSV,
        relations_csv: str = RELATIONS_CSV
    ):
        self.taxonomy_path = taxonomy_path
        self.occupations_csv = occupations_csv
        self.relations_csv = relations_csv

        # Bộ nhớ đệm danh mục nghề nghiệp trong 4 ngành
        self.taxonomy_occupations: List[Dict[str, Any]] = []
        # Tra cứu nhanh theo tên nghề chuẩn và alias
        self.occupation_name_index: Dict[str, Dict[str, Any]] = {}

        # Tra cứu quan hệ kỹ năng ESCO từ CSV khi cần fallback
        self.esco_all_occupations: Dict[str, Dict[str, Any]] = {}
        self.esco_skills_by_uri: Dict[str, Dict[str, List[Dict[str, str]]]] = {}

        self._load_taxonomy()

    def _load_taxonomy(self):
        """Nạp 416 nghề nghiệp đã được cấu trúc trong taxonomy 4 ngành mục tiêu."""
        if os.path.exists(self.taxonomy_path):
            try:
                with open(self.taxonomy_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.taxonomy_occupations = data.get("occupations", [])
                
                for occ in self.taxonomy_occupations:
                    name = occ.get("occupation_name", "")
                    clean_n = clean_label(name)
                    if clean_n:
                        self.occupation_name_index[clean_n] = occ
                        
                print(f"[OccupationEscoMatcher] Đã nạp {len(self.taxonomy_occupations)} nghề chuẩn từ taxonomy 4 ngành.")
            except Exception as e:
                print(f"[OccupationEscoMatcher] Cảnh báo lỗi nạp taxonomy: {e}")

    def _load_full_esco_relations(self):
        """Nạp dữ liệu quan hệ nghề - kỹ năng từ occupationSkillRelations_en.csv khi cần."""
        if self.esco_skills_by_uri:
            return  # Đã nạp trước đó

        print("[OccupationEscoMatcher] Đang nạp quan hệ kỹ năng từ occupationSkillRelations_en.csv...")
        if os.path.exists(self.relations_csv):
            with open(self.relations_csv, "r", encoding="utf-8", errors="replace") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    occ_uri = row.get("occupationUri", "").strip()
                    rel_type = row.get("relationType", "essential").strip().lower()
                    sk_label = row.get("skillLabel", "").strip()
                    sk_uri = row.get("skillUri", "").strip()
                    sk_type = row.get("skillType", "skill/competence").strip()

                    if not occ_uri or not sk_label:
                        continue

                    if occ_uri not in self.esco_skills_by_uri:
                        self.esco_skills_by_uri[occ_uri] = {"essential": [], "optional": []}

                    bucket = "essential" if rel_type == "essential" else "optional"
                    self.esco_skills_by_uri[occ_uri][bucket].append({
                        "skill_name": sk_label,
                        "esco_skill_uri": sk_uri,
                        "skill_type": "KNOWLEDGE" if "knowledge" in sk_type.lower() else "HARD"
                    })
            print(f"[OccupationEscoMatcher] Đã lập chỉ mục kỹ năng cho {len(self.esco_skills_by_uri)} nghề nghiệp ESCO.")

    def match_occupation(
        self,
        position_name: str,
        industry: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Tìm kiếm nghề nghiệp chuẩn ESCO phù hợp nhất cho vị trí công việc.
        Thứ tự ưu tiên:
        1. Exact Match trong Taxonomy 4 ngành
        2. Known Aliases / Semantic mapping (VD: Business Analyst, Tester, Developer...)
        3. Fuzzy Token Matching / Substring Matching
        """
        if not position_name:
            return None

        p_clean = clean_label(position_name)
        if not p_clean:
            return None

        # Danh sách các tiền tố cấp bậc cần làm sạch để tìm nghề gốc
        clean_candidates = [p_clean]
        stripped = re.sub(
            r"^(chuyên viên|nhân viên|kỹ sư|cán bộ|trưởng nhóm|trưởng phòng|giám sát|senior|junior|lead|thực tập sinh|thực tập|fresher|intern)\s+",
            "", p_clean
        ).strip()
        if stripped and stripped != p_clean and len(stripped) >= 2:
            clean_candidates.append(stripped)

        # Bảng ánh xạ phổ biến giữa chức danh tiếng Việt / tiếng Anh và Occupation ESCO
        KNOWN_MAPPINGS = {
            # Business Analyst
            "business analyst": "ICT business analyst",
            "ict business analyst": "ICT business analyst",
            "ba": "ICT business analyst",
            "chuyên viên ba": "ICT business analyst",
            "chuyên viên phân tích nghiệp vụ": "ICT business analyst",
            "phân tích nghiệp vụ": "ICT business analyst",
            "nhân viên phân tích nghiệp vụ": "ICT business analyst",
            "chuyên viên phân tích nghiệp vụ (ba)": "ICT business analyst",
            "system analyst": "ICT system analyst",

            # Software Tester
            "tester": "software tester",
            "software tester": "software tester",
            "kiểm thử phần mềm": "software tester",
            "kiểm thử": "software tester",
            "nhân viên kiểm thử": "software tester",
            "nhân viên kiểm thử phần mềm": "software tester",
            "chuyên viên kiểm thử": "software tester",
            "chuyên viên kiểm thử phần mềm": "software tester",
            "manual tester": "software tester",
            "automation tester": "software tester",
            "qa tester": "software tester",
            "qc tester": "software tester",
            "qa/qc": "software tester",
            "qa engineer": "software tester",
            "qc engineer": "software tester",

            # Data Engineer
            "data engineer": "data engineer",
            "kỹ sư dữ liệu": "data engineer",
            "data engineering": "data engineer",
            "big data engineer": "data engineer",

            # Kế toán
            "kế toán": "accountant",
            "kế toán viên": "accountant",
            "nhân viên kế toán": "accountant",
            "kế toán tổng hợp": "accountant",
            "kế toán thuế": "tax accountant",
            "kế toán nội bộ": "accountant",
            "accountant": "accountant",
            "general accountant": "accountant",
            "tax accountant": "tax accountant",

            # Kế toán trưởng / Quản lý kế toán
            "kế toán trưởng": "accounting manager",
            "chief accountant": "accounting manager",
            "trưởng phòng kế toán": "accounting manager",
            "accounting manager": "accounting manager",

            # Developer / Lập trình viên
            "developer": "software developer",
            "lập trình viên": "software developer",
            "software developer": "software developer",
            "software engineer": "software developer",
            "kỹ sư phần mềm": "software developer",
            "frontend developer": "software developer",
            "lập trình viên frontend": "software developer",
            "backend developer": "software developer",
            "lập trình viên backend": "software developer",
            "fullstack developer": "software developer",
            "web developer": "software developer",

            # Logistics & Xuất nhập khẩu
            "nhân viên xuất nhập khẩu": "import export specialist",
            "chuyên viên xuất nhập khẩu": "import export specialist",
            "xuất nhập khẩu": "import export specialist",
            "import export specialist": "import export specialist",
            "nhân viên logistics": "logistics and distribution manager",
            "chuyên viên logistics": "logistics and distribution manager",
            "logistics coordinator": "rail logistics coordinator",

            # Du lịch & Dịch vụ
            "lễ tân": "hospitality establishment receptionist",
            "nhân viên lễ tân": "hospitality establishment receptionist",
            "lễ tân khách sạn": "hospitality establishment receptionist",
            "receptionist": "hospitality establishment receptionist",
            "hotel receptionist": "hospitality establishment receptionist",
        }

        # 1. Kiểm tra bảng ánh xạ trực tiếp
        for cand in clean_candidates:
            target_name = KNOWN_MAPPINGS.get(cand)
            if target_name:
                for occ in self.taxonomy_occupations:
                    if clean_label(occ.get("occupation_name", "")) == clean_label(target_name):
                        return {
                            "occupation_name": occ["occupation_name"],
                            "esco_occupation_uri": occ.get("esco_occupation_uri"),
                            "isco_group_code": occ.get("isco_group_code"),
                            "industry_groups": occ.get("industry_groups", []),
                            "match_score": 1.0,
                            "match_method": "direct_alias",
                            "raw_occupation_data": occ
                        }

        # 2. Exact match trong Taxonomy 4 ngành
        for cand in clean_candidates:
            if cand in self.occupation_name_index:
                occ = self.occupation_name_index[cand]
                return {
                    "occupation_name": occ["occupation_name"],
                    "esco_occupation_uri": occ.get("esco_occupation_uri"),
                    "isco_group_code": occ.get("isco_group_code"),
                    "industry_groups": occ.get("industry_groups", []),
                    "match_score": 1.0,
                    "match_method": "exact_taxonomy",
                    "raw_occupation_data": occ
                }

        # 3. Fuzzy search trong Taxonomy 4 ngành
        best_match = None
        best_score = 0.0

        for cand in clean_candidates:
            for occ in self.taxonomy_occupations:
                occ_name = occ.get("occupation_name", "")
                occ_clean = clean_label(occ_name)
                
                # Substring match
                if cand in occ_clean or occ_clean in cand:
                    score = len(cand) / max(len(occ_clean), 1)
                    if score > best_score and score >= 0.6:
                        best_score = score
                        best_match = occ

                # SequenceMatcher ratio
                ratio = SequenceMatcher(None, cand, occ_clean).ratio()
                if ratio > best_score and ratio >= 0.72:
                    best_score = ratio
                    best_match = occ

        if best_match:
            return {
                "occupation_name": best_match["occupation_name"],
                "esco_occupation_uri": best_match.get("esco_occupation_uri"),
                "isco_group_code": best_match.get("isco_group_code"),
                "industry_groups": best_match.get("industry_groups", []),
                "match_score": round(best_score, 3),
                "match_method": "fuzzy_taxonomy",
                "raw_occupation_data": best_match
            }

        return None

    def get_esco_skills_for_position(
        self,
        position_name: str,
        include_optional: bool = False,
        max_skills: int = 15
    ) -> Dict[str, Any]:
        """
        Cho một tên vị trí (Position/Chức danh):
        1. Tìm occupation ESCO phù hợp.
        2. Lấy danh sách kỹ năng cốt lõi (essential skills).
        3. Lấy danh sách kỹ năng bổ trợ (optional skills nếu cần).
        """
        match = self.match_occupation(position_name)
        if not match:
            return {
                "position_name": position_name,
                "matched_occupation": None,
                "essential_skills": [],
                "optional_skills": []
            }

        occ_data = match.get("raw_occupation_data", {})
        essential_list = []
        optional_list = []

        # 1. Lấy từ Taxonomy Model nếu đã nạp
        if "essential_skills" in occ_data:
            for s in occ_data["essential_skills"][:max_skills]:
                essential_list.append({
                    "skill_name": s.get("skill_name"),
                    "esco_skill_uri": s.get("esco_skill_uri"),
                    "skill_type": "KNOWLEDGE" if s.get("skill_type") == "knowledge" else "HARD",
                    "relation_type": "essential",
                    "source": "esco_essential"
                })

        if include_optional and "optional_skills" in occ_data:
            for s in occ_data["optional_skills"][:max_skills]:
                optional_list.append({
                    "skill_name": s.get("skill_name"),
                    "esco_skill_uri": s.get("esco_skill_uri"),
                    "skill_type": "KNOWLEDGE" if s.get("skill_type") == "knowledge" else "HARD",
                    "relation_type": "optional",
                    "source": "esco_optional"
                })

        # 2. Nếu taxonomy chưa có list skill chi tiết, fallback sang CSV
        if not essential_list and match.get("esco_occupation_uri"):
            self._load_full_esco_relations()
            uri = match["esco_occupation_uri"]
            if uri in self.esco_skills_by_uri:
                for s in self.esco_skills_by_uri[uri]["essential"][:max_skills]:
                    essential_list.append({
                        **s,
                        "relation_type": "essential",
                        "source": "esco_essential"
                    })
                if include_optional:
                    for s in self.esco_skills_by_uri[uri]["optional"][:max_skills]:
                        optional_list.append({
                            **s,
                            "relation_type": "optional",
                            "source": "esco_optional"
                        })

        return {
            "position_name": position_name,
            "matched_occupation": {
                "occupation_name": match["occupation_name"],
                "esco_occupation_uri": match["esco_occupation_uri"],
                "isco_group_code": match.get("isco_group_code"),
                "match_score": match.get("match_score"),
                "match_method": match.get("match_method")
            },
            "essential_skills": essential_list,
            "optional_skills": optional_list
        }

    def enrich_job_skills_with_esco(
        self,
        explicit_skills: List[Dict[str, Any]],
        position_name: str,
        include_optional: bool = False,
        max_inferred: int = 10
    ) -> Dict[str, Any]:
        """
        Làm giàu kỹ năng cho tin tuyển dụng (Job Posting):
        - Giữ nguyên các explicit skills (gán source='explicit').
        - Bổ sung kỹ năng ESCO từ chức danh (gán source='esco_essential' / 'esco_optional').
        - Khử trùng lặp giữa explicit và inferred.
        """
        # Chuẩn hóa explicit skills
        clean_explicit = []
        explicit_names = set()

        for s in explicit_skills:
            name = s.get("skill_name", "").strip()
            if not name:
                continue
            item = dict(s)
            item["source"] = "explicit"
            clean_explicit.append(item)
            explicit_names.add(name.lower())

        # Lấy kỹ năng từ ESCO theo position
        esco_data = self.get_esco_skills_for_position(
            position_name=position_name,
            include_optional=include_optional,
            max_skills=max_inferred
        )

        inferred_skills = []
        for es in esco_data["essential_skills"]:
            ename = es["skill_name"]
            if ename.lower() not in explicit_names:
                inferred_skills.append(es)
                explicit_names.add(ename.lower())

        if include_optional:
            for os_item in esco_data["optional_skills"]:
                oname = os_item["skill_name"]
                if oname.lower() not in explicit_names:
                    inferred_skills.append(os_item)
                    explicit_names.add(oname.lower())

        return {
            "position_name": position_name,
            "matched_occupation": esco_data["matched_occupation"],
            "explicit_skills_count": len(clean_explicit),
            "inferred_skills_count": len(inferred_skills),
            "explicit_skills": clean_explicit,
            "esco_inferred_skills": inferred_skills,
            "combined_skills": clean_explicit + inferred_skills
        }

    def get_esco_skills_by_occupation_uri(
        self,
        occupation_uri: str,
        include_optional: bool = False,
        max_skills: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Hàm chuẩn: occupation_id/uri -> list {skill_name, esco_skill_uri, relation_type: essential|optional}
        """
        if not occupation_uri:
            return []

        # 1. Tìm trong taxonomy 4 ngành
        for occ in self.taxonomy_occupations:
            if occ.get("esco_occupation_uri") == occupation_uri or str(occ.get("occupation_id")) == str(occupation_uri):
                skills = []
                for s in occ.get("essential_skills", [])[:max_skills]:
                    skills.append({
                        "skill_name": s.get("skill_name"),
                        "esco_skill_uri": s.get("esco_skill_uri"),
                        "skill_type": "KNOWLEDGE" if s.get("skill_type") == "knowledge" else "HARD",
                        "relation_type": "essential",
                        "source": "esco_essential"
                    })
                if include_optional:
                    for s in occ.get("optional_skills", [])[:max_skills]:
                        skills.append({
                            "skill_name": s.get("skill_name"),
                            "esco_skill_uri": s.get("esco_skill_uri"),
                            "skill_type": "KNOWLEDGE" if s.get("skill_type") == "knowledge" else "HARD",
                            "relation_type": "optional",
                            "source": "esco_optional"
                        })
                if skills:
                    return skills

        # 2. Fallback sang relations CSV
        self._load_full_esco_relations()
        skills = []
        if occupation_uri in self.esco_skills_by_uri:
            for s in self.esco_skills_by_uri[occupation_uri]["essential"][:max_skills]:
                skills.append({**s, "relation_type": "essential", "source": "esco_essential"})
            if include_optional:
                for s in self.esco_skills_by_uri[occupation_uri]["optional"][:max_skills]:
                    skills.append({**s, "relation_type": "optional", "source": "esco_optional"})
        return skills

    def resolve_or_create_skill_in_db(
        self,
        cur,
        skill_name: str,
        skill_type_str: str = "HARD",
        esco_uri: Optional[str] = None,
        is_esco: bool = False
    ) -> int:
        """
        Tra cứu hoặc tạo mới kỹ năng trong bảng `skills`:
        - Ưu tiên: Tra cứu khớp tên (LOWER) hoặc khớp esco_uri.
        - Nếu chưa có: Tạo mới với cờ `is_esco = 1` và lưu esco_uri tham chiếu.
        """
        s_clean = skill_name.strip()
        s_low = s_clean.lower()

        # 1. Tìm theo tên
        cur.execute("SELECT skill_id FROM skills WHERE LOWER(skill_name) = %s LIMIT 1;", (s_low,))
        row = cur.fetchone()
        if row:
            return row[0]

        # 2. Tìm theo esco_uri
        if esco_uri:
            cur.execute("SELECT skill_id FROM skills WHERE esco_uri = %s LIMIT 1;", (esco_uri,))
            row = cur.fetchone()
            if row:
                return row[0]

        # 3. Tạo mới vào bảng skills
        type_map = {
            "HARD": 1,
            "SOFT": 2,
            "TOOL": 3,
            "KNOWLEDGE": 4,
            "CERTIFICATION": 5,
            "LANGUAGE": 6
        }
        st_id = type_map.get(skill_type_str.upper(), 1)
        cur.execute("""
            INSERT INTO skills (skill_name, skill_type_id, esco_uri, is_esco)
            VALUES (%s, %s, %s, %s);
        """, (s_clean, st_id, esco_uri, 1 if is_esco else 0))
        return cur.lastrowid

    def sync_job_with_separated_sources(
        self,
        conn,
        job_id: int,
        position_name: str,
        explicit_skills: List[Dict[str, Any]],
        include_optional: bool = False,
        max_inferred: int = 10
    ) -> Dict[str, Any]:
        """
        Ghi toàn bộ kỹ năng của việc làm vào MySQL:
        - explicit_skills ghi với source = 'explicit'.
        - esco_essential skills ghi với source = 'esco_essential' (hoặc 'esco_optional').
        - QUY TẮC: Trùng skill (cùng skill_id đã có explicit): GIỮ explicit, KHÔNG ghi đè thành esco.
        """
        cur = conn.cursor()

        # Tìm job_id chính xác trong bảng jobs (hỗ trợ cả raw_job_id và job_id)
        cur.execute("SELECT job_id FROM jobs WHERE raw_job_id = %s OR job_id = %s LIMIT 1;", (str(job_id), str(job_id)))
        row = cur.fetchone()
        if not row:
            cur.close()
            return {"error": f"Job {job_id} không tìm thấy trong bảng jobs"}
        real_job_id = row[0]

        # Cập nhật esco_occupation_uri trong bảng positions nếu khớp
        matched_occ = self.match_occupation(position_name)
        if matched_occ and matched_occ.get("esco_occupation_uri"):
            cur.execute("""
                UPDATE positions
                SET esco_occupation_uri = %s,
                    isco_group_code = %s
                WHERE position_name = %s;
            """, (matched_occ["esco_occupation_uri"], matched_occ.get("isco_group_code"), position_name))

        # 1. Lưu explicit skills
        explicit_skill_ids = set()
        explicit_names = set()

        for s in explicit_skills:
            s_name = s.get("skill_name", "").strip()
            if not s_name:
                continue
            s_type = (s.get("skill_type") or "HARD").upper()
            sid = self.resolve_or_create_skill_in_db(cur, s_name, skill_type_str=s_type, is_esco=False)
            explicit_skill_ids.add(sid)
            explicit_names.add(s_name.lower())

            cur.execute("""
                INSERT INTO job_skills (job_id, skill_id, requirement_level, extraction_source, confidence_score, source)
                VALUES (%s, %s, %s, 'llm', 1.0, 'explicit')
                ON DUPLICATE KEY UPDATE source = 'explicit';
            """, (real_job_id, sid, s.get("requirement_level", "required")))

        # 2. Lưu ESCO inferred skills (chỉ kỹ năng chưa có trong explicit)
        esco_data = self.get_esco_skills_for_position(
            position_name=position_name,
            include_optional=include_optional,
            max_skills=max_inferred
        )

        all_esco_items = []
        for es in esco_data.get("essential_skills", []):
            all_esco_items.append((es, "esco_essential"))
        if include_optional:
            for os_item in esco_data.get("optional_skills", []):
                all_esco_items.append((os_item, "esco_optional"))

        added_esco_count = 0
        added_esco_samples = []

        for es, src_tag in all_esco_items:
            ename = es["skill_name"].strip()
            if ename.lower() in explicit_names:
                continue  # Bỏ qua vì đã có trong explicit

            e_sid = self.resolve_or_create_skill_in_db(
                cur,
                skill_name=ename,
                skill_type_str=es.get("skill_type", "HARD"),
                esco_uri=es.get("esco_skill_uri"),
                is_esco=True
            )

            if e_sid in explicit_skill_ids:
                continue  # Trùng skill_id -> Bỏ qua, giữ explicit

            # INSERT IGNORE đảm bảo nếu cặp (job_id, skill_id) đã có thì không ghi đè
            cur.execute("""
                INSERT IGNORE INTO job_skills (job_id, skill_id, requirement_level, extraction_source, confidence_score, source)
                VALUES (%s, %s, 'preferred', 'llm', 0.85, %s);
            """, (real_job_id, e_sid, src_tag))
            if cur.rowcount > 0:
                added_esco_count += 1
                added_esco_samples.append(ename)

        conn.commit()
        cur.close()

        return {
            "job_id": job_id,
            "position_name": position_name,
            "matched_occupation": matched_occ["occupation_name"] if matched_occ else None,
            "esco_occupation_uri": matched_occ["esco_occupation_uri"] if matched_occ else None,
            "explicit_count": len(explicit_skill_ids),
            "esco_count": added_esco_count,
            "esco_samples": added_esco_samples[:4]
        }


# =============================================================================
# DEMO THỰC THI (CHO 2 OCCUPATION: BUSINESS ANALYST & SOFTWARE TESTER)
# =============================================================================

def run_demo():
    print("=" * 80)
    print("DEMO ÁNH XẠ CHỨC DANH SANG ESCO OCCUPATION & BỔ SUNG KỸ NĂNG (PART B)")
    print("=" * 80)

    matcher = OccupationEscoMatcher()

    demo_cases = [
        {
            "position": "Business Analyst",
            "sample_explicit_skills": [
                {"skill_name": "SQL", "skill_type": "HARD"},
                {"skill_name": "Jira", "skill_type": "TOOL"},
                {"skill_name": "Kỹ năng giao tiếp", "skill_type": "SOFT"}
            ]
        },
        {
            "position": "Tester",
            "sample_explicit_skills": [
                {"skill_name": "Kiểm thử phần mềm", "skill_type": "HARD"},
                {"skill_name": "Postman", "skill_type": "TOOL"},
                {"skill_name": "Làm việc nhóm", "skill_type": "SOFT"}
            ]
        }
    ]

    for case in demo_cases:
        pos = case["position"]
        expl = case["sample_explicit_skills"]

        print(f"\n[DEMO VỊ TRÍ]: '{pos}'")
        res = matcher.enrich_job_skills_with_esco(expl, pos, include_optional=True, max_inferred=8)

        occ = res["matched_occupation"]
        if occ:
            print(f"  -> Khớp Nghề ESCO: '{occ['occupation_name']}'")
            print(f"  -> ESCO URI: {occ['esco_occupation_uri']}")
            print(f"  -> Phương thức khớp: {occ['match_method']} (Độ tương đồng: {occ['match_score']})")
        else:
            print("  -> Không tìm thấy nghề nghiệp ESCO tương ứng.")

        print(f"\n  * KỸ NĂNG THỰC TẾ TRONG JD (source='explicit' - DÙNG CHO DEMAND & EVALUATE):")
        for s in res["explicit_skills"]:
            print(f"    - [{s['source'].upper()}] {s['skill_name']} ({s['skill_type']})")

        print(f"\n  * KỸ NĂNG GỢI Ý TỪ ESCO (source='esco_essential' - CHỈ DÙNG CHO ĐÀO TẠO / GỢI Ý KHÓA HỌC):")
        for s in res["esco_inferred_skills"]:
            print(f"    - [{s['source']}] {s['skill_name']} ({s['skill_type']})")

    print("\n" + "=" * 80)
    print("KẾT THÚC DEMO THÀNH CÔNG!")
    print("=" * 80)


if __name__ == "__main__":
    run_demo()
