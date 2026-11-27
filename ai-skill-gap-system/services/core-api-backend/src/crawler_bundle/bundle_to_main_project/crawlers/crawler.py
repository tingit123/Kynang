"""
crawler.py - Engine thu thập tin tuyển dụng TopCV.vn (Phiên bản Đa Luồng Siêu Tốc)
Dự án: Skill Gap Analysis tại Đà Nẵng mở rộng (Đà Nẵng, Huế, Quảng Ngãi)
Tính năng vượt trội:
  - Cào đa luồng song song (Multi-threading ThreadPoolExecutor): tăng tốc độ gấp 5 - 8 lần
  - Vượt rào cản Cloudflare (curl_cffi impersonate Chrome 124 / cloudscraper)
  - Khử trùng lặp và cập nhật linh hoạt vào MySQL jobs_raw
  - Bỏ qua tải chi tiết nếu tin đã có không đổi title & company
  - Bắt lỗi không sập chương trình, ghi nhận lỗi vào errors.log
  - Hiển thị tiến trình thời gian thực: [idx/total] Tên việc làm...
  - Báo cáo tổng kết số lượng tin theo từng ngành trong MySQL
"""

import concurrent.futures
import functools
import json
import logging
import os
import random
import re
import sys
import threading
import time
import traceback
from typing import Any, Dict, List, Optional, Tuple

from bs4 import BeautifulSoup

# Hỗ trợ hiển thị tiếng Việt trên Terminal Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

print = functools.partial(print, flush=True)

# Kiểm tra curl_cffi / cloudscraper
try:
    from curl_cffi import requests as cffi_requests
    HAS_CURL_CFFI = True
except ImportError:
    HAS_CURL_CFFI = False

try:
    import cloudscraper
    HAS_CLOUDSCRAPER = True
except ImportError:
    HAS_CLOUDSCRAPER = False

import requests as std_requests

from config import (
    CATEGORIES,
    LOCATIONS,
    BASE_URL,
    SEARCH_URL_TEMPLATE,
    DEFAULT_HEADERS,
    MIN_DELAY_SECONDS,
    MAX_DELAY_SECONDS,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    MAX_WORKERS,
    TARGET_JOBS_PER_CATEGORY,
    ERROR_LOG_PATH,
    MAX_PAGES_PER_CATEGORY,
)
from db_handler import DatabaseHandler

# Thiết lập ghi nhận log lỗi vào file errors.log
logging.basicConfig(
    filename=ERROR_LOG_PATH,
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8"
)

# Quản lý Session riêng cho từng luồng để bảo đảm an toàn Thread-safe tuyệt đối
_thread_local = threading.local()


def get_thread_session():
    """Tạo và duy trì phiên session độc lập cho mỗi worker thread."""
    if not hasattr(_thread_local, "session"):
        if HAS_CURL_CFFI:
            s = cffi_requests.Session(impersonate="chrome124")
        elif HAS_CLOUDSCRAPER:
            s = cloudscraper.create_scraper()
        else:
            s = std_requests.Session()
        s.headers.update(DEFAULT_HEADERS)
        _thread_local.session = s
    return _thread_local.session


class TopCVCrawler:
    def __init__(self):
        """Khởi tạo phiên cào dữ liệu và nạp cơ sở dữ liệu."""
        print("[TopCVCrawler] Đang kết nối tới MySQL Database...")
        self.db = DatabaseHandler()
        
        # Nạp sẵn danh mục job_id hiện có trong DB vào RAM
        self.existing_jobs = self.db.load_existing_jobs_index()
        print(f"[TopCVCrawler] Đã nạp {len(self.existing_jobs)} tin đã có từ MySQL vào bộ nhớ cache.")
        print(f"[TopCVCrawler] Chế độ Đa Luồng: Kích hoạt {MAX_WORKERS} luồng cào song song siêu tốc.")

        # Thống kê toàn phiên chạy
        self.total_stats = {
            "new": 0,
            "updated": 0,
            "skipped": 0,
            "error": 0
        }

    def _fetch_html(self, url: str) -> Optional[str]:
        """Tải HTML với cơ chế retry thông minh và tự động hạ nhiệt khi gặp Cloudflare 429."""
        session = get_thread_session()
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                # Nghỉ tự nhiên giữa các request để duy trì tần suất an toàn
                if MAX_DELAY_SECONDS > 0:
                    time.sleep(random.uniform(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS))

                resp = session.get(url, timeout=REQUEST_TIMEOUT)

                # Nhận diện nếu bị Cloudflare 429 Rate Limit hoặc Challenge
                is_challenge = (
                    resp.status_code in (429, 403, 503) or
                    "Just a moment..." in resp.text or
                    "Attention Required!" in resp.text or
                    resp.headers.get("cf-mitigated") == "challenge"
                )

                if is_challenge:
                    cooldown = 12 * attempt  # 12s, 24s, 36s...
                    print(f"\n[Cloudflare Cooldown] Gặp mã {resp.status_code} / Thử thách. Tạm nghỉ {cooldown}s để hạ nhiệt IP...", flush=True)
                    time.sleep(cooldown)
                    # Làm mới phiên session cho luồng
                    if hasattr(_thread_local, "session"):
                        del _thread_local.session
                    session = get_thread_session()
                    continue

                if resp.status_code == 200:
                    return resp.text
                else:
                    logging.error(f"HTTP {resp.status_code} khi tải {url}")
                    return None

            except Exception as e:
                if attempt == MAX_RETRIES:
                    logging.error(f"Lỗi ngoại lệ mạng ({url}): {str(e)}")
                time.sleep(attempt * 2.0)

        logging.error(f"Không thể tải trang sau {MAX_RETRIES} lần thử: {url}")
        return None

    def parse_listing_page(self, html: str) -> List[Dict[str, str]]:
        """Trích xuất danh sách việc làm từ trang danh sách."""
        soup = BeautifulSoup(html, "html.parser")
        job_items = []
        seen_job_ids = set()

        links = soup.select("h3 a[href*='/viec-lam/'], a[href*='/viec-lam/']")

        for a in links:
            href = a.get("href", "")
            if not href:
                continue

            match_id = re.search(r"/(\d+)\.html", href)
            if not match_id:
                continue

            job_id = match_id.group(1)
            if job_id in seen_job_ids:
                continue
            seen_job_ids.add(job_id)

            title = (
                a.get("aria-label")
                or a.get("title")
                or a.get_text(strip=True)
            )

            company_name = ""
            parent = a.find_parent(class_=re.compile(r"job-item|job-ta|item"))
            if not parent:
                parent = a.find_parent("div")
            if parent:
                comp_tag = parent.select_one(
                    "a.company, a.company-name, .company, .company-name, a[href*='/cong-ty/']"
                )
                if comp_tag:
                    company_name = (
                        comp_tag.get("title")
                        or comp_tag.get("aria-label")
                        or comp_tag.get_text(strip=True)
                    )

            job_items.append({
                "job_id": job_id,
                "title": title.strip() if title else "",
                "company_name": company_name.strip() if company_name else "",
                "job_url": href.split("?")[0]
            })

        return job_items

    def parse_detail_page(self, html: str, job_url: str, category_name: str) -> Optional[Dict[str, Any]]:
        """Bóc tách chi tiết thông tin công việc (kết hợp HTML DOM + JSON-LD)."""
        soup = BeautifulSoup(html, "html.parser")

        match_id = re.search(r"/(\d+)\.html", job_url)
        job_id = match_id.group(1) if match_id else ""
        if not job_id:
            return None

        # 1. Đọc khối JSON-LD
        json_ld = {}
        for script in soup.select('script[type="application/ld+json"]'):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get("@type") == "JobPosting":
                    json_ld = data
                    break
            except Exception:
                pass

        # 2. Tiêu đề
        title = ""
        if json_ld.get("title"):
            title = str(json_ld["title"]).strip()
        if not title:
            t_tag = soup.select_one(".job-detail__info--title, h1.job-title, h1.title, h1")
            if t_tag:
                title = t_tag.get_text(strip=True)

        # 3. Tên công ty
        company_name = ""
        if json_ld.get("hiringOrganization", {}).get("name"):
            company_name = str(json_ld["hiringOrganization"]["name"]).strip()
        if not company_name:
            c_tag = soup.select_one(".job-detail__company--title, .company-name, a.company-title, a.company-name")
            if c_tag:
                company_name = c_tag.get_text(strip=True)

        # 4. Mức lương (Ưu tiên JSON-LD Schema trước, sau đó tới HTML sạch)
        salary = ""
        if json_ld.get("baseSalary"):
            bs = json_ld["baseSalary"]
            if isinstance(bs, dict) and "value" in bs:
                val = bs["value"]
                if isinstance(val, dict):
                    min_v = val.get("minValue")
                    max_v = val.get("maxValue")
                    if min_v and max_v:
                        min_tr = round(min_v / 1_000_000, 1) if min_v >= 100_000 else min_v
                        max_tr = round(max_v / 1_000_000, 1) if max_v >= 100_000 else max_v
                        min_str = f"{int(min_tr)}" if min_tr == int(min_tr) else f"{min_tr}"
                        max_str = f"{int(max_tr)}" if max_tr == int(max_tr) else f"{max_tr}"
                        salary = f"{min_str} - {max_str} triệu VND"
                    elif min_v:
                        min_tr = round(min_v / 1_000_000, 1) if min_v >= 100_000 else min_v
                        min_str = f"{int(min_tr)}" if min_tr == int(min_tr) else f"{min_tr}"
                        salary = f"Từ {min_str} triệu VND"
                    elif max_v:
                        max_tr = round(max_v / 1_000_000, 1) if max_v >= 100_000 else max_v
                        max_str = f"{int(max_tr)}" if max_tr == int(max_tr) else f"{max_tr}"
                        salary = f"Tới {max_str} triệu VND"

        if not salary:
            for item in soup.select(".job-detail__info--section, .job-detail__box--left .box-item, .box-header-job-list-info__item--content"):
                txt = item.get_text(separator=" ", strip=True)
                txt_lower = txt.lower()
                if any(k in txt_lower for k in ["mức lương", "lương"]) and not any(w in txt_lower for w in ["lừa đảo", "hứa hẹn", "cảnh giác", "bất thường", "chiêu trò"]):
                    val = item.select_one(".list-info__content__detail, .job-detail__info--section-content-value, .detail, .value")
                    salary = val.get_text(strip=True) if val else txt
                    salary = re.sub(r'^(Mức lương|Lương)[\s:]*', '', salary, flags=re.I).strip()
                    break

        # 5. Địa điểm
        location = ""
        for item in soup.select(".box-header-job-list-info__item--content, .job-detail__info--section"):
            txt = item.get_text(separator=" ", strip=True)
            if "địa điểm" in txt.lower():
                val = item.select_one(".list-info__content__detail, .job-detail__info--section-content-value, .detail")
                location = val.get_text(strip=True) if val else txt
                location = re.sub(r"^Địa điểm\s*", "", location, flags=re.IGNORECASE)
                break

        if not location:
            addr_item = soup.select_one(".box-job-information-address-and-time-list__item")
            if addr_item:
                location = addr_item.get_text(separator=" ", strip=True)

        if not location and json_ld.get("jobLocation"):
            jl = json_ld["jobLocation"]
            if isinstance(jl, dict):
                addr = jl.get("address", {})
                if isinstance(addr, dict):
                    location = addr.get("streetAddress") or addr.get("addressLocality") or ""

        # 6. Kinh nghiệm
        experience_required = ""
        for item in soup.select(".box-header-job-list-info__item--content, .job-detail__info--section"):
            txt = item.get_text(separator=" ", strip=True)
            if "kinh nghiệm" in txt.lower():
                val = item.select_one(".list-info__content__detail, .job-detail__info--section-content-value, .detail")
                experience_required = val.get_text(strip=True) if val else txt
                experience_required = re.sub(r"^Kinh nghiệm\s*", "", experience_required, flags=re.IGNORECASE)
                break

        if not experience_required and json_ld.get("experienceRequirements"):
            exp_req = json_ld["experienceRequirements"]
            if isinstance(exp_req, dict) and "monthsOfExperience" in exp_req:
                m = exp_req["monthsOfExperience"]
                experience_required = f"{m // 12} năm" if m >= 12 else f"{m} tháng"
            else:
                experience_required = str(exp_req)

        # 7. Hạn nộp
        deadline = ""
        for item in soup.select(".box-header-job-list-info__item--content, .job-detail__info--deadline, .deadline"):
            txt = item.get_text(separator=" ", strip=True)
            if any(k in txt.lower() for k in ["hạn nộp", "hạn ứng tuyển"]):
                val = item.select_one(".list-info__content__detail, .detail")
                deadline = val.get_text(strip=True) if val else txt
                deadline = re.sub(r"^Hạn ứng tuyển\s*|^Hạn nộp hồ sơ\s*", "", deadline, flags=re.IGNORECASE)
                break

        if not deadline and json_ld.get("validThrough"):
            deadline = str(json_ld["validThrough"])

        # 8. Ngày đăng
        posted_date = ""
        if json_ld.get("datePosted"):
            posted_date = str(json_ld["datePosted"])
        else:
            p_tag = soup.select_one(".job-detail__info--posted-date, .posted-date")
            if p_tag:
                posted_date = p_tag.get_text(strip=True)

        # 9. Mô tả & Yêu cầu
        description = ""
        requirements = ""

        for section in soup.select(".box-job-information-detail-item, .job-description__item"):
            h_tag = section.select_one(".box-job-information-detail-item__title--title, .job-description__item--title, h2, h3")
            if not h_tag:
                continue

            sec_title = h_tag.get_text(strip=True).lower()
            content_tag = section.select_one(".box-job-information-detail-item__content, .job-description__item--content")
            sec_content = content_tag.get_text(separator="\n", strip=True) if content_tag else section.get_text(separator="\n", strip=True)

            if "mô tả công việc" in sec_title or "mô tả" in sec_title:
                description = sec_content
            elif "yêu cầu ứng viên" in sec_title or "yêu cầu" in sec_title:
                requirements = sec_content

        if (not description or not requirements) and json_ld.get("description"):
            full_text = BeautifulSoup(json_ld["description"], "html.parser").get_text(separator="\n", strip=True)
            parts = re.split(r"(?i)(?:mô tả công việc|yêu cầu ứng viên|quyền lợi được hưởng|quyền lợi)", full_text)
            headings = re.findall(r"(?i)(mô tả công việc|yêu cầu ứng viên|quyền lợi)", full_text)

            for i, h in enumerate(headings):
                hl = h.lower()
                if "mô tả" in hl and not description and i + 1 < len(parts):
                    description = parts[i + 1].strip()
                elif "yêu cầu" in hl and not requirements and i + 1 < len(parts):
                    requirements = parts[i + 1].strip()

            if not description and not requirements:
                description = full_text

        # 10. Kỹ năng cần có & nên có
        skills_required_tags = []
        skills_preferred_tags = []

        for tag_box in soup.select(".required-tag__content"):
            desc_el = tag_box.select_one(".required-tag__content--desc")
            desc_title = desc_el.get_text(strip=True).lower() if desc_el else ""
            tag_text = desc_el.get_text(strip=True) if desc_el else ""
            tags = [t.strip() for t in tag_text.split(",") if t.strip()]

            if "kỹ năng cần có" in desc_title:
                for t in tags:
                    if t not in skills_required_tags:
                        skills_required_tags.append(t)
            elif "kỹ năng nên có" in desc_title:
                for t in tags:
                    if t not in skills_preferred_tags:
                        skills_preferred_tags.append(t)

        for a_tag in soup.select(".box-category-tags a, .job-tags a"):
            t_name = a_tag.get_text(strip=True)
            if t_name and t_name not in skills_required_tags and t_name not in skills_preferred_tags:
                skills_required_tags.append(t_name)

        return {
            "job_id": job_id,
            "title": title,
            "company_name": company_name,
            "salary": salary,
            "location": location,
            "experience_required": experience_required,
            "category": category_name,
            "description": description,
            "requirements": requirements,
            "skills_required_tags": skills_required_tags,
            "skills_preferred_tags": skills_preferred_tags,
            "posted_date": posted_date,
            "deadline": deadline,
            "job_url": job_url
        }

    def _worker_fetch_detail(self, job: Dict[str, str], category_name: str) -> Tuple[Dict[str, str], Optional[Dict[str, Any]], Optional[str]]:
        """Hàm worker cho luồng song song: Tải và bóc tách trang chi tiết của 1 việc làm."""
        j_url = job["job_url"]
        detail_html = self._fetch_html(j_url)
        if not detail_html:
            return job, None, f"Lỗi tải HTML ({j_url})"

        try:
            job_data = self.parse_detail_page(detail_html, j_url, category_name)
            if not job_data:
                return job, None, f"Không bóc tách được chi tiết ({j_url})"

            if not job_data.get("title"):
                job_data["title"] = job["title"]
            if not job_data.get("company_name"):
                job_data["company_name"] = job["company_name"]

            return job, job_data, None
        except Exception as e:
            return job, None, f"Lỗi xử lý ({j_url}): {str(e)}"

    def crawl_category(self, cat_key: str, cat_info: Dict[str, str]):
        """Crawl toàn bộ các trang của 1 nhóm ngành sử dụng Đa Luồng Song Song."""
        cat_name = cat_info["name"]
        cat_code = cat_info["code"]
        cat_db_name = cat_info["category_db"]

        print(f"\n{'='*75}")
        print(f"BẮT ĐẦU CRAWL: [{cat_name.upper()}] (Code: {cat_code} -> DB: '{cat_db_name}')")
        print(f"{'='*75}")

        current_saved = self.db.get_category_job_count(cat_db_name)
        if current_saved >= TARGET_JOBS_PER_CATEGORY:
            print(f"[{cat_name}] Đã có sẵn {current_saved}/{TARGET_JOBS_PER_CATEGORY} việc làm trong MySQL. Đạt chỉ tiêu!")
            return

        print(f"[{cat_name}] Hiện có: {current_saved}/{TARGET_JOBS_PER_CATEGORY} việc làm. Cần cào thêm: {TARGET_JOBS_PER_CATEGORY - current_saved} tin.")

        page = 1
        while True:
            if current_saved >= TARGET_JOBS_PER_CATEGORY:
                print(f"\n[{cat_name}] HOÀN THÀNH CHỈ TIÊU: Đã thu thập đủ {TARGET_JOBS_PER_CATEGORY} bài job cho ngành này!")
                break

            if MAX_PAGES_PER_CATEGORY and page > MAX_PAGES_PER_CATEGORY:
                print(f"[{cat_name}] Đạt giới hạn {MAX_PAGES_PER_CATEGORY} trang theo cấu hình.")
                break

            url = SEARCH_URL_TEMPLATE.format(
                category_code=cat_code,
                locations=LOCATIONS,
                page=page
            )

            html = self._fetch_html(url)
            if not html:
                logging.error(f"Không thể tải trang listing: {url}")
                print(f"[{cat_name}] Trang {page}: Lỗi tải trang listing -> Bỏ qua.")
                break

            job_listings = self.parse_listing_page(html)
            if not job_listings:
                print(f"[{cat_name}] Trang {page}: Không còn tin tuyển dụng nào -> Hoàn tất ngành này.")
                break

            page_new = 0
            page_updated = 0
            page_skipped = 0
            page_error = 0

            # 1. Lọc trước các tin không đổi để bỏ qua siêu tốc
            jobs_to_fetch = []
            for job in job_listings:
                jid = job["job_id"]
                j_title = job["title"].strip().lower()
                j_company = job["company_name"].strip().lower()

                if jid in self.existing_jobs:
                    cached = self.existing_jobs[jid]
                    if cached["title"] == j_title and cached["company_name"] == j_company:
                        self.db.mark_job_checked(jid)
                        page_skipped += 1
                        self.total_stats["skipped"] += 1
                        continue

                jobs_to_fetch.append(job)

            # Giới hạn chỉ cào đúng số lượng tin còn thiếu để đạt 250
            needed = TARGET_JOBS_PER_CATEGORY - current_saved
            if len(jobs_to_fetch) > needed:
                jobs_to_fetch = jobs_to_fetch[:needed]

            total_fetch = len(jobs_to_fetch)
            print(f"[{cat_name}] Trang {page}: Tổng {len(job_listings)} tin (Bỏ qua {page_skipped} tin cũ, cào song song {total_fetch} tin mới)...")

            # 2. Cào song song các tin mới bằng ThreadPoolExecutor
            if total_fetch > 0:
                completed_count = 0
                with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                    futures = [
                        executor.submit(self._worker_fetch_detail, j, cat_db_name)
                        for j in jobs_to_fetch
                    ]

                    for future in concurrent.futures.as_completed(futures):
                        completed_count += 1
                        job_item, job_data, err_msg = future.result()
                        jid = job_item["job_id"]
                        j_title = job_item["title"].strip().lower()
                        j_company = job_item["company_name"].strip().lower()

                        display_name = (job_item['title'][:32] + '...') if len(job_item['title']) > 32 else job_item['title']
                        print(f"\r  -> [{completed_count}/{total_fetch}] {display_name}", end="", flush=True)

                        if err_msg or not job_data:
                            logging.error(err_msg or f"Lỗi không xác định job {jid}")
                            page_error += 1
                            self.total_stats["error"] += 1
                            continue

                        # Lưu an toàn vào MySQL (chạy tại luồng chính để tránh xung đột kết nối)
                        status = self.db.upsert_job(job_data)
                        if status == "inserted":
                            page_new += 1
                            current_saved += 1
                            self.total_stats["new"] += 1
                            self.existing_jobs[jid] = {"title": j_title, "company_name": j_company}
                        elif status == "updated":
                            page_updated += 1
                            self.total_stats["updated"] += 1
                            self.existing_jobs[jid] = {"title": j_title, "company_name": j_company}
                        elif status == "unchanged":
                            page_skipped += 1
                            self.total_stats["skipped"] += 1
                        else:
                            page_error += 1
                            self.total_stats["error"] += 1

                print()  # Xuống dòng sau khi hoàn tất thanh tiến trình

            # In log tổng kết của trang kèm tiến độ ngành
            print(f"[{cat_name}] Trang {page}: Mới +{page_new} | Cập nhật +{page_updated} | Bỏ qua +{page_skipped} | Lỗi +{page_error} (Tiến độ: {current_saved}/{TARGET_JOBS_PER_CATEGORY})")

            page += 1

    def run(self):
        """Khởi chạy toàn bộ quá trình thu thập cho cả 4 nhóm ngành."""
        start_time = time.time()
        print("\n" + "#"*75)
        print("# KHỞI CHẠY HỆ THỐNG CRAWL DỮ LIỆU TOPCV.VN -> MYSQL JOBS_RAW (ĐA LUỒNG)")
        print(f"# Khu vực: Đà Nẵng, Huế, Quảng Ngãi (locations={LOCATIONS})")
        print("#"*75)

        for cat_code, cat_info in CATEGORIES.items():
            self.crawl_category(cat_code, cat_info)

        elapsed = round(time.time() - start_time, 2)
        print("\n" + "="*75)
        print(f"HOÀN THÀNH QUÁ TRÌNH THU THẬP TRONG {elapsed} GIÂY!")
        print(f"Kết quả phiên: Mới +{self.total_stats['new']} | Cập nhật +{self.total_stats['updated']} | Bỏ qua +{self.total_stats['skipped']} | Lỗi +{self.total_stats['error']}")
        print("="*75)

        self.print_summary()
        self.db.close()

    def print_summary(self):
        """In bảng tổng kết số lượng việc làm hiện có theo từng ngành."""
        print("\n" + "-"*50)
        print("TỔNG KẾT SỐ LƯỢNG VIỆC LÀM TRONG DATABASE MYSQL")
        print("-" * 50)
        stats = self.db.get_category_stats()
        if not stats:
            print("Chưa có dữ liệu hoặc không thể truy vấn bảng jobs_raw.")
            return

        total = 0
        print(f"{'Nhóm ngành':<35} | {'Số lượng':>10}")
        print("-" * 50)
        for cat, cnt in sorted(stats.items(), key=lambda x: x[1], reverse=True):
            print(f"{cat:<35} | {cnt:>10}")
            total += cnt
        print("-" * 50)
        print(f"{'TỔNG CỘNG':<35} | {total:>10}")
        print("-" * 50)


if __name__ == "__main__":
    crawler = TopCVCrawler()
    crawler.run()
