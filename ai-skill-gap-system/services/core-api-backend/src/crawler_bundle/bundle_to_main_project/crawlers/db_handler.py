"""
db_handler.py - Xử lý kết nối và thao tác với MySQL (Skill Gap Analysis)
Nhiệm vụ:
  - Quản lý kết nối pymysql an toàn (tự động kết nối lại nếu rớt kết nối)
  - Chèn mới (INSERT) hoặc cập nhật (ON DUPLICATE KEY UPDATE) vào bảng jobs_raw
  - Kiểm tra thay đổi nội dung (description, requirements, salary, deadline)
  - Quản lý bộ nhớ đệm (index) để bỏ qua việc tải trang chi tiết nếu tin không đổi
  - Thống kê tổng số lượng công việc theo từng nhóm ngành
"""

import json
import logging
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

import pymysql
from pymysql.cursors import DictCursor

from config import MYSQL_CONFIG, TABLE_NAME, ERROR_LOG_PATH


class DatabaseHandler:
    def __init__(self, config: Dict[str, Any] = None):
        """Khởi tạo kết nối MySQL."""
        self.config = config or MYSQL_CONFIG
        self.table_name = TABLE_NAME
        self.conn = None
        self._connect()

    def _connect(self):
        """Tạo kết nối đến MySQL với utf8mb4."""
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
            err_msg = f"[DatabaseHandler] Lỗi kết nối MySQL: {e}"
            print(err_msg)
            logging.error(err_msg)
            raise e

    def ensure_connected(self):
        """Đảm bảo kết nối vẫn còn hoạt động, tự động kết nối lại nếu bị ngắt."""
        try:
            if self.conn is None:
                self._connect()
            else:
                self.conn.ping(reconnect=True)
        except Exception:
            self._connect()

    def close(self):
        """Đóng kết nối cơ sở dữ liệu an toàn."""
        if self.conn and self.conn.open:
            try:
                self.conn.close()
            except Exception:
                pass

    def truncate_table(self):
        """Xóa toàn bộ dữ liệu trong bảng jobs_raw nếu người dùng muốn làm mới hoàn toàn."""
        self.ensure_connected()
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(f"TRUNCATE TABLE {self.table_name};")
            print(f"[DatabaseHandler] Đã làm trống (TRUNCATE) bảng {self.table_name} thành công.")
        except Exception as e:
            logging.error(f"Lỗi khi TRUNCATE bảng {self.table_name}: {e}")
            print(f"Lỗi TRUNCATE bảng: {e}")

    def load_existing_jobs_index(self) -> Dict[str, Dict[str, Any]]:
        """
        Nạp nhanh danh sách các job đã có trong DB vào RAM.
        Trả về dict: {job_id: {"title": title, "company_name": company_name}}
        Giúp so sánh O(1) ngay tại trang listing để bỏ qua load trang chi tiết khi không đổi.
        """
        self.ensure_connected()
        index = {}
        try:
            with self.conn.cursor() as cursor:
                sql = f"SELECT job_id, title, company_name FROM {self.table_name};"
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    jid = str(row["job_id"])
                    index[jid] = {
                        "title": (row["title"] or "").strip().lower(),
                        "company_name": (row["company_name"] or "").strip().lower()
                    }
        except Exception as e:
            logging.error(f"Lỗi khi nạp danh mục job_id từ DB: {e}")
        return index

    def mark_job_checked(self, job_id: str):
        """
        Khi tin tuyển dụng ở trang listing đã tồn tại và không đổi title + company,
        ta bỏ qua việc cào trang chi tiết nhưng vẫn cập nhật last_checked_at và duplicate_count.
        """
        self.ensure_connected()
        try:
            sql = f"""
                UPDATE {self.table_name}
                SET last_checked_at = NOW(),
                    duplicate_count = duplicate_count + 1
                WHERE job_id = %s;
            """
            with self.conn.cursor() as cursor:
                cursor.execute(sql, (str(job_id),))
        except Exception as e:
            logging.error(f"Lỗi mark_job_checked cho job_id {job_id}: {e}")

    @staticmethod
    def _format_date(date_val: Optional[str]) -> Optional[str]:
        """Chuẩn hóa chuỗi ngày tháng về định dạng YYYY-MM-DD cho cột DATE của MySQL."""
        if not date_val:
            return None
        
        date_str = str(date_val).strip()
        # Đã là định dạng chuẩn YYYY-MM-DD
        if re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            return date_str
            
        # Dạng DD/MM/YYYY
        match_vn = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", date_str)
        if match_vn:
            d, m, y = match_vn.groups()
            return f"{y}-{int(m):02d}-{int(d):02d}"
            
        # Dạng ISO 2026-03-10T...
        match_iso = re.search(r"(\d{4})-(\d{2})-(\d{2})", date_str)
        if match_iso:
            return match_iso.group(0)

        return None

    def upsert_job(self, job_data: Dict[str, Any]) -> str:
        """
        Chèn mới hoặc cập nhật một tin tuyển dụng theo chuẩn yêu cầu:
        1. NẾU job_id CHƯA tồn tại:
           -> INSERT mới, set first_seen_at = NOW(), last_checked_at = NOW(), last_updated_at = NOW()
        2. NẾU job_id ĐÃ tồn tại:
           -> Nếu nội dung (description, requirements, salary, deadline) KHÔNG đổi:
              chỉ update last_checked_at = NOW(), duplicate_count = duplicate_count + 1
              Trả về: 'unchanged'
           -> Nếu CÓ thay đổi:
              update các cột thay đổi + last_updated_at = NOW(), last_checked_at = NOW(), duplicate_count = duplicate_count + 1
              Trả về: 'updated'
        """
        self.ensure_connected()
        job_id = str(job_data.get("job_id", "")).strip()
        if not job_id:
            return "error"

        # Chuẩn bị dữ liệu định dạng chuẩn
        title = (job_data.get("title") or "")[:255]
        company_name = (job_data.get("company_name") or "")[:255]
        salary = (job_data.get("salary") or "")[:100]
        location = (job_data.get("location") or "")[:255]
        experience_required = (job_data.get("experience_required") or "")[:50]
        category = (job_data.get("category") or "")[:100]
        description = job_data.get("description") or ""
        requirements = job_data.get("requirements") or ""

        # Xử lý tags sang định dạng JSON string
        skills_req = job_data.get("skills_required_tags", [])
        if isinstance(skills_req, (list, dict)):
            skills_req_json = json.dumps(skills_req, ensure_ascii=False)
        else:
            skills_req_json = "[]"

        skills_pref = job_data.get("skills_preferred_tags", [])
        if isinstance(skills_pref, (list, dict)):
            skills_pref_json = json.dumps(skills_pref, ensure_ascii=False)
        else:
            skills_pref_json = "[]"

        posted_date = self._format_date(job_data.get("posted_date"))
        deadline = self._format_date(job_data.get("deadline"))
        job_url = (job_data.get("job_url") or "")[:500]

        try:
            with self.conn.cursor() as cursor:
                # 1. Kiểm tra xem job_id đã tồn tại chưa
                check_sql = f"""
                    SELECT description, requirements, salary, deadline 
                    FROM {self.table_name} 
                    WHERE job_id = %s;
                """
                cursor.execute(check_sql, (job_id,))
                existing = cursor.fetchone()

                if not existing:
                    # ==========================================
                    # TRƯỜNG HỢP 1: JOB MỚI HOÀN TOÀN
                    # ==========================================
                    insert_sql = f"""
                        INSERT INTO {self.table_name} (
                            job_id, title, company_name, salary, location,
                            experience_required, category, description, requirements,
                            skills_required_tags, skills_preferred_tags,
                            posted_date, deadline, job_url, duplicate_count,
                            first_seen_at, last_updated_at, last_checked_at, llm_processed
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1,
                            NOW(), NOW(), NOW(), FALSE
                        );
                    """
                    cursor.execute(insert_sql, (
                        job_id, title, company_name, salary, location,
                        experience_required, category, description, requirements,
                        skills_req_json, skills_pref_json,
                        posted_date, deadline, job_url
                    ))
                    return "inserted"

                else:
                    # ==========================================
                    # TRƯỜNG HỢP 2: JOB ĐÃ TỒN TẠI TRONG DATABASE
                    # ==========================================
                    old_desc = (existing["description"] or "").strip()
                    old_req = (existing["requirements"] or "").strip()
                    old_salary = (existing["salary"] or "").strip()
                    old_deadline = str(existing["deadline"]) if existing["deadline"] else None

                    # So sánh 4 trường quan trọng: description, requirements, salary, deadline
                    is_changed = (
                        (description.strip() != old_desc) or
                        (requirements.strip() != old_req) or
                        (salary.strip() != old_salary) or
                        (deadline != old_deadline)
                    )

                    if not is_changed:
                        # Nội dung không đổi: chỉ cập nhật last_checked_at và tăng duplicate_count
                        up_sql = f"""
                            UPDATE {self.table_name}
                            SET last_checked_at = NOW(),
                                duplicate_count = duplicate_count + 1
                            WHERE job_id = %s;
                        """
                        cursor.execute(up_sql, (job_id,))
                        return "unchanged"
                    else:
                        # Có thay đổi nội dung: cập nhật các trường và set last_updated_at = NOW()
                        up_sql = f"""
                            UPDATE {self.table_name}
                            SET title = %s,
                                company_name = %s,
                                salary = %s,
                                location = %s,
                                experience_required = %s,
                                category = %s,
                                description = %s,
                                requirements = %s,
                                skills_required_tags = %s,
                                skills_preferred_tags = %s,
                                posted_date = %s,
                                deadline = %s,
                                job_url = %s,
                                last_updated_at = NOW(),
                                last_checked_at = NOW(),
                                duplicate_count = duplicate_count + 1
                            WHERE job_id = %s;
                        """
                        cursor.execute(up_sql, (
                            title, company_name, salary, location,
                            experience_required, category, description, requirements,
                            skills_req_json, skills_pref_json,
                            posted_date, deadline, job_url,
                            job_id
                        ))
                        return "updated"

        except Exception as e:
            err_msg = f"[DatabaseHandler] Lỗi upsert_job cho job_id {job_id}: {e}"
            logging.error(err_msg)
            return "error"

    def get_category_job_count(self, category: str) -> int:
        """Đếm số lượng việc làm hiện có của một ngành cụ thể."""
        self.ensure_connected()
        try:
            with self.conn.cursor() as cursor:
                sql = f"SELECT COUNT(*) as cnt FROM {self.table_name} WHERE category = %s;"
                cursor.execute(sql, (category,))
                row = cursor.fetchone()
                return row["cnt"] if row else 0
        except Exception as e:
            logging.error(f"Lỗi khi đếm số lượng job ngành {category}: {e}")
            return 0

    def get_category_stats(self) -> Dict[str, int]:
        """
        Lấy số lượng tin tuyển dụng hiện có trong database theo từng nhóm ngành.
        """
        self.ensure_connected()
        stats = {}
        try:
            with self.conn.cursor() as cursor:
                sql = f"""
                    SELECT category, COUNT(*) as count 
                    FROM {self.table_name} 
                    GROUP BY category;
                """
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    stats[row["category"] or "Chưa phân loại"] = row["count"]
        except Exception as e:
            logging.error(f"Lỗi khi truy vấn thống kê category: {e}")
        return stats
