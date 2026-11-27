# DANH MỤC CÁC TRƯỜNG DỮ LIỆU THÔ ĐƯA VÀO DATABASE (`jobs_raw`)

Tài liệu này mô tả chi tiết toàn bộ các trường dữ liệu việc làm thô (**Raw Job Posting Data**) được hệ thống crawler tự động thu thập từ nền tảng tuyển dụng TopCV và lưu trữ vào bảng `jobs_raw` thuộc cơ sở dữ liệu MySQL `skill_intelligence`.

---

## 1. TỔNG QUAN BẢNG DỮ LIỆU THÔ

- **Tên cơ sở dữ liệu:** `skill_intelligence`
- **Tên bảng:** `jobs_raw`
- **Công cụ lưu trữ (Storage Engine):** `InnoDB`
- **Bộ mã ký tự (Charset / Collation):** `utf8mb4` / `utf8mb4_unicode_ci`
- **Mục đích:** Lưu trữ nguyên trạng (ground-truth raw data) các tin tuyển dụng thực tế trước khi đưa qua pipeline làm sạch, phân tích kỹ năng và chuẩn hóa sang mô hình 3NF.
- **Tổng số trường:** **19 trường**

---

## 2. BẢNG TỔNG HỢP CHI TIẾT 19 TRƯỜNG DỮ LIỆU THÔ

| STT | Tên trường (`Field Name`) | Kiểu dữ liệu MySQL | Ràng buộc / Khóa | Nguồn bóc tách (TopCV Crawler) | Ý nghĩa & Mục đích sử dụng | Ví dụ dữ liệu thực tế |
| :-: | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | `job_id` | `VARCHAR(50)` | **PRIMARY KEY** (NOT NULL) | Regex URL `/(\d+)\.html` hoặc ID thẻ tin | Mã định danh duy nhất của tin tuyển dụng trên TopCV. Dùng làm khóa chính và chống trùng lặp. | `'1044822'` |
| **2** | `title` | `VARCHAR(255)` | `NOT NULL` | JSON-LD `title` hoặc thẻ `h1.job-title` | Tiêu đề / chức danh công việc nguyên gốc của nhà tuyển dụng. | `'Trợ Lý Merchandiser / PPC Development'` |
| **3** | `company_name` | `VARCHAR(255)` | `NULL` | JSON-LD `hiringOrganization.name` hoặc `.company-name` | Tên doanh nghiệp / công ty đăng tin tuyển dụng. | `'CÔNG TY TNHH DỆT MAY HOA SEN'` |
| **4** | `salary` | `VARCHAR(100)` | `NULL` | JSON-LD `baseSalary` hoặc khối thông tin mức lương | Mức lương thô nguyên bản do nhà tuyển dụng công bố (chưa chuẩn hóa số). | `'15 - 20 triệu VND'`, `'Thỏa thuận'` |
| **5** | `location` | `VARCHAR(255)` | `NULL` | JSON-LD `jobLocation` hoặc mục Địa điểm | Địa chỉ / khu vực làm việc thô của tin tuyển dụng. | `'Đà Nẵng'`, `'Quận Hải Châu, Đà Nẵng'` |
| **6** | `experience_required` | `VARCHAR(50)` | `NULL` | JSON-LD `experienceRequirements` hoặc mục Kinh nghiệm | Yêu cầu số năm kinh nghiệm làm việc thô từ tin tuyển dụng. | `'3 năm'`, `'Không yêu cầu kinh nghiệm'`, `'Dưới 1 năm'` |
| **7** | `category` | `VARCHAR(100)` | `NULL` | Phân loại từ chiến dịch cào (`config.py`) | Nhóm ngành mục tiêu mà tin tuyển dụng thuộc về (1 trong 4 nhóm ngành trọng điểm). | `'Công nghệ Thông tin'`, `'Logistics'`, `'Du lịch-Dịch vụ'`, `'Kế toán'` |
| **8** | `description` | `TEXT` | `NULL` | Mục `.box-job-information-detail-item` hoặc JSON-LD | Toàn bộ văn bản mô tả công việc (Job Description - JD) nguyên gốc, chưa qua xử lý. | `'Mô tả công việc\n1. Theo dõi đơn hàng...\n2. Báo cáo tiến độ...'` |
| **9** | `requirements` | `TEXT` | `NULL` | Mục `yêu cầu ứng viên` hoặc JSON-LD | Toàn bộ văn bản yêu cầu năng lực, chuyên môn, bằng cấp và kỹ năng đối với ứng viên. | `'Yêu cầu ứng viên\n1. Tốt nghiệp Cao đẳng/Đại học...\n2. Thành thạo Excel...'` |
| **10** | `skills_required_tags` | `JSON` | `NULL` (Mặc định: `'[]'`) | Thẻ `.required-tag__content--desc` (kỹ năng cần có) và `.job-tags` | Mảng JSON chứa các từ khóa kỹ năng bắt buộc do TopCV gán cho tin. | `'["Tiếng Anh", "Giao tiếp", "Kỹ năng đàm phán"]'` |
| **11** | `skills_preferred_tags`| `JSON` | `NULL` (Mặc định: `'[]'`) | Thẻ `.required-tag__content--desc` (kỹ năng nên có) | Mảng JSON chứa các từ khóa kỹ năng ưu tiên (nice-to-have) từ TopCV. | `'["Photoshop", "Quản lý thời gian"]'` |
| **12** | `posted_date` | `DATE` | `NULL` | JSON-LD `datePosted` hoặc `.job-detail__info--posted-date` | Ngày tin tuyển dụng được đăng tải (đã chuẩn hóa định dạng `YYYY-MM-DD`). | `'2026-09-15'` |
| **13** | `deadline` | `DATE` | `NULL` | JSON-LD `validThrough` hoặc mục `.deadline` | Hạn chót nhận hồ sơ ứng tuyển (đã chuẩn hóa định dạng `YYYY-MM-DD`). | `'2026-10-31'` |
| **14** | `job_url` | `VARCHAR(500)` | `NULL` | Thuộc tính `href` của tin tại trang listing | Đường dẫn URL trực tiếp tới tin tuyển dụng trên TopCV. | `'https://www.topcv.vn/viec-lam/.../1044822.html'` |
| **15** | `duplicate_count` | `INT` | Mặc định: `1` | Hệ thống quản trị (`db_handler.py`) | Số lần hệ thống bắt gặp lại tin này trong các chu kỳ quét tiếp theo (phục vụ thống kê độ lặp). | `1`, `2` |
| **16** | `first_seen_at` | `DATETIME` | `NULL` | Hệ thống quản trị (`NOW()`) | Thời điểm đầu tiên tin tuyển dụng được phát hiện và thêm mới vào cơ sở dữ liệu. | `'2026-09-16 01:04:17'` |
| **17** | `last_updated_at` | `DATETIME` | `NULL` | Hệ thống quản trị (`NOW()`) | Thời điểm gần nhất mà nội dung quan trọng của tin (lương, hạn nộp, JD) bị thay đổi. | `'2026-09-16 01:04:17'` |
| **18** | `last_checked_at` | `DATETIME` | `NULL` | Hệ thống quản trị (`NOW()`) | Thời điểm gần nhất mà crawler kiểm tra lại sự tồn tại của tin trên trang tuyển dụng. | `'2026-09-16 01:09:32'` |
| **19** | `llm_processed` | `TINYINT(1)` | Mặc định: `0` (FALSE) | Trạng thái pipeline AI | Cờ đánh dấu tin đã được mô hình AI/LLM bóc tách kỹ năng hay chưa (`0`: Chưa, `1`: Rồi). | `0` |

---

## 3. PHÂN NHÓM CHỨC NĂNG CỦA CÁC TRƯỜNG DỮ LIỆU

Nhằm tối ưu hóa cho quá trình khai phá dữ liệu và phân tích khoảng cách kỹ năng (Skill Gap Analysis), 19 trường dữ liệu trên được phân chia thành **5 nhóm chức năng**:

### Nhóm 1: Định danh & Nguồn gốc tin (Identification & Source)
- `job_id`: Khóa chính duy nhất, định danh tin trên hệ thống tuyển dụng.
- `job_url`: Đường dẫn gốc để kiểm chứng và truy xuất nguồn tin khi cần.
- `category`: Nhãn nhóm ngành mục tiêu (IT, Du lịch, Logistics, Kế toán).

### Nhóm 2: Thông tin tuyển dụng & Đãi ngộ (Job Info & Compensation)
- `title`: Tên vị trí việc làm.
- `company_name`: Doanh nghiệp tuyển dụng.
- `salary`: Mức lương công bố.
- `location`: Khu vực/địa điểm làm việc (tập trung khu vực Đà Nẵng mở rộng).
- `experience_required`: Số năm kinh nghiệm đòi hỏi từ ứng viên.

### Nhóm 3: Nội dung văn bản thô & Kỹ năng (Raw Content & Skills)
- `description`: Toàn bộ nội dung mô tả nhiệm vụ công việc.
- `requirements`: Toàn bộ nội dung yêu cầu về năng lực, bằng cấp, kỹ năng.
- `skills_required_tags`: Các tag kỹ năng bắt buộc do nền tảng tuyển dụng cung cấp dạng JSON.
- `skills_preferred_tags`: Các tag kỹ năng ưu tiên do nền tảng tuyển dụng cung cấp dạng JSON.

### Nhóm 4: Mốc thời gian tuyển dụng (Timeline)
- `posted_date`: Ngày phát hành tin tuyển dụng.
- `deadline`: Hạn nộp hồ sơ.

### Nhóm 5: Quản trị & Điều phối Pipeline (Audit & Pipeline Control)
- `duplicate_count`: Bộ đếm số lần tin xuất hiện lại trên sàn tuyển dụng.
- `first_seen_at`: Mốc thời gian ghi nhận tin lần đầu.
- `last_updated_at`: Mốc thời gian nội dung tin có biến động.
- `last_checked_at`: Mốc thời gian quét kiểm tra tin gần nhất.
- `llm_processed`: Cờ điều phối phục vụ module LLM bóc tách kỹ năng.

---

## 4. CƠ CHẾ LƯU TRỮ VÀ XỬ LÝ (UPSERT LOGIC)

Dữ liệu thô khi đưa vào database thông qua phương thức `DatabaseHandler.upsert_job(job_data)` trong file `db_handler.py`:
1. **Nếu `job_id` chưa tồn tại:**
   - Thực hiện `INSERT` mới toàn bộ 14 trường thông tin trích xuất.
   - Thiết lập `duplicate_count = 1`, `llm_processed = FALSE`.
   - Ghi nhận `first_seen_at = NOW()`, `last_updated_at = NOW()`, `last_checked_at = NOW()`.
2. **Nếu `job_id` đã tồn tại:**
   - Hệ thống tự động so sánh 4 trường cốt lõi: `description`, `requirements`, `salary`, `deadline`.
   - **Nếu không thay đổi:** Giữ nguyên dữ liệu, chỉ cập nhật `last_checked_at = NOW()` và tăng `duplicate_count = duplicate_count + 1`.
   - **Nếu có thay đổi:** Cập nhật các trường mới cùng `last_updated_at = NOW()`, `last_checked_at = NOW()`, và tăng `duplicate_count`.
