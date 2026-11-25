# BÁO CÁO PHÂN TÍCH LỖI TRÍCH XUẤT KỸ NĂNG (ERROR ANALYSIS)
*Thời gian đánh giá:* 2026-11-03 15:31:07  
*Dữ liệu đối chuẩn:* 80 Tin tuyển dụng (JD) & 40 Hồ sơ ứng viên (CV) thuộc bộ Gold Standard.

---

## 1. TỔNG HỢP HIỆU SUẤT MÔ HÌNH (SUMMARY)

| Phân loại | Precision | Recall | F1-Score | Gold Skills | Machine Skills | True Positives (TP) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Toàn bộ (Overall)** | **51.65%** | **79.11%** | **62.50%** | 474 | 726 | 375 |
| **Tin tuyển dụng (JD)** | **56.09%** | **88.36%** | **68.62%** | 318 | 501 | 281 |
| **Hồ sơ ứng viên (CV)** | **41.78%** | **60.26%** | **49.35%** | 156 | 225 | 94 |

---

## 2. HIỆU SUẤT CHI TIẾT THEO TỪNG LOẠI KỸ NĂNG (BY SKILL TYPE)

| Nhóm kỹ năng (Skill Type) | Precision | Recall | F1-Score | Số lượng Gold | Số lượng Máy | TP | FP | FN |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **HARD** | 47.10% | 92.86% | 62.50% | 70 | 138 | 65 | 73 | 5 |
| **SOFT** | 47.90% | 70.14% | 56.92% | 211 | 309 | 148 | 161 | 63 |
| **TOOL** | 58.94% | 85.31% | 69.71% | 143 | 207 | 122 | 85 | 21 |
| **KNOWLEDGE** | 28.00% | 50.00% | 35.90% | 14 | 25 | 7 | 18 | 7 |
| **CERTIFICATION** | 40.00% | 100.00% | 57.14% | 2 | 5 | 2 | 3 | 0 |
| **LANGUAGE** | 73.81% | 91.18% | 81.58% | 34 | 42 | 31 | 11 | 3 |

---

## 3. PHÂN TÍCH CÁC LỖI TIÊU BIỂU (ERROR SAMPLES)

### 3.1. Lỗi Bỏ sót Kỹ năng (False Negatives - FN)
*Định nghĩa:* Kỹ năng có trong Gold Standard nhưng mô hình không trích xuất được.
*Nguyên nhân chính:*
1. Kỹ năng nằm ẩn trong câu dài hoặc được viết tắt / diễn đạt gián tiếp trong JD / CV.
2. Mô hình bỏ qua các kỹ năng mềm xuất hiện ở phần trách nhiệm công việc chung.

| Tài liệu (ID) | Tên kỹ năng bị bỏ sót | Loại kỹ năng | Trích dẫn ngữ cảnh (Context Snippet) |
| :---: | :--- | :---: | :--- |
| `JD_2294268` | **Chủ động & Trách nhiệm** | `SOFT` | ...ốt; kiên nhẫn và cẩn trọng trong xử lý dữ liệu. - Tinh thần chủ động, trách nhiệm, cẩn ... |
| `JD_2296084` | **Data analytics pipelines** | `HARD` | ...s of experience in python development. Experience designing data analytics pipelines. E... |
| `JD_1270625` | **Kỹ năng giao tiếp** | `SOFT` | ...t tài liệu, mô tả yêu cầu và phối hợp tốt với đội kỹ thuật. Giao tiếp tốt, chủ động, cẩ... |
| `JD_1270625` | **Giải quyết vấn đề** | `SOFT` | ...mềm, Kế toán, Kiểm toán Kỹ năng cần có SQL, Tester, Kỹ năng giải quyết vấn đề, Kiến Thứ... |
| `JD_1270625` | **Chủ động & Trách nhiệm** | `SOFT` | ...tả yêu cầu và phối hợp tốt với đội kỹ thuật. Giao tiếp tốt, chủ động, cẩn thận, chịu đư... |
| `JD_2292213` | **Luật Kế toán / VAS** | `KNOWLEDGE` | ...tế với WordPress & WooCommerce. Nắm vững PHP, HTML, CSS, JavaScript. Có khả năng tùy ch... |
| `JD_2288117` | **Chủ động & Trách nhiệm** | `SOFT` | ...u ứng viên Tốt nghiệp Cao Đẳng/Đại học trở lên. Trung thực, có trách nhiệm, là người cầ... |
| `JD_1880654` | **Kỹ năng giao tiếp** | `SOFT` | ..., chủ động, tinh thần trách nhiệm cao. Thành thạo tiếng Anh giao tiếp là điểm cộng Kiến... |
| `JD_2208788` | **Microsoft Office** | `TOOL` | ...i hình ưa nhìn, tác phong chuyên nghiệp. Sử dụng thành thạo Microsoft Office (Word, Exc... |
| `JD_1776975` | **Chủ động & Trách nhiệm** | `SOFT` | ...cao về chất lượng, vệ sinh và hiệu quả vận hành của BA GÁC. Trách nhiệm chính 1. Quản l... |
| `JD_2302380` | **Kỹ năng giao tiếp** | `SOFT` | ...à hàng Khách sạn. - Thời gian làm việc: theo ca - Tiếng Anh giao tiếp - Có kinh nghiệm ... |
| `JD_2302380` | **Chủ động & Trách nhiệm** | `SOFT` | Mô tả công việc Mô tả công việc: - Tìm kiếm khách hàng mới (Chủ động liên hệ với khách hàn... |
| `JD_1671799` | **Chủ động & Trách nhiệm** | `SOFT` | Mô tả công việc Chịu trách nhiệm về các chỉ tiêu doanh số do công ty đề ra Xây dựng và phá... |
| `JD_2292807` | **Kỹ năng giao tiếp** | `SOFT` | ...nhiệt tình và có trách nhiệm trong công việc. - Có khả năng giao tiếp tiếng Anh và sử d... |
| `JD_2295155` | **Chủ động & Trách nhiệm** | `SOFT` | Mô tả công việc TRÁCH NHIỆM CHÍNH Khai thác và duy trì khách hàng: Tìm kiếm khách hàng...... |

### 3.2. Lỗi Trích xuất Dư thừa / Suy diễn (False Positives - FP)
*Định nghĩa:* Kỹ năng được máy trích xuất nhưng không có trong Gold Standard.
*Nguyên nhân chính:*
1. Máy bóc tách các khái niệm chung chung hoặc phẩm chất cá nhân (như "tự tin", "nhiệt huyết", "chăm chỉ").
2. Trích xuất cả tên vị trí / chức danh thành kỹ năng.
3. Độ chi tiết của máy cao hơn người gán nhãn (ví dụ gán nhãn chỉ lấy "Python", máy bóc tách thêm "Pandas", "NumPy").

| Tài liệu (ID) | Kỹ năng máy trích xuất dư | Loại kỹ năng | Dẫn chứng văn bản (Snippet) |
| :---: | :--- | :---: | :--- |
| `JD_2170822` | **Chủ động & Trách nhiệm** | `SOFT` | Chủ động cập nhật thông tin công nghệ về AI... |
| `JD_2170822` | **Machine Learning** | `HARD` | ở lên chuyên ngành CNTT, Khoa học máy tính, Công nghệ phần mềm - Tố... |
| `JD_2170822` | **SQL** | `HARD` | n trị cơ sở dữ liệu RDBMS (MS SQL, Postgres SQL), NoSQL (MongoD... |
| `JD_2294268` | **Làm việc nhóm** | `SOFT` | phối hợp và đào tạo người dùng tốt... |
| `JD_2294268` | **Giải quyết vấn đề** | `SOFT` | kỹ năng phân tích, xử lý vấn đề... |
| `JD_2300563` | **Adobe Illustrator** | `TOOL` | và các phần mềm 2D (AI, PTS,..) là một lợi thế lớn... |
| `JD_2300563` | **Adobe Photoshop** | `TOOL` | và các phần mềm 2D (AI, PTS,..) là một lợi thế lớn... |
| `JD_2294012` | **Tư duy logic & Phản biện** | `SOFT` | Strong organizational, analytical, and problem-solving skills.... |
| `JD_2294012` | **Quản lý thời gian** | `SOFT` | Strong organizational, analytical, and problem-solving skills.... |
| `JD_2294012` | **Chủ động & Trách nhiệm** | `SOFT` | Self-managed and self-motivated skills.... |
| `JD_2294012` | **LoadRunner** | `TOOL` | Performance Testing (jmeter, Loadrunner)... |
| `JD_2294012` | **Phân tích nghiệp vụ** | `HARD` | Project Manager, test leader, BA during planning and reporting... |
| `JD_2289755` | **Wi-Fi** | `TOOL` | có kiến thức cơ bản về mạng LAN/Wi-Fi... |
| `JD_2289755` | **Microsoft 365** | `TOOL` | n phần mềm. Quản trị hệ thống Microsoft 365: OneDrive, SharePoint, Teams.... |
| `JD_2294081` | **Làm việc nhóm** | `SOFT` | Phối hợp với các thành viên trong nhóm và các bộ phận liên quan... |

### 3.3. Lỗi Nhầm lẫn Phân loại Loại Kỹ năng (Skill Type Mismatches)
*Định nghĩa:* Máy tìm đúng kỹ năng nhưng phân loại sai nhóm (ví dụ: Gold gán nhãn là `TOOL`, máy gán là `HARD` hoặc ngược lại).

| Tài liệu (ID) | Tên kỹ năng | Nhãn Máy gán | Nhãn Gold chuẩn | Dẫn chứng ngữ cảnh |
| :---: | :--- | :---: | :---: | :--- |

---

## 4. ĐỀ XUẤT CẢI TIẾN PIPELINE
1. **Tinh chỉnh Prompt phân định HARD vs TOOL:** Bổ sung ví dụ đối sánh cụ thể (ngôn ngữ lập trình -> `HARD`, phần mềm/IDE/thư viện -> `TOOL`).
2. **Cập nhật danh mục Stop-skills:** Loại bỏ triệt để các tính từ tính cách (nhiệt tình, trung thực, chịu khó) ra khỏi nhóm kỹ năng mềm.
3. **Canonical Post-Processing:** Tiếp tục mở rộng từ điển chuẩn hóa đồng nghĩa để tăng độ phủ và độ hội tụ giữa tiếng Anh và tiếng Việt.
