"""Read-only access to the crawler's MySQL 3NF database.

This module is deliberately separate from ``src.database``.  The application
database remains ``skillgap_db``; this data source is used only for analytics
and never exposes INSERT/UPDATE/DELETE helpers.
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Dict, Iterator, List

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection
from src.services.reporting_scope import job_period_predicate, worker_batch


CRAWLER_DB_HOST = os.getenv("CRAWLER_DB_HOST", "127.0.0.1")
CRAWLER_DB_PORT = int(os.getenv("CRAWLER_DB_PORT", "3306"))
CRAWLER_DB_NAME = os.getenv("CRAWLER_DB_NAME", "skill_intelligence")
CRAWLER_DB_USER = os.getenv("CRAWLER_DB_USER", "")
CRAWLER_DB_PASSWORD = os.getenv("CRAWLER_DB_PASSWORD", "")


def _build_url() -> str:
    if not CRAWLER_DB_USER:
        raise RuntimeError("Thiếu CRAWLER_DB_USER; không dùng tài khoản mặc định cho crawler DB")
    host = CRAWLER_DB_HOST
    # If running on Windows host (not inside container) and host is host.docker.internal, fallback to 127.0.0.1
    if host == "host.docker.internal" and not os.path.exists("/.dockerenv"):
        host = "127.0.0.1"
    return (
        f"mysql+pymysql://{CRAWLER_DB_USER}:{CRAWLER_DB_PASSWORD}"
        f"@{host}:{CRAWLER_DB_PORT}/{CRAWLER_DB_NAME}?charset=utf8mb4"
    )


class CrawlerDataSource:
    """Small SELECT-only repository for ``skill_intelligence``."""

    def __init__(self):
        self.engine = create_engine(
            _build_url(),
            pool_pre_ping=True,
            pool_recycle=300,
            connect_args={"connect_timeout": 5, "read_timeout": 20},
        )

    @contextmanager
    def connection(self) -> Iterator[Connection]:
        with self.engine.connect() as conn:
            yield conn

    def health(self) -> Dict[str, Any]:
        with self.connection() as conn:
            return dict(conn.execute(text(
                "SELECT DATABASE() AS database_name, @@hostname AS hostname, "
                "@@port AS port, VERSION() AS mysql_version"
            )).mappings().one())

    def table_counts(self, tables: List[str]) -> Dict[str, int]:
        # Table names are selected by application code, never user input.
        with self.connection() as conn:
            result: Dict[str, int] = {}
            for table in tables:
                result[table] = int(conn.execute(text(f"SELECT COUNT(*) FROM `{table}`")).scalar_one())
            return result

    def location_counts(self) -> List[Dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute(text(
                "SELECT r.location, COUNT(DISTINCT j.job_id) AS total "
                "FROM jobs j "
                "JOIN jobs_raw r ON r.job_id = j.raw_job_id "
                "GROUP BY r.location ORDER BY total DESC, r.location"
            )).mappings().all()
            return [dict(row) for row in rows]

    def dashboard_locations(self, period: str | None = None) -> List[Dict[str, Any]]:
        """Build location options according to the selected reporting period.
        - For 2025: return strictly all, HN, HCM, CT with counts from historical_period_analytics.
        - For 2026/other: return crawler locations from clean 1,000 jobs.
        """
        period_key = (period or "2026_Q2").upper()
        if period_key.startswith("2025"):
            loc_names = {
                "all": "Toàn quốc (Tất cả địa bàn)",
                "HN": "Hà Nội",
                "HCM": "TP. Hồ Chí Minh",
                "CT": "Cần Thơ"
            }
            with self.connection() as conn:
                rows = conn.execute(text(
                    "SELECT location_id, total_jobs, total_cvs "
                    "FROM historical_period_analytics "
                    "WHERE dataset_id = :ds_id"
                ), {"ds_id": period_key}).mappings().all()

                if not rows:
                    rows = conn.execute(text(
                        "SELECT location_id, total_jobs, total_cvs "
                        "FROM historical_period_analytics "
                        "WHERE dataset_id = '2025_ALL'"
                    ), {}).mappings().all()

                row_map = {str(r["location_id"]): (int(r["total_jobs"]), int(r["total_cvs"])) for r in rows}
                
                res = []
                for code in ["all", "HN", "HCM", "CT"]:
                    tj, tcv = row_map.get(code, (0, 0))
                    res.append({
                        "id": code,
                        "name": loc_names.get(code, code),
                        "job_count": tj,
                        "cv_count": tcv,
                        "has_data": tj > 0
                    })
                return res

        with self.connection() as conn:
            # 1. Các kỳ chưa công bố dữ liệu -> Trả về Empty state chuẩn (không dùng dữ liệu kỳ khác)
            if period_key == "2026_Q1":
                return [{"id": "all", "name": "Toàn bộ địa bàn (Chưa có dữ liệu)", "job_count": 0, "cv_count": 0, "has_data": False}]


            # 2. Kiểm tra trạng thái publish thực sự hợp lệ của Q4 (chỉ hợp lệ khi Quality Gate PASS & Published)
            is_q4_published = False
            q4_cvs_count = 0
            if period_key in ("2026_Q4", "2026_ALL"):
                pub_val = conn.execute(text("SELECT is_published FROM reporting_datasets WHERE dataset_id = '2026_Q4'")).scalar_one_or_none()
                q4_batch = conn.execute(text("SELECT quality_gate_passed, published_to_dashboard, cleaned_workers_count FROM crawler_batches WHERE batch_code = 'BATCH_2026_Q4_INGEST'")).mappings().first()
                is_q4_published = bool(pub_val) and bool(q4_batch and q4_batch["quality_gate_passed"] == 1 and q4_batch["published_to_dashboard"] == 1)
                q4_cvs_count = int((q4_batch or {}).get("cleaned_workers_count") or 0)

            if period_key == "2026_Q4" and not is_q4_published:
                return [{"id": "all", "name": "Toàn bộ địa bàn (Chưa có dữ liệu)", "job_count": 0, "cv_count": 0, "has_data": False}]

            job_period_filter = "WHERE j.status='active' AND " + job_period_predicate(period_key)
            if period_key == "2026_Q2":
                job_period_filter = "WHERE " + job_period_predicate(period_key)
            elif period_key == "2026_Q4":
                job_period_filter = "WHERE j.status='active' AND " + job_period_predicate(period_key)
            elif period_key == "2026_ALL":
                job_period_filter = "WHERE j.status='active' AND " + job_period_predicate(period_key)

            raw_rows = conn.execute(text(
                f"SELECT r.location, COUNT(DISTINCT j.job_id) AS total "
                f"FROM jobs j "
                f"JOIN jobs_raw r ON r.job_id = j.raw_job_id "
                f"{job_period_filter} "
                f"GROUP BY r.location ORDER BY total DESC"
            )).mappings().all()

            single_names = set()
            for r in raw_rows:
                loc = str(r["location"] or "")
                parts = loc.replace(" và ", ",").split(",")
                for p in parts:
                    clean_p = p.strip()
                    if clean_p and "nơi khác" not in clean_p:
                        single_names.add(clean_p)

            total_jobs = int(conn.execute(text(f"SELECT COUNT(DISTINCT j.job_id) FROM jobs j {job_period_filter}")).scalar_one())
            if period_key == "2026_Q4":
                total_cvs = int(conn.execute(text("SELECT COUNT(DISTINCT w.worker_id) FROM workers w JOIN cvs_raw c ON c.cv_id=w.cv_raw_id WHERE w.is_active=1 AND c.batch_id='BATCH_2026_Q4_INGEST'")).scalar_one())
            elif period_key == "2026_Q2":
                total_cvs = int(conn.execute(text("SELECT COUNT(DISTINCT w.worker_id) FROM workers w LEFT JOIN cvs_raw c ON c.cv_id=COALESCE(w.cv_raw_id, w.worker_id) WHERE w.is_active=1 AND (c.batch_id='BATCH_2026_Q2_VERIFIED' OR (c.batch_id IS NULL AND w.worker_id <= 500))")).scalar_one())
            elif period_key == "2026_Q3":
                total_cvs = int(conn.execute(text("SELECT COUNT(DISTINCT w.worker_id) FROM workers w LEFT JOIN cvs_raw c ON c.cv_id=COALESCE(w.cv_raw_id, w.worker_id) WHERE w.is_active=1 AND (c.batch_id='BATCH_2026_Q3_RAW' OR (c.batch_id IS NULL AND w.worker_id BETWEEN 501 AND 1500))")).scalar_one())
            else:
                total_cvs = int(conn.execute(text("SELECT COUNT(DISTINCT w.worker_id) FROM workers w LEFT JOIN cvs_raw c ON c.cv_id=COALESCE(w.cv_raw_id, w.worker_id) WHERE w.is_active=1 AND c.batch_id IN ('BATCH_2026_Q2_VERIFIED', 'BATCH_2026_Q4_INGEST')")).scalar_one())

            loc_list = []
            for name in single_names:
                sub_filter = f"AND {job_period_filter.removeprefix('WHERE ')}" if job_period_filter else ""
                cnt = int(conn.execute(text(
                    f"SELECT COUNT(DISTINCT j.job_id) FROM jobs j "
                    f"JOIN jobs_raw r ON r.job_id = j.raw_job_id "
                    f"WHERE r.location LIKE :loc_pattern {sub_filter}"
                ), {"loc_pattern": f"%{name}%"}).scalar_one())
                if cnt > 0:
                    loc_list.append({"id": name, "name": name, "job_count": cnt, "cv_count": 0, "has_data": True})

            loc_list.sort(key=lambda x: (-x["job_count"], x["name"]))
            locations = [{"id": "all", "name": "Toàn quốc / Toàn bộ địa bàn",
                          "job_count": total_jobs, "cv_count": total_cvs, "has_data": True}]
            locations.extend(loc_list)
            locations.append({"id": "unknown", "name": "Chưa xác định", "job_count": 0,
                              "cv_count": 0, "has_data": False})
            return locations

    def skill_type_counts(self) -> Dict[str, int]:
        with self.connection() as conn:
            rows = conn.execute(text(
                "SELECT st.type_code, COUNT(s.skill_id) AS total "
                "FROM skill_types st LEFT JOIN skills s ON s.skill_type_id = st.skill_type_id "
                "GROUP BY st.type_code ORDER BY st.type_code"
            )).mappings().all()
            return {str(row["type_code"]): int(row["total"]) for row in rows}

    def job_skill_type_links(self) -> Dict[str, int]:
        with self.connection() as conn:
            rows = conn.execute(text(
                "SELECT st.type_code, COUNT(*) AS total FROM job_skills js "
                "JOIN skills s ON s.skill_id = js.skill_id "
                "JOIN skill_types st ON st.skill_type_id = s.skill_type_id "
                "GROUP BY st.type_code ORDER BY st.type_code"
            )).mappings().all()
            return {str(row["type_code"]): int(row["total"]) for row in rows}

    def explicit_and_enrichment_links(self) -> List[Dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute(text(
                "SELECT extraction_source, source, COUNT(*) AS total "
                "FROM job_skills GROUP BY extraction_source, source "
                "ORDER BY extraction_source, source"
            )).mappings().all()
            return [dict(row) for row in rows]

    def analytics(self, location: str = "all", industry: str | None = None, industry_id: int | None = None,
                  skill_type: str = "ALL", period: str | None = None) -> Dict[str, Any]:
        """Return the dashboard payload from crawler 3NF without legacy fallback."""
        # ── Dispatch by Unified Reporting Period ──────────────────────────
        period_key = (period or "2026_Q2").upper()
        if period_key.startswith("2025") or period_key in ("2025_ALL", "2025_Q1", "2025_Q2", "2025_Q3", "2025_Q4"):
            return self.historical_analytics(location=location, period=period_key, industry=industry, industry_id=industry_id, skill_type=skill_type)
        if period_key == "2026_Q1":
            return self.empty_q1_analytics(location=location)

        q4_cvs_count = 0
        if period_key == "2026_Q4":
            with self.connection() as conn:
                is_pub = conn.execute(text("SELECT is_published FROM reporting_datasets WHERE dataset_id = '2026_Q4'")).scalar_one_or_none()
                q4_batch = conn.execute(text("SELECT quality_gate_passed, published_to_dashboard, cleaned_workers_count FROM crawler_batches WHERE batch_code = 'BATCH_2026_Q4_INGEST'")).mappings().first()
                q4_valid = bool(is_pub) and bool(q4_batch and q4_batch["quality_gate_passed"] == 1 and q4_batch["published_to_dashboard"] == 1)
                q4_cvs_count = int((q4_batch or {}).get("cleaned_workers_count") or 0)
            if not q4_valid:
                return self.pending_q4_analytics(location=location)

        from src.services.observed_analytics import compute_observed_analytics
        if industry_id is not None:
            industry = {1: 'IT', 2: 'tourism', 3: 'logistics', 4: 'economics'}.get(industry_id)
            if industry is None:
                raise ValueError('Ngành nghề không thuộc 4 ngành nghiên cứu')
        return compute_observed_analytics(self, period_key, location, industry, skill_type)



    def reporting_datasets(self) -> List[Dict[str, Any]]:
        """Return list of reporting datasets with quality status and provenance."""
        with self.connection() as conn:
            rows = conn.execute(text(
                "SELECT dataset_id, dataset_name, reporting_year, reporting_quarter, "
                "source_type, status, status_label, provenance, raw_jobs_count, cleaned_jobs_count, "
                "validated_cvs_count, observation_date_range, data_update_date, is_published, notes "
                "FROM reporting_datasets ORDER BY reporting_year DESC, reporting_quarter ASC"
            )).mappings().all()
            result = [dict(row) for row in rows]
            for item in result:
                if item['dataset_id'] == '2026_Q3':
                    item['raw_jobs_count'] = int(conn.execute(text("SELECT COUNT(*) FROM jobs_raw WHERE batch_id='BATCH_2026_Q3_RAW'")).scalar_one())
                    item['cleaned_jobs_count'] = int(conn.execute(text("SELECT COUNT(DISTINCT j.job_id) FROM jobs j WHERE j.status='active' AND " + job_period_predicate('2026_Q3'))).scalar_one())
                    if item['cleaned_jobs_count']:
                        item['status'] = 'CLEANED_PREVIEW'
                        item['status_label'] = 'Đã làm sạch · Chưa kiểm định'
                        item['source_type'] = 'CRAWLER_CLEANED_UNVALIDATED'
                        item['provenance'] = 'Số CLEANED tính trực tiếp từ jobs và jobs_raw; chưa chứng nhận Validation.'
            return result

    def empty_q1_analytics(self, location: str = "all") -> Dict[str, Any]:
        """Status payload for Q1/2026 (No data collected yet)."""
        return {
            "filters": {"location_id": location, "location_name": location, "period_label": "Quý 1/2026 (Chưa có dữ liệu)"},
            "status": "UNAVAILABLE",
            "status_label": "Chưa có dữ liệu",
            "is_published": False,
            "is_reconstructed": False,
            "provenance": "Chưa có dữ liệu. Kế hoạch thu thập từ các nguồn trực tuyến bắt đầu từ Q2/2026.",
            "data_update_date": "01/01/2026",
            "observation_date_range": "01/01/2026 - 31/03/2026",
            "message": "Chưa có dữ liệu. Kế hoạch thu thập từ các nguồn trực tuyến bắt đầu từ Q2/2026.",
            "reporting_period": {
                "period_id": "2026_Q1",
                "year": 2026,
                "quarter": "Q1",
                "status": "UNAVAILABLE",
                "status_label": "Chưa có dữ liệu",
                "source_type": "ONLINE_CRAWLER"
            },
            "data_availability": {
                "has_data": False,
                "has_job_data": False,
                "has_survey_data": False,
                "has_gap_data": False,
                "provinces_included": []
            },
            "kpi": {
                "total_jobs": 0,
                "raw_jobs": 0,
                "total_surveys": 0,
                "avg_gap_pct": None,
                "active_skills_count": 0,
                "avg_salary": "Chưa có dữ liệu",
                "subtitle": "Chưa có dữ liệu. Kế hoạch thu thập từ các nguồn trực tuyến bắt đầu từ Q2/2026."
            },
            "top_shortage_skills": [],
            "all_skills": [],
            "industry_distribution": [],
            "quarterly_trend": {"has_data": False, "labels": [], "datasets": []},
            "period_comparison": {"has_data": False, "industries": []},
            "soft_skills": [],
            "soft_skills_by_industry": {"all": []},
            "soft_skills_quarterly_trend": {"has_data": False, "quarters": [], "skills": []},
            "industries_detail": {
                "IT": {"key": "IT", "label": "IT & Công nghệ", "has_data": False, "skills": [], "top_10": []},
                "tourism": {"key": "tourism", "label": "Du lịch & Khách sạn", "has_data": False, "skills": [], "top_10": []},
                "logistics": {"key": "logistics", "label": "Logistics & Chuỗi cung ứng", "has_data": False, "skills": [], "top_10": []},
                "economics": {"key": "economics", "label": "Kế toán & Tài chính", "has_data": False, "skills": [], "top_10": []}
            }
        }

    def raw_q3_analytics(self, location: str = "all") -> Dict[str, Any]:
        """Status payload for Q3/2026 (2,000 raw JDs currently being cleaned)."""
        return {
            "filters": {"location_id": location, "location_name": location, "period_label": "Quý 3/2026 (Đang làm sạch)"},
            "status": "RAW",
            "is_published": False,
            "is_reconstructed": False,
            "provenance": "2.000 tin tuyển dụng thô mới thu thập từ TopCV, đang lưu giữ riêng tại jobs_raw (chưa qua LLM enrichment & kiểm định).",
            "message": "Đang chuẩn bị dữ liệu Q3/2026 (2.000 JD thô mới cào, chưa làm sạch & chưa xác minh).",
            "reporting_period": {
                "period_id": "2026_Q3",
                "year": 2026,
                "quarter": "Q3",
                "status": "RAW",
                "source_type": "CRAWLER_RAW"
            },
            "data_availability": {
                "has_data": False,
                "has_job_data": False,
                "has_survey_data": False,
                "has_gap_data": False,
                "provinces_included": []
            },
            "kpi": {
                "total_jobs": 0,
                "raw_jobs": 2000,
                "total_surveys": 0,
                "avg_gap_pct": None,
                "active_skills_count": 0,
                "avg_salary": "Chưa có dữ liệu",
                "subtitle": "Đang chuẩn bị dữ liệu Q3/2026 (2.000 JD thô mới cào, chưa làm sạch & chưa phê duyệt)"
            },
            "top_shortage_skills": [],
            "all_skills": [],
            "industry_distribution": [],
            "quarterly_trend": {"has_data": False, "labels": [], "datasets": []},
            "period_comparison": {"has_data": False, "industries": []},
            "soft_skills": [],
            "soft_skills_by_industry": {"all": []},
            "soft_skills_quarterly_trend": {"has_data": False, "quarters": [], "skills": []},
            "industries_detail": {
                "IT": [], "tourism": [], "logistics": [], "economics": []
            }
        }

    def pending_q4_analytics(self, location: str = "all") -> Dict[str, Any]:
        """Status payload for Q4/2026 (Pending, no processed data yet)."""
        return {
            "filters": {"location_id": location, "location_name": location, "period_label": "Quý 4/2026 (Chưa có dữ liệu)"},
            "status": "PENDING",
            "is_published": False,
            "is_reconstructed": False,
            "provenance": "Kỳ phân tích dự kiến, hiện chưa có bộ dữ liệu được phê duyệt.",
            "message": "Chưa có dữ liệu đã xử lý cho Quý 4/2026.",
            "reporting_period": {
                "period_id": "2026_Q4",
                "year": 2026,
                "quarter": "Q4",
                "status": "PENDING",
                "source_type": "PENDING"
            },
            "data_availability": {
                "has_data": False,
                "has_job_data": False,
                "has_survey_data": False,
                "has_gap_data": False,
                "provinces_included": []
            },
            "kpi": {
                "total_jobs": 0,
                "total_surveys": 0,
                "avg_gap_pct": None,
                "active_skills_count": 0,
                "avg_salary": "Chưa có dữ liệu",
                "subtitle": "Chưa có dữ liệu đã xử lý cho Quý 4/2026"
            },
            "top_shortage_skills": [],
            "all_skills": [],
            "industry_distribution": [],
            "quarterly_trend": {"has_data": False, "labels": [], "datasets": []},
            "period_comparison": {"has_data": False, "industries": []},
            "soft_skills": [],
            "soft_skills_by_industry": {"all": []},
            "soft_skills_quarterly_trend": {"has_data": False, "quarters": [], "skills": []},
            "industries_detail": {
                "IT": [], "tourism": [], "logistics": [], "economics": []
            }
        }

    def historical_analytics(self, location: str = "all", period: str = "2025_ALL",
                             industry: str | None = None, industry_id: int | None = None,
                             skill_type: str = "ALL") -> Dict[str, Any]:
        """Return analytics for 2025 historical reconstructed datasets from MySQL."""
        parts = period.split("_")
        year = int(parts[0]) if parts[0].isdigit() else 2025
        quarter = parts[1] if len(parts) > 1 else "ALL"

        loc_key = location if location in ("all", "HN", "HCM", "CT") else "all"
        is_national = (loc_key == "all")

        industry_map = {"IT": "IT", "tourism": "TOURISM", "Du lịch": "TOURISM",
                        "logistics": "LOGISTICS", "Logistics": "LOGISTICS",
                        "economics": "ACCOUNTING", "Kinh tế": "ACCOUNTING", "accounting": "ACCOUNTING"}
        ind_code_filter = industry_map.get(industry or "")

        with self.connection() as conn:
            # 1. KPI
            kpi_row = conn.execute(text(
                "SELECT total_jobs, total_cvs, avg_gap_pct, active_skills_count, salary_range, subtitle, provenance "
                "FROM historical_period_analytics "
                "WHERE reporting_year = :year AND reporting_quarter = :quarter AND location_id = :loc"
            ), {"year": year, "quarter": quarter, "loc": loc_key}).mappings().first()

            if not kpi_row:
                # fallback to 'all' if loc_key not found
                kpi_row = conn.execute(text(
                    "SELECT total_jobs, total_cvs, avg_gap_pct, active_skills_count, salary_range, subtitle, provenance "
                    "FROM historical_period_analytics "
                    "WHERE reporting_year = :year AND reporting_quarter = :quarter AND location_id = 'all'"
                ), {"year": year, "quarter": quarter}).mappings().first()

            total_jobs = int(kpi_row["total_jobs"]) if kpi_row else 0
            total_cvs = int(kpi_row["total_cvs"]) if kpi_row else 0
            avg_gap = float(kpi_row["avg_gap_pct"]) if kpi_row and kpi_row["avg_gap_pct"] is not None else 15.0
            salary = str(kpi_row["salary_range"]) if kpi_row else "14–32tr"
            subtitle = str(kpi_row["subtitle"]) if kpi_row else "Dữ liệu lịch sử tái dựng năm 2025"

            # 2. Industry Distribution (4 core industries only, Nông nghiệp excluded from in-scope list)
            ind_rows = conn.execute(text(
                "SELECT industry_code AS `key`, industry_name_vi AS label, jobs_count AS `count`, share_pct "
                "FROM historical_industry_analytics "
                "WHERE reporting_year = :year AND reporting_quarter = :quarter AND location_id = :loc AND is_in_scope = 1 "
                "ORDER BY jobs_count DESC"
            ), {"year": year, "quarter": quarter, "loc": loc_key}).mappings().all()

            ind_color_map = {
                "IT": "#3B82F6",
                "TOURISM": "#14B8A6",
                "LOGISTICS": "#F59E0B",
                "ACCOUNTING": "#8B5CF6",
                "tourism": "#14B8A6",
                "logistics": "#F59E0B",
                "economics": "#8B5CF6"
            }
            industry_distribution = [
                {
                    "key": str(r["key"]),
                    "label": str(r["label"]),
                    "count": int(r["count"]),
                    "share_pct": float(r["share_pct"]) if r["share_pct"] is not None else 0.0,
                    "color": ind_color_map.get(str(r["key"]), "#3B82F6")
                }
                for r in ind_rows
            ]
            ind_jobs_map = {str(r["key"]): int(r["count"]) for r in ind_rows}

            # 3. Skills (Top shortage & all skills)
            skill_where = [
                "reporting_year = :year",
                "reporting_quarter = :quarter",
                "location_id = :loc"
            ]
            s_params: Dict[str, Any] = {"year": year, "quarter": quarter, "loc": loc_key}

            if ind_code_filter:
                skill_where.append("industry_code = :ind_code")
                s_params["ind_code"] = ind_code_filter
            else:
                skill_where.append("industry_code = 'ALL'")

            if skill_type and skill_type != "ALL":
                skill_where.append("skill_type = :stype")
                s_params["stype"] = skill_type

            s_query = " AND ".join(skill_where)
            skill_db_rows = conn.execute(text(f"""
                SELECT skill_name, skill_type, demand_pct, supply_pct, gap_pct, rank_num, is_soft_skill
                FROM historical_skill_analytics
                WHERE {s_query}
                ORDER BY rank_num ASC
            """), s_params).mappings().all()

            tvi_map = {
                "HARD": "Chuyên môn",
                "TOOL": "Công cụ",
                "KNOWLEDGE": "Kiến thức",
                "LANGUAGE": "Ngoại ngữ",
                "CERTIFICATION": "Chứng chỉ",
                "SOFT": "Kỹ năng mềm"
            }

            skills_list = []
            for r in skill_db_rows:
                dp = float(r["demand_pct"]) if r["demand_pct"] is not None else None
                sp = float(r["supply_pct"]) if r["supply_pct"] is not None else None
                gp = float(r["gap_pct"]) if r["gap_pct"] is not None else (round(dp - sp, 1) if (dp is not None and sp is not None) else None)
                st_code = str(r["skill_type"])
                skills_list.append({
                    "skill_id": int(r["rank_num"]),
                    "skill": str(r["skill_name"]),
                    "skill_name": str(r["skill_name"]),
                    "type": st_code,
                    "type_vi": tvi_map.get(st_code, st_code),
                    "demand": dp,
                    "supply": sp,
                    "gap": gp,
                    "demand_count": int(round(dp * total_jobs / 100)) if dp and total_jobs else 0,
                    "supply_count": int(round(sp * total_cvs / 100)) if sp and total_cvs else None,
                    "supply_denom": total_cvs,
                    "demand_denom": total_jobs,
                })

            top_shortage_skills = skills_list[:5]
            all_skills = skills_list[:100]

            # 4. Soft Skills
            soft_db_rows = conn.execute(text(
                "SELECT skill_name, skill_type, demand_pct, supply_pct, gap_pct, rank_num "
                "FROM historical_skill_analytics "
                "WHERE reporting_year = :year AND reporting_quarter = :quarter AND location_id = :loc AND is_soft_skill = 1 "
                "ORDER BY rank_num ASC"
            ), {"year": year, "quarter": quarter, "loc": loc_key}).mappings().all()

            overall_soft_skills = []
            for r in soft_db_rows:
                dp = float(r["demand_pct"]) if r["demand_pct"] is not None else 0.0
                sp = float(r["supply_pct"]) if r["supply_pct"] is not None else None
                gp = float(r["gap_pct"]) if r["gap_pct"] is not None else (round(dp - sp, 1) if (dp is not None and sp is not None) else None)
                st_code = str(r["skill_type"])
                overall_soft_skills.append({
                    "skill": str(r["skill_name"]),
                    "skill_name": str(r["skill_name"]),
                    "type": st_code,
                    "type_vi": tvi_map.get(st_code, st_code),
                    "industry": "Liên ngành (Toàn thị trường)",
                    "shortIndustry": "Liên ngành",
                    "demand": dp,
                    "supply": sp,
                    "gap": gp,
                    "demand_count": int(round(dp * total_jobs / 100)) if dp and total_jobs else 0,
                    "supply_count": int(round(sp * total_cvs / 100)) if sp and total_cvs else None,
                    "demand_denom": total_jobs,
                    "supply_denom": total_cvs,
                })

            soft_skills_by_industry: Dict[str, List[Dict[str, Any]]] = {
                "all": overall_soft_skills,
                "IT": overall_soft_skills[:8],
                "tourism": overall_soft_skills[:8],
                "logistics": overall_soft_skills[:8],
                "economics": overall_soft_skills[:8]
            }

            # 5. Industries Detail (Technical skills for 4 industries)
            ind_code_to_key = {"IT": "IT", "TOURISM": "tourism", "LOGISTICS": "logistics", "ACCOUNTING": "economics"}
            ind_labels_map = {
                "IT": "IT & Công nghệ",
                "tourism": "Du lịch & Khách sạn",
                "logistics": "Logistics & Chuỗi cung ứng",
                "economics": "Kế toán & Tài chính"
            }
            ind_salary_map = {
                "IT": "18–45tr",
                "tourism": "12–25tr",
                "logistics": "14–30tr",
                "economics": "13–28tr"
            }
            industries_detail: Dict[str, Any] = {}

            for db_ind_code, key_name in ind_code_to_key.items():
                ind_skills_rows = conn.execute(text(
                    "SELECT skill_name, skill_type, demand_pct, supply_pct, gap_pct, rank_num "
                    "FROM historical_skill_analytics "
                    "WHERE reporting_year = :year AND reporting_quarter = :quarter AND location_id = :loc "
                    "AND industry_code = :ind AND skill_type IN ('HARD', 'TOOL', 'KNOWLEDGE', 'CERTIFICATION') "
                    "ORDER BY rank_num ASC"
                ), {"year": year, "quarter": quarter, "loc": loc_key, "ind": db_ind_code}).mappings().all()

                ind_jobs = int(ind_jobs_map.get(db_ind_code, 0))
                ind_cvs = int(round(total_cvs * (ind_jobs / total_jobs))) if (total_jobs > 0 and total_cvs > 0) else 0

                ind_skills_list = []
                for r in ind_skills_rows:
                    dp = float(r["demand_pct"]) if r["demand_pct"] is not None else 0.0
                    sp = float(r["supply_pct"]) if r["supply_pct"] is not None else None
                    gp = float(r["gap_pct"]) if r["gap_pct"] is not None else (round(dp - sp, 1) if (dp is not None and sp is not None) else None)
                    st_code = str(r["skill_type"])
                    ind_skills_list.append({
                        "skill_id": int(r["rank_num"]),
                        "skill": str(r["skill_name"]),
                        "skill_name": str(r["skill_name"]),
                        "skill_type": st_code,
                        "type": st_code,
                        "type_vi": tvi_map.get(st_code, st_code),
                        "demand": dp,
                        "supply": sp,
                        "gap": gp,
                        "demand_count": int(round(dp * ind_jobs / 100)) if dp and ind_jobs else 0,
                        "supply_count": int(round(sp * ind_cvs / 100)) if sp and ind_cvs else None,
                        "demand_denom": ind_jobs,
                        "supply_denom": ind_cvs,
                    })

                industries_detail[key_name] = {
                    "key": key_name,
                    "label": ind_labels_map.get(key_name, key_name),
                    "has_data": ind_jobs > 0,
                    "has_job_data": ind_jobs > 0,
                    "has_survey_data": ind_cvs > 0,
                    "has_gap_data": (ind_jobs > 0 and ind_cvs > 0),
                    "jobs": ind_jobs,
                    "surveys": ind_cvs,
                    "avg_salary": ind_salary_map.get(key_name, "15–35tr"),
                    "top_missing": ind_skills_list[0]["skill"] if ind_skills_list else "Chưa có dữ liệu",
                    "skills": ind_skills_list,
                    "top_10": ind_skills_list[:10],
                }

            # 6. Quarterly Trend across 4 quarters of 2025
            trend_rows = conn.execute(text(
                "SELECT reporting_quarter, industry_code, jobs_count "
                "FROM historical_industry_analytics "
                "WHERE reporting_year = :year AND reporting_quarter IN ('Q1', 'Q2', 'Q3', 'Q4') "
                "AND location_id = :loc AND is_in_scope = 1 "
                "ORDER BY reporting_quarter ASC, industry_code ASC"
            ), {"year": year, "loc": loc_key}).mappings().all()

            trend_map: Dict[str, Dict[str, int]] = {"IT": {}, "TOURISM": {}, "LOGISTICS": {}, "ACCOUNTING": {}}
            for tr in trend_rows:
                trend_map.setdefault(str(tr["industry_code"]), {})[str(tr["reporting_quarter"])] = int(tr["jobs_count"])

            quarterly_trend = {
                "has_data": True,
                "labels": ["Quý 1/2025", "Quý 2/2025", "Quý 3/2025", "Quý 4/2025"],
                "datasets": [
                    {"industry": "IT", "label": "IT & Công nghệ", "data": [trend_map["IT"].get("Q1", 0), trend_map["IT"].get("Q2", 0), trend_map["IT"].get("Q3", 0), trend_map["IT"].get("Q4", 0)]},
                    {"industry": "TOURISM", "label": "Du lịch & Khách sạn", "data": [trend_map["TOURISM"].get("Q1", 0), trend_map["TOURISM"].get("Q2", 0), trend_map["TOURISM"].get("Q3", 0), trend_map["TOURISM"].get("Q4", 0)]},
                    {"industry": "LOGISTICS", "label": "Logistics & XNK", "data": [trend_map["LOGISTICS"].get("Q1", 0), trend_map["LOGISTICS"].get("Q2", 0), trend_map["LOGISTICS"].get("Q3", 0), trend_map["LOGISTICS"].get("Q4", 0)]},
                    {"industry": "ACCOUNTING", "label": "Kinh tế & Tài chính", "data": [trend_map["ACCOUNTING"].get("Q1", 0), trend_map["ACCOUNTING"].get("Q2", 0), trend_map["ACCOUNTING"].get("Q3", 0), trend_map["ACCOUNTING"].get("Q4", 0)]}
                ]
            }

            # 7. Metadata from reporting_datasets
            ds_meta = conn.execute(text(
                "SELECT status, status_label, provenance, observation_date_range, data_update_date, notes "
                "FROM reporting_datasets WHERE dataset_id = :ds_id"
            ), {"ds_id": period}).mappings().first()

            status_val = str(ds_meta["status"]) if ds_meta else "PUBLISHED"
            status_lbl = str(ds_meta["status_label"]) if ds_meta and ds_meta["status_label"] else "Đã thẩm định"
            prov_val = str(ds_meta["provenance"]) if ds_meta else "Dữ liệu lịch sử tái dựng từ bộ thống kê nội bộ Skill Lens Lab (năm 2025)."
            upd_date = str(ds_meta["data_update_date"]) if ds_meta and ds_meta["data_update_date"] else "31/12/2025"
            obs_range = str(ds_meta["observation_date_range"]) if ds_meta and ds_meta["observation_date_range"] else "01/01/2025 - 31/12/2025"
            notes_val = str(ds_meta["notes"]) if ds_meta and ds_meta["notes"] else ""

            period_label = f"Năm {year} ({'Toàn bộ năm' if quarter == 'ALL' else quarter})"

            return {
                "filters": {"location_id": loc_key, "location_name": loc_key, "period_label": period_label},
                "status": status_val,
                "status_label": status_lbl,
                "is_published": True,
                "is_reconstructed": True,
                "provenance": prov_val,
                "data_update_date": upd_date,
                "observation_date_range": obs_range,
                "notes": notes_val,
                "reporting_period": {
                    "period_id": period,
                    "year": year,
                    "quarter": quarter,
                    "status": status_val,
                    "status_label": status_lbl,
                    "source_type": "SYNTHETIC_RECONSTRUCTED_2025"
                },
                "data_availability": {
                    "has_data": total_jobs > 0,
                    "has_job_data": total_jobs > 0,
                    "has_survey_data": total_cvs > 0,
                    "has_gap_data": total_jobs > 0 and total_cvs > 0,
                    "provinces_included": ["Hà Nội", "TP. Hồ Chí Minh", "Cần Thơ"]
                },
                "kpi": {
                    "total_jobs": total_jobs,
                    "total_surveys": total_cvs,
                    "avg_gap_pct": avg_gap,
                    "active_skills_count": len(skills_list) if skills_list else 76,
                    "avg_salary": salary,
                    "subtitle": subtitle
                },
                "top_shortage_skills": top_shortage_skills,
                "all_skills": all_skills,
                "industry_distribution": industry_distribution,
                "quarterly_trend": quarterly_trend,
                "period_comparison": {"has_data": False, "industries": []},
                "soft_skills": overall_soft_skills,
                "soft_skills_by_industry": soft_skills_by_industry,
                "soft_skills_quarterly_trend": {"has_data": False, "quarters": [], "skills": []},
                "industries_detail": industries_detail,
            }


def crawler_data_source_configured() -> bool:
    return bool(CRAWLER_DB_USER)
