# TỔNG KẾT DỰ ÁN: THU THẬP & CHUẨN HÓA DỮ LIỆU TUYỂN DỤNG THÔ (SKILL INTELLIGENCE)

**Địa bàn nghiên cứu:** Khu vực Đà Nẵng mở rộng (Đà Nẵng, Quảng Nam, Thừa Thiên Huế, Quảng Ngãi)  
**Mục tiêu chính:** Xây dựng hệ thống tự động cào và chuẩn hóa **dữ liệu việc làm thô** chất lượng cao từ thị trường tuyển dụng thực tế cho 4 nhóm ngành kinh tế trọng điểm, lưu trữ an toàn vào cơ sở dữ liệu MySQL (`jobs_raw`).

> [!IMPORTANT]
> **VAI TRÒ CỦA CÁC TỆP CSV VÀ JSON TRONG DỰ ÁN:**  
> Các tệp dữ liệu `.csv` và `.json` (dữ liệu ESCO, từ điển nghề nghiệp, kỹ năng chuẩn và mô hình `skill_taxonomy_model_4nganh_FINAL.json`) **là các tệp dữ liệu hỗ trợ tham chiếu (Reference & Ground-truth Data)**.  
> Chúng được sử dụng để:
> 1. Định hướng phạm vi nghề nghiệp và chuẩn hóa việc phân loại ngành.
> 2. Hỗ trợ quá trình cào, lọc và đưa dữ liệu tin tuyển dụng vào bảng dữ liệu thô (`jobs_raw`) một cách chính xác, đúng ngành và đúng ngữ cảnh nhất.
> 3. **Hoàn toàn KHÔNG dùng các tệp này để tính khoảng cách (distance / skill gap).**

---

## 1. CÁC MODULE VÀ CÔNG VIỆC KỸ THUẬT ĐÃ TRIỂN KHAI

### 1.1. Module Dữ Liệu Tham Chiếu Hỗ Trợ Phân Loại (Supporting Reference Data)
- **Bộ dữ liệu chuẩn hóa ESCO v1.2.1 (Reference CSVs):**
  - Sử dụng trực tiếp các tệp dữ liệu CSV chuẩn phục vụ tra cứu, nhúng semantic và định danh:
    + `occupations_en.csv`: Danh mục chức danh và định danh nghề nghiệp chuẩn ESCO.
    + `skills_en.csv`: Danh mục chuẩn các kỹ năng và kiến thức ESCO.
    + `occupationSkillRelations_en.csv`: Quan hệ giữa nghề nghiệp và các nhóm kỹ năng liên quan.
    + `skillsHierarchy_en.csv`: Cấu trúc phân cấp ngành nghề theo chuẩn ISCO/ESCO.
    + `transversalSkillsCollection_en.csv`: Nhóm kỹ năng mềm dùng chung.
- **Xây dựng bộ từ điển / cây phân loại 4 ngành (`build_model.py`):**
  - Tạo ra file mô hình tham chiếu: `skill_taxonomy_model_4nganh_FINAL.json`.
  - Giúp ánh xạ và định nghĩa rõ ràng phạm vi nghề nghiệp của 4 nhóm ngành mục tiêu:
    + **Công nghệ Thông tin** (ICT)
    + **Du lịch - Nhà hàng - Khách sạn**
    + **Logistics - Chuỗi cung ứng - Kho vận**
    + **Kế toán - Kiểm toán - Thuế**
  - Tệp này đóng vai trò như một bộ quy tắc và từ điển từ đồng nghĩa (`altLabels`) để làm cơ sở đối chiếu, làm sạch và định hướng cào dữ liệu tuyển dụng vào đúng phân nhóm.

---

### 1.2. Module Cơ Sở Dữ Liệu MySQL (`db_handler.py`)
- **Cơ sở dữ liệu:** MySQL Database `skill_intelligence`, bảng đích: `jobs_raw`.
- **Cấu trúc bảng `jobs_raw` (19 trường dữ liệu thô):**
  *(Xem tài liệu chi tiết tại [RAW_DATA_FIELDS.md](file:///d:/cao%20du%20lieu/RAW_DATA_FIELDS.md))*

| STT | Tên trường | Kiểu dữ liệu | Vai trò / Ý nghĩa |
| :-: | :--- | :--- | :--- |
| 1 | `job_id` | `VARCHAR(50)` (PK) | Mã định danh duy nhất của tin tuyển dụng trên TopCV |
| 2 | `title` | `VARCHAR(255)` | Chức danh / tiêu đề công việc nguyên bản |
| 3 | `company_name` | `VARCHAR(255)` | Tên công ty / doanh nghiệp tuyển dụng |
| 4 | `salary` | `VARCHAR(100)` | Mức lương công bố thô (chưa chuẩn hóa dạng số) |
| 5 | `location` | `VARCHAR(255)` | Địa điểm / khu vực làm việc thô |
| 6 | `experience_required` | `VARCHAR(50)` | Yêu cầu số năm kinh nghiệm thô |
| 7 | `category` | `VARCHAR(100)` | Nhóm ngành mục tiêu (IT, Du lịch, Logistics, Kế toán) |
| 8 | `description` | `TEXT` | Nội dung mô tả công việc (JD) thô |
| 9 | `requirements` | `TEXT` | Nội dung yêu cầu ứng viên / kỹ năng thô |
| 10 | `skills_required_tags` | `JSON` | Thẻ kỹ năng bắt buộc (bóc tách dạng JSON array) |
| 11 | `skills_preferred_tags` | `JSON` | Thẻ kỹ năng ưu tiên / nên có (JSON array) |
| 12 | `posted_date` | `DATE` | Ngày đăng tin tuyển dụng (`YYYY-MM-DD`) |
| 13 | `deadline` | `DATE` | Hạn nộp hồ sơ ứng tuyển (`YYYY-MM-DD`) |
| 14 | `job_url` | `VARCHAR(500)` | Đường dẫn URL gốc của tin tuyển dụng |
| 15 | `duplicate_count` | `INT` | Số lần tin xuất hiện / phát hiện lại |
| 16 | `first_seen_at` | `DATETIME` | Mốc thời gian lần đầu ghi nhận tin vào DB |
| 17 | `last_updated_at` | `DATETIME` | Mốc thời gian cập nhật nội dung tin gần nhất |
| 18 | `last_checked_at` | `DATETIME` | Mốc thời gian kiểm tra / quét tin gần nhất |
| 19 | `llm_processed` | `TINYINT(1)` | Cờ trạng thái đã xử lý qua AI/LLM hay chưa |

- **Cơ chế Upsert & Chống trùng lặp thông minh:**
  + Tự động nạp bộ nhớ đệm (RAM index) danh sách `job_id` sẵn có trong MySQL lúc khởi động để bỏ qua nhanh các tin không đổi, tiết kiệm tài nguyên mạng.
  + Nếu tin có thay đổi (nội dung, mức lương, hạn nộp) -> Thực hiện `UPDATE` và tăng `duplicate_count`.
  + Tự động kiểm tra và phục hồi kết nối (`ping()`) giúp crawler chạy ổn định liên tục.

---

### 1.3. Module Thu Thập Dữ Liệu Tuyển Dụng Thực Tế Đa Luồng (`crawler.py` & `config.py`)
- **Nguồn cào:** Nền tảng tuyển dụng TopCV.vn.
- **Phạm vi khu vực:** Đà Nẵng mở rộng (`locations=l8_l61_l52` gồm Đà Nẵng, Quảng Nam, Thừa Thiên Huế, Quảng Ngãi).
- **Kỹ thuật vượt rào cản và tối ưu tốc độ:**
  + **Đa luồng song song (`ThreadPoolExecutor`):** Tăng tốc thu thập nhiều lần so với tuần tự.
  + **Vượt rào cản Cloudflare / WAF:** Sử dụng `curl_cffi` giả lập dấu vân tay trình duyệt thực (Chrome 124 TLS Fingerprinting) cùng cơ chế Cooldown tự động khi gặp HTTP 429.
  + **Bóc tách lai ghép (Hybrid Parsing):** Kết hợp cấu trúc thẻ Schema `application/ld+json` (`JobPosting`) và bộ phân tích HTML DOM (`BeautifulSoup4`) để trích xuất đầy đủ, chính xác từng trường thông tin thô.

---

### 1.4. Module Trích Xuất & Chuẩn Hóa Kỹ Năng (`skill_extractor.py`)
- **Công nghệ cốt lõi:**
  + **LLM Engine:** Groq API tốc độ cao, hỗ trợ tự động chọn model chat tốt nhất (`openai/gpt-oss-120b`, `qwen/qwen3.8-27b`).
  + **Mô hình Embedding đa ngôn ngữ:** `paraphrase-multilingual-MiniLM-L12-v2` đối sánh ngữ nghĩa giữa kỹ năng tiếng Việt (LLM trích) và kỹ năng tiếng Anh trong từ điển chuẩn ESCO (VD: *"lập trình Java"* khớp *"Java programming"* với cosine similarity > 0.81).
- **Quy tắc trích xuất & đối sánh nghiêm ngặt:**
  1. **Tuyệt đối không suy diễn (Strict Grounding):** Chỉ bóc tách kỹ năng có văn bản dẫn chứng xác thực từ JD.
  2. **Chuẩn hóa tên phổ biến:** Viết theo tên chuẩn thường gặp (VD: `reactjs` -> `React`, `nodejs` -> `Node.js`).
  3. **Ngưỡng tương đồng ESCO (`SIMILARITY_THRESHOLD = 0.75`):**
     - **Nếu >= 0.75:** Khớp chuẩn ESCO -> Lưu `esco_uri`, lưu alias tiếng Việt vào bảng `skill_aliases`.
     - **Nếu < 0.75:** Kỹ năng đặc thù Việt Nam (VD: *Thông tư 200*, *MISA*, *Fast*) -> Giữ nguyên tên tiếng Việt, lưu vào bảng `skills` (`esco_uri = NULL`) và cập nhật vào mục `vietnam_local_skills` trong tệp `skill_taxonomy_model_4nganh_FINAL.json`.
  4. **Ghi vào MySQL chuẩn 3NF:** Tự động điền dữ liệu sạch vào bảng `skills`, `skill_aliases`, `job_skills` và cập nhật cờ `jobs_raw.llm_processed = 1`.

---

## 2. KẾT QUẢ DỮ LIỆU ĐÃ ĐẠT ĐƯỢC

Hệ thống đã cào và đưa thành công **1.000 dòng dữ liệu thô (tin tuyển dụng thực tế)** vào bảng `jobs_raw`:

| STT | Nhóm ngành mục tiêu | Mã ngành TopCV | Tên danh mục trong MySQL | Số lượng tin đã cào | Trạng thái |
| :-: | :--- | :-: | :--- | :-: | :-: |
| 1 | **Công nghệ Thông tin** | `r257` | Công nghệ Thông tin | **250** | ✅ Đạt 100% |
| 2 | **Nhà hàng / Khách sạn / Du lịch** | `r857` | Du lịch-Dịch vụ | **250** | ✅ Đạt 100% |
| 3 | **Logistics / Thu mua / Kho vận** | `r711` | Logistics | **250** | ✅ Đạt 100% |
| 4 | **Kế toán / Kiểm toán / Thuế** | `r392` | Kế toán | **250** | ✅ Đạt 100% |
| **Tổng** | **4 Nhóm ngành trọng điểm** | | | **1.000** | 🎉 **Đạt chỉ tiêu đề ra** |

---

## 3. DANH MỤC CÁC TỆP TIN TRONG DỰ ÁN

| Tệp tin | Vai trò chính |
| :--- | :--- |
| `config.py` | Cấu hình tham số MySQL, ánh xạ 4 nhóm ngành, khu vực, header, tốc độ delay và chỉ tiêu thu thập. |
| `db_handler.py` | Quản lý kết nối MySQL, chuẩn hóa ngày tháng, bộ nhớ đệm chống trùng và logic Upsert vào `jobs_raw`. |
| `crawler.py` | Engine cào dữ liệu đa luồng, vượt Cloudflare, bóc tách chi tiết tin tuyển dụng từ TopCV. |
| `build_model.py` | Script trích xuất và xây dựng bộ từ điển/mô hình tham chiếu 4 ngành phục vụ định hướng cào. |
| `skill_taxonomy_model_4nganh_FINAL.json` | Tệp dữ liệu tham chiếu cấu trúc nghề nghiệp & kỹ năng chuẩn của 4 ngành (kèm danh mục `vietnam_local_skills`). |
| `skill_extractor.py` | Module trích xuất kỹ năng dùng Groq API, so khớp ngữ nghĩa đa ngôn ngữ ESCO bằng `paraphrase-multilingual-MiniLM-L12-v2` và ghi vào MySQL 3NF. |
| `extract_positions_groq.py` | Module trích xuất chức vụ (`chuc_vu`) và vị trí (`position`) chuẩn hóa từ dữ liệu thô bằng Groq API (`qwen/qwen3.8-27b`), cập nhật vào `clean_job_postings.json` và bảng `positions`/`jobs` trong MySQL. |
| `process_data.py` | Pipeline làm sạch dữ liệu tin tuyển dụng, sinh 500 CV lao động và tính toán phân tích chỉ số Cung - Cầu - Thiếu hụt kỹ năng (MSPS) cho Dashboard. |
| `schema_3nf_v2.sql` | Kịch bản SQL Schema 3NF (Phiên bản 2): Khởi tạo 23 bảng quan hệ, 5 Views phân tích cung - cầu (Demand, Supply, Gap, Shortage Rate, MSPS) và migrate 1.000 tin từ `jobs_raw` sang `jobs`. |
| `RAW_DATA_FIELDS.md` | Tài liệu đặc tả chi tiết 19 trường dữ liệu việc làm thô trong bảng `jobs_raw` (kiểu dữ liệu, nguồn trích xuất, ví dụ). |
| `PROJECT_SUMMARY.md` | Tài liệu tóm tắt kiến trúc hệ thống, vai trò các file và số liệu hiện tại của dự án. |

---

## 4. ENTRYPOINTS & CẤU TRÚC THƯ MỤC CHUẨN SAU KHI DỌN DẸP

### 4.1. Các Entrypoint chạy chính ở Root
- **Cào dữ liệu (Crawler):** `python crawler.py` (Cào đa luồng 1.000 tin tuyển dụng từ TopCV vào `jobs_raw`).
- **Làm sạch & trích xuất (Clean & Extract Pipeline):** `python execute_clean_pipeline.py` (Áp dụng Whitelist, bóc tách kỹ năng, đồng bộ MySQL 3NF & file JSON).
- **Đánh giá mô hình (Evaluate F1 & Error Analysis):** `python evaluate_gold_standard.py` (Đánh giá trên bộ Gold Standard 80 JD + 40 CV, F1 ~ 62.50%).
- **Xử lý nguồn cung (Supply / CVs):** `python process_supply_cvs.py` (Xử lý 500 CV lao động, ẩn PII, trích xuất kỹ năng).
- **Đồng bộ MySQL 3NF:** `python sync_clean_data_to_mysql.py`.
- **Giao diện trực quan:** Mở trực tiếp `dashboard.html` trên trình duyệt.

### 4.2. Cấu trúc thư mục dự án
- `root/`: Chứa các script thực thi xương sống, file ESCO CSV chuẩn, file whitelist `allowed_skills.json` và cấu hình MySQL.
- `data/`: Dữ liệu sạch sau pipeline (`clean_job_postings.json`, `clean_resumes_500.json`) và cache vector/embedding.
- `data1/`: Dữ liệu Gold Standard sạch chính thức (`gold_annotation_CLEAN.xlsx`, `gold_cv_annotation_DRAFT.xlsx`, `gold_jd_raw..csv`, `gold_cv_raw.csv`).
- `gold_standard/`: Kết quả đánh giá (`evaluation/`: metrics, error analysis) và cache trích xuất máy (`cache/`).
- `archive/`: Lưu trữ tập trung các script demo, thử nghiệm tạm thời (`scratch/`), script cũ (`deprecated_scripts/`), bản backup xuất dữ liệu (`old_exports/`) và kết quả đánh giá cũ (`old_evaluations/`).
