# HƯỚNG DẪN TÍCH HỢP TỪ GÓI DỮ LIỆU SANG DỰ ÁN CHÍNH (SKILLGAP AI)

Gói thư mục này (`bundle_to_main_project`) chứa toàn bộ thành quả đã hoàn thiện từ hệ thống cào dữ liệu và chuẩn hóa kỹ năng, sẵn sàng để gộp trực tiếp vào dự án chính (`ai-skill-gap-system`).

---

## 📁 CẤU TRÚC GÓI TÍCH HỢP

```text
bundle_to_main_project/
├── 1. database/
│   ├── skill_intelligence_full_dump.sql     <-- [Khuyên dùng] 1 file SQL chứa cả Schema 3NF, 5 Views và 1.000 JD + 500 CV sạch
│   ├── schema_3nf_v2.sql                    <-- Bản vẽ DDL Schema 3NF & 5 Views (Cung - Cầu - Gap - MSPS)
│   ├── sync_clean_data_to_mysql.py          <-- Script tự động nạp dữ liệu từ file JSON vào MySQL
│   ├── clean_job_postings.json              <-- 1.000 tin tuyển dụng sạch (chuẩn hóa lương VND, kinh nghiệm, vị trí, kỹ năng)
│   └── clean_resumes_500.json               <-- 500 hồ sơ ứng viên sạch phân theo 4 ngành
│
├── 2. llm_extraction/
│   ├── skill_extractor.py                   <-- Engine LLM trích xuất kỹ năng bằng Groq API (Few-shot, Strict Grounding)
│   ├── extract_positions_groq.py            <-- Trích xuất và chuẩn hóa Chức vụ (chuc_vu) & Vị trí (position)
│   ├── execute_clean_pipeline.py            <-- Pipeline tích hợp: Keyword Boost Regex, Lọc Stop-skills, Soft Collapse
│   └── allowed_skills.json                  <-- [BẮT BUỘC] Whitelist từ điển kỹ năng hợp lệ (đã lọc sạch rác, tỉnh thành)
│
├── 3. esco_taxonomy/
│   ├── occupation_esco_matcher.py           <-- Module ánh xạ Chức danh -> Nghề nghiệp ESCO (tách explicit vs esco_essential)
│   ├── skill_taxonomy_model_4nganh_FINAL.json <-- [BẮT BUỘC] Mô hình tri thức phân loại 4 ngành & kỹ năng bản địa Việt Nam
│   ├── esco_skills_cache.pt                 <-- Vector embedding PyTorch của kỹ năng ESCO phục vụ tra cứu tức thì
│   └── *.csv (5 file ESCO v1.2.1)           <-- Bộ dữ liệu tham chiếu chuẩn quốc tế của Liên minh Châu Âu
│
├── 4. crawlers/
│   ├── crawler.py                           <-- Engine cào tin TopCV đa luồng, vượt Cloudflare bằng curl_cffi (Chrome TLS)
│   ├── config.py                            <-- Cấu hình headers, mã khu vực Đà Nẵng mở rộng, 4 nhóm ngành
│   ├── update_all_real_salaries.py          <-- Bóc tách dải lương và mô hình định giá lương thị trường
│   └── requirements.txt                     <-- Danh mục các thư viện Python cần thiết
│
├── 5. evaluation_benchmark/
│   ├── evaluate_gold_standard.py            <-- Script chạy đánh giá F1 (kết quả đạt chuẩn ~62.50%)
│   ├── data1/                               <-- 4 file nhãn chuẩn Gold Standard (80 JD + 40 CV gán nhãn sạch)
│   └── reports/                             <-- Báo cáo chi tiết: metrics_overall, metrics_jd_vs_cv, error_analysis.md
│
└── 6. docs/
    ├── PROJECT_SUMMARY.md                   <-- Báo cáo tổng kết toàn bộ dự án
    └── RAW_DATA_FIELDS.md                   <-- Đặc tả 19 trường dữ liệu việc làm thô
```

---

## 🚀 HƯỚNG DẪN TỪNG BƯỚC TÍCH HỢP VÀO DỰ ÁN CHÍNH

### BƯỚC 1: CẬP NHẬT DATABASE DỰ ÁN CHÍNH (Chọn 1 trong 2 cách)

#### 👉 Cách 1: Nạp nhanh toàn bộ qua file Dump (Khuyên dùng - Nhanh nhất)
File `database/skill_intelligence_full_dump.sql` đã chứa sẵn 100% cấu trúc 23 bảng 3NF, 5 Views tính toán tự động và toàn bộ 1.000 tin việc làm + 500 CV sạch.
```bash
# Tạo database mới nếu chưa có
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS skill_intelligence CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Nạp trực tiếp dữ liệu vào
mysql -u root -p skill_intelligence < database/skill_intelligence_full_dump.sql
```

#### 👉 Cách 2: Khởi tạo Schema DDL rồi nạp qua file JSON
Nếu bạn muốn tự chạy script nạp:
1. Chạy file `database/schema_3nf_v2.sql` trong MySQL Workbench để tạo bảng và views.
2. Chạy lệnh: `python database/sync_clean_data_to_mysql.py` để nạp từ `clean_job_postings.json`.

---

### BƯỚC 2: TÍCH HỢP BỘ NÃO LLM VÀO `ai-nlp-worker`
Để khi sang dự án chính, worker vẫn trích xuất chính xác mà không suy diễn:
1. Sao chép `llm_extraction/*` vào module xử lý NLP của dự án chính (ví dụ: `services/ai-nlp-worker/src/extractor/`).
2. **Quan trọng nhất:** Giữ nguyên file `allowed_skills.json` cùng cấp với script trích xuất để làm bộ lọc Whitelist chống sinh rác.
3. Đảm bảo cấu hình biến môi trường `GROQ_API_KEY` để gọi mô hình `qwen/qwen3.8-27b`.

---

### BƯỚC 3: TÍCH HỢP MODULE ÁNH XẠ NGHỀ NGHIỆP ESCO & TAXONOMY
1. Sao chép toàn bộ thư mục `esco_taxonomy/*` vào thư mục taxonomy của backend/worker (ví dụ: `services/ai-nlp-worker/src/taxonomy/`).
2. Module `occupation_esco_matcher.py` sẽ tự động đọc `skill_taxonomy_model_4nganh_FINAL.json` để phân định rõ ràng giữa:
   - `explicit`: Kỹ năng xuất hiện trực tiếp trong tin tuyển dụng (dùng tính Demand/Supply/Gap).
   - `esco_essential`: Kỹ năng cốt lõi theo chuẩn quốc tế (dùng cho gợi ý nghề nghiệp và khóa học).

---

### BƯỚC 4: TÍCH HỢP ENGINE CÀO MỚI (CRAWLER)
1. Đưa `crawlers/crawler.py` và `crawlers/config.py` vào thư mục crawler của dự án chính.
2. Cài đặt thư viện: `pip install curl_cffi pymysql beautifulsoup4`.
3. Khi cần cào bổ sung tin tuyển dụng mới: Chạy `python crawler.py`.

---

### BƯỚC 5: KIỂM TRA ĐỐI CHUẨN ĐỘ CHÍNH XÁC (F1 BENCHMARK)
Để kiểm tra xem hệ thống bên dự án chính có đạt cùng độ chính xác hay không:
```bash
cd evaluation_benchmark
python evaluate_gold_standard.py
```
👉 Kết quả chuẩn xác cần đạt được: **F1-Score ~ 62.50%** (Precision: 51.65%, Recall: 79.11%).

