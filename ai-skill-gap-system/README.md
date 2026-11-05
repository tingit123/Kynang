<div align="center">

# 🧠 SkillGap AI
### Hệ Thống AI Phân Tích & Phát Hiện Kỹ Năng Thiếu Hụt Lao Động
**Cần Thơ · 2026**

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)](https://docker.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?logo=mysql)](https://mysql.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

</div>

---

## 📖 Giới Thiệu

**SkillGap AI** là hệ thống phân tích khoảng cách kỹ năng lao động sử dụng AI, được xây dựng cho thị trường lao động tại Cần Thơ. Hệ thống:

- 🕷️ **Cào dữ liệu** 1,000+ tin tuyển dụng từ TopCV và 500 CV sinh viên
- 🤖 **Dùng LLM (GPT-4o / Gemini)** để làm sạch và trích xuất kỹ năng theo cấu trúc phân cấp
- 📊 **Tính Gap = Demand – Supply** để tìm kỹ năng thiếu hụt theo từng ngành
- 🎯 **Gợi ý nghề nghiệp + khóa học** cá nhân hóa cho từng người lao động

---

## 🗂️ Cấu Trúc Dự Án

```
ai-skill-gap-system/
│
├── 📄 docker-compose.yml          ← Chạy toàn bộ hệ thống 1 lệnh
├── 📄 .env.example                ← Mẫu biến môi trường (copy → .env)
│
├── 📁 database/
│   ├── init.sql                   ← Script tạo schema MySQL tự động
│   └── config/
│
├── 📁 services/                   ← Các microservice backend
│   │
│   ├── 📁 data-crawler/           ← Module 1: Thu thập dữ liệu
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── src/
│   │       ├── crawler.py         ← Cào TopCV / VietnamWorks
│   │       ├── cleaner.py         ← Làm sạch, loại trùng lặp
│   │       └── scheduler.py       ← Lịch cào tự động (6h/lần)
│   │
│   ├── 📁 ai-nlp-worker/          ← Module 2: AI phân tích
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── src/
│   │       ├── extractor.py       ← Trích xuất kỹ năng từ JD/CV
│   │       ├── classifier.py      ← Phân loại theo ngành
│   │       └── gap_analyzer.py    ← Tính Demand, Supply, Gap
│   │
│   └── 📁 core-api-backend/       ← Module 3: FastAPI REST API
│       ├── Dockerfile
│       ├── requirements.txt
│       └── src/
│           ├── main.py
│           ├── database.py
│           ├── routers/           ← /skills, /jobs, /surveys, /courses
│           ├── controllers/
│           └── models/            ← SQLAlchemy models
│
└── 📁 apps/                       ← Frontend
    ├── 📁 auth-web/               ← 🎃 Cổng Đăng nhập / Đăng ký (Halloween theme)
    │   └── index.html
    ├── 📁 admin-web-dashboard/    ← ⭐ Dashboard chính (HTML + Chart.js)
    │   └── index.html
    └── 📁 mobile-survey-app/      ← App khảo sát sinh viên
```

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy

### Yêu cầu hệ thống
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/Mac/Linux)
- Git

### Bước 1 – Clone dự án
```bash
git clone https://github.com/<your-username>/ai-skill-gap-system.git
cd ai-skill-gap-system
```

### Bước 2 – Cấu hình biến môi trường
```bash
# Sao chép file mẫu
copy .env.example .env        # Windows
# hoặc
cp .env.example .env          # Linux/Mac

# Mở .env và điền các giá trị thật (OPENAI_API_KEY, v.v.)
```

### Bước 3 – Chạy toàn bộ hệ thống
```bash
docker-compose up -d
```

### Bước 4 – Truy cập ứng dụng

| Dịch vụ | URL |
|---|---|
| 🎃 **Đăng Nhập / Đăng Ký (Auth Web)** | http://localhost:8081 |
| 🖥️ **Dashboard** | http://localhost:8080 |
| ⚡ **API Docs (Swagger)** | http://localhost:8000/docs |
| 🗃️ **API Redoc** | http://localhost:8000/redoc |

---

## 🔐 Đăng Nhập & Phân Quyền

Hệ thống sử dụng cơ chế xác thực tập trung qua JWT lưu trong Cookie HttpOnly (`SameSite=Lax`, hết hạn 8 giờ) với 4 chức vụ người dùng:

### 1. Bảng phân quyền 4 chức vụ
| Chức vụ | Vai trò (`users.role`) | Đăng ký trực tuyến | Quyền hạn trên hệ thống |
|---|---|---|---|
| **ADMIN** | `admin` | ❌ (Chỉ tạo thủ công) | Toàn quyền quản trị hệ thống, duyệt đối tác, xem tất cả menu |
| **Người lao động** | `worker` | ✅ | Xem Dashboard, Kỹ năng mềm, Kỹ năng ngành, Gợi ý nghề nghiệp & phân tích CV |
| **Nhà tuyển dụng** | `employer` | ✅ (Chờ duyệt) | Xem Dashboard, Kỹ năng mềm, Kỹ năng ngành, Quản lý tin tuyển dụng |
| **Đơn vị đào tạo** | `course_provider` | ✅ (Chờ duyệt) | Xem Dashboard, Kỹ năng mềm, Kỹ năng ngành, Quản lý khóa học |

### 2. Quy tắc đăng ký
- Chỉ cho phép đăng ký trực tuyến 3 chức vụ: **Người lao động**, **Nhà tuyển dụng**, **Đơn vị đào tạo**.
- Mọi nỗ lực gửi `role="admin"` qua API đều bị từ chối với mã lỗi `403 Forbidden`.
- Tài khoản **Nhà tuyển dụng** và **Đơn vị đào tạo** sau khi đăng ký sẽ ở trạng thái chờ duyệt (`is_verified = 0`).

### 3. Cách tạo tài khoản Admin
Khởi tạo tài khoản Quản trị viên thông qua dòng lệnh bằng Docker Compose (mật khẩu nhập ẩn an toàn bằng `getpass` và băm `bcrypt`):
```bash
docker compose exec core-api python src/scripts/create_admin.py
```


---

## ✨ Tính Năng Dashboard

| Trang | Mô tả |
|---|---|
| 📊 **Tổng Quan** | KPI: 1,000 JD · 500 CV · Gap trung bình · Biểu đồ |
| ⭐ **Kỹ Năng Mềm** | Top 10 kỹ năng mềm chung + 3 biểu đồ Demand/Supply/Gap |
| 💻 **Kỹ Năng Theo Ngành** | 5 tab ngành → Top 10 kỹ năng + phân cấp nhóm |
| 🎯 **Gợi Ý Nghề Nghiệp** | AI Chẩn đoán lỗ hổng + Kê đơn khóa học bù đắp |
| 👥 **Người Lao Động** | Quản lý 500 CV đã AI phân loại |
| 🏢 **Nhà Tuyển Dụng** | Đăng và quản lý tin tuyển dụng |
| 📚 **Khóa Học** | Nhà cung cấp đăng khóa học theo kỹ năng |
| ⚙️ **Admin** | Quản lý toàn bộ tài khoản hệ thống |

---

## 🛠️ Tech Stack

| Tầng | Công nghệ |
|---|---|
| **Frontend Dashboard** | HTML5, Vanilla CSS, Chart.js 4.4 |
| **Backend API** | Python 3.11, FastAPI, SQLAlchemy |
| **AI / NLP** | spaCy, GPT-4o (OpenAI), Gemini |
| **Database** | MySQL 8.0 |
| **Data Crawler** | Scrapy, Selenium, BeautifulSoup4 |
| **DevOps** | Docker, docker-compose |

---

## 📊 Luồng Dữ Liệu

```
TopCV (1,000 JD) ──┐
                   ├──► Data Crawler ──► Raw DB
CV Sinh viên(500) ─┘         │
                              ▼
                         LLM Cleaner (GPT-4o/Gemini)
                              │
                         Skill Extractor
                         (Nhóm lớn → Nhóm nhỏ)
                              │
                         Gap Calculator
                         (Demand – Supply = Gap)
                              │
                         MySQL Database
                              │
                    ┌─────────┴──────────┐
                    ▼                    ▼
              Dashboard UI       Recommendation Engine
              (Biểu đồ)         (Gợi ý nghề + khóa học)
```

---

## 👥 Nhóm Phát Triển

> Dự án đồ án – Trường Đại học Cần Thơ · 2026

---

## 📜 License

MIT License – Xem file [LICENSE](LICENSE) để biết thêm chi tiết.

## Đối chiếu CV với yêu cầu tin tuyển dụng — MVP

Employer → Ứng viên dùng API thật; chọn hồ sơ và bấm **Đối chiếu yêu cầu**.
Yêu cầu lấy từ `extracted_skills`. Mỗi dẫn chứng được backend kiểm tra trên
`cv_snapshot_text`, hiển thị vị trí trong bản văn đã nộp và cho HR xác nhận/sửa
kèm lý do. Giữ nguyên nhận định gốc; không chấm điểm, xếp hạng hay tự từ chối.
Đây là đối chiếu nội dung, chưa xác minh năng lực. MVP chưa lưu/hiển thị PDF gốc.

Chạy thử trong PowerShell, tại thư mục chứa `docker-compose.yml`:

```powershell
$env:EVIDENCE_PROVIDER = 'keyword' # Demo offline, không gửi CV tới LLM
docker compose up -d
docker compose cp seed_demo_evidence.py core-api:/app/seed_demo_evidence.py
docker compose exec -T core-api python /app/seed_demo_evidence.py
```

Script in tài khoản `evidence.employer@demo.local` và mật khẩu ngẫu nhiên.
Có thể truyền `DEMO_PASSWORD` bằng `docker compose exec -e DEMO_PASSWORD=...`.
Seed chạy lại không tạo trùng hồ sơ; mật khẩu employer được cập nhật mỗi lần chạy.
Đăng nhập tại <http://localhost:8081>, mở
<http://localhost:8080/#/employer/candidates>. Có 38 hồ sơ mẫu, 6 yêu cầu.
Email đuôi `@demo.local` là dấu nhận diện hồ sơ mẫu tạm thời, chưa phải trường
phân loại dữ liệu chính thức. Script tương thích role `candidate` trên DB cũ.

Mặc định cấu hình `EVIDENCE_PROVIDER=auto`: Gemini → Groq → từ khóa.
Nếu không có key, `auto` dùng từ khóa và lưu `done`. Nếu các LLM được cấu hình
đều lỗi, run vẫn lưu `error`, provider `keyword` và mã
`LLM_UNAVAILABLE_KEYWORD_FALLBACK`; các dòng từ khóa chỉ là đối chiếu dự phòng.
Ép `gemini`/`groq` mà lỗi
thì lưu `error`, không mất đơn và có thể chạy lại. Email/số điện thoại được che
trước khi gửi LLM; không phải cơ chế ẩn danh hoàn toàn. Bộ từ khóa chỉ nhận
diện tên/alias đơn giản, chưa hiểu phủ định hoặc mức độ kinh nghiệm.
CV dưới 40 ký tự không tính khoảng trắng được xem là chưa đọc được.

Frontend hiện được nginx phục vụ từ `index.html`, không có bước build JSX.
Trang thật và `EmployerCandidatesPage.jsx` dùng chung `src/employer-evidence.js`.
Nút xác nhận/mời chuyển sang quy trình xem trước và gửi thông báo bên dưới.

Chạy pytest offline (LLM được mock, SQLite bật foreign keys):

```powershell
docker compose exec -T core-api mkdir -p /app/tests
docker compose cp services/core-api-backend/tests/test_evidence.py core-api:/app/tests/test_evidence.py
docker compose exec -T core-api pip install 'pytest>=8,<9'
docker compose exec -T core-api python -m pytest tests/test_evidence.py -q -p no:cacheprovider
```

Để phát triển ngoài Docker, cài `services/core-api-backend/requirements-dev.txt`.

## Đăng nhập nhanh employer demo

Trang chủ → Đăng nhập → Đăng nhập cơ bản → **Employer (Tuyển dụng)**.
Không cần nhập email/mật khẩu. Nút dùng tài khoản `evidence.employer@demo.local`
đã seed, tạo cookie HttpOnly/JWT thật và mở danh sách ứng viên. Không tự tạo tài
khoản, không đổi mật khẩu, không tạo trạng thái đăng nhập giả khi API thất bại.

Bản localhost hiện tại đã bật. Để bật lại khi tạo lại container:

```powershell
docker compose -f docker-compose.yml -f docker-compose.demo.yml up -d --no-deps core-api
```

Bản Compose mặc định để `DEMO_EMPLOYER_LOGIN=0`; chỉ override demo mới bật `1`.
Endpoint POST `/api/auth/demo/employer` chỉ chọn đúng tài khoản demo có role employer,
đang hoạt động và đã duyệt; kiểm tra host/origin localhost. Đây là tài khoản demo
được vào không mật khẩu khi bật, không dùng chế độ này cho triển khai thật. Các vai
trò demo khác giữ cách hoạt động cũ. Lỗi có thông báo trong form cơ bản.

Đã kiểm tra 12 trường hợp cho tính năng này, cùng Chrome trắng: bấm Employer khi
hai ô đăng nhập rỗng, API /me trả employer thật, tải lại trang vẫn giữ phiên.

## Ứng viên và Tuyển dụng nhanh — giao diện mới

Hai mục độc lập trên thanh bên trái:

- **Ứng viên**: danh sách hồ sơ theo tin, có nhãn kỹ năng dựa trên kết quả đối chiếu đã lưu. Bấm một ứng viên để xem dẫn chứng và CV gốc, hoặc soạn thông báo ngay trong hồ sơ.
  Dùng danh sách chọn hoặc nút trước/sau để đổi người ngay trong phần chi tiết.
  Hai nút **Dẫn chứng / CV gốc** nằm cạnh nhau phía trên. Nút **Tuyển dụng** mở ngay
  trình soạn thông báo cho đúng người đang xem, không đổi trang hoặc chạy lại bộ lọc.
- **Tuyển dụng nhanh**: <http://localhost:8080/#/employer/recruitment>. Bộ lọc luôn mở,
  chọn nhanh kỹ năng theo IT, Du lịch, Logistics, Kinh tế hoặc nhập bổ sung.
  Kỹ năng đã chọn nằm trong khung riêng, có **Hoàn tác** tối đa 30 thao tác thêm/bỏ/xóa.
  Thông báo nhập thiếu nằm dưới ô bổ sung kỹ năng. Chọn số kỹ năng tối thiểu trong
  dropdown ở góc phải **Kết quả tuyển dụng** sau khi đã bấm **Lọc ứng viên**.
  Nút **Hoàn tác** nằm cạnh **Bỏ chọn tất cả**; tab thao tác có tên **Tìm ứng viên**.
  Chỉnh kỹ năng/dropdown không tự gọi đối chiếu. Không còn nút lưu bộ lọc, loại mục,
  bắt buộc/ưu tiên hoặc các chip so sánh x/y. Thay đổi tiêu chí làm khóa thao tác gửi
  cho đến khi lọc lại; kết quả lần trước có cảnh báo rõ ràng.

Kết quả ghi số kỹ năng có dẫn chứng; chưa đánh giá/lỗi/chưa đọc được không bị coi là 0.
HR review được ưu tiên khi tính kết quả. Không tự từ chối hoặc xác minh năng lực qua CV.
Danh sách tuyển dụng có 10 hồ sơ/trang; chọn tất cả xuyên trang. Tối đa **100 hồ sơ/đợt
 gửi**, **50 hồ sơ/lượt đối chiếu**; vượt 100 cần thu hẹp hoặc chia đợt, không cắt ngầm.

### CV tự tạo để demo

Đã viết mới 16 CV hư cấu cho bốn ngành, kèm tệp gốc trong `demo_cvs/`.
Tin `[CV tự tạo] Backend Developer` có Bích Ngọc, Văn An, Minh Quân, Gia Hân;
đây là hồ sơ mới lưu trong DB, không phải các thẻ giao diện hardcode trước đây.
Tin tự tạo được ưu tiên hiển thị. Dữ liệu cũ và lịch sử gửi vẫn giữ nguyên.

Sau khi seed tài khoản employer ở mục trước, chạy:

```powershell
# Xuất lại tệp gốc trên máy (không cần DB)
python seed_recruitment_cvs.py --write-files
# Nạp bổ sung, không ghi đè hồ sơ đã có
docker compose cp seed_recruitment_cvs.py core-api:/app/seed_recruitment_cvs.py
docker compose exec -T core-api python /app/seed_recruitment_cvs.py
```

Đăng nhập `evidence.employer@demo.local` bằng mật khẩu từ seed trước đó (không bị đổi
bởi script mới). **CV gốc** hỗ trợ PDF, PNG, JPG, WEBP và TXT; mở phóng lớn và tải nguyên tệp.
Nhà tuyển dụng có quyền với tin (hoặc admin) có thể **Tải lên CV** ngay trong hồ sơ,
tối đa 5 MB; PDF tối đa 30 trang, không có mật khẩu. Tệp được kiểm tra nội dung thực,
lưu bền vững trong DB và chỉ đọc được qua API có xác thực. Chưa hỗ trợ DOCX.
Tải tệp mới sẽ thay CV của hồ sơ sau xác nhận; nội dung trích xuất thay đổi sẽ làm
kết quả cũ mất hiệu lực. PDF có lớp văn bản được đọc cục bộ; ảnh dùng OCR cục bộ.
PDF scan hoặc ảnh chưa đọc được vẫn xem được bản gốc, nhưng trạng thái đối chiếu
là chưa đọc được, không sinh nội dung thay thế. Dẫn chứng không còn bản văn bên dưới.
Hồ sơ cũ thiếu tệp gốc sẽ báo rõ, không dựng bản trích xuất thành tệp gốc giả.

### Thông báo tuyển dụng

Chọn hồ sơ → Xác nhận hồ sơ/Mời phỏng vấn → điền thông tin → **Gửi ngay**; hoặc mở **Xem trước** rồi gửi nếu muốn kiểm tra bản cá nhân hóa trước.
HR được sửa tiêu đề và toàn bộ nội dung, dùng biến cá nhân hóa hoặc văn bản thường.
**Lưu mẫu thông báo** lưu riêng trong DB theo tài khoản và loại thông báo (tối đa 40 mẫu);
chọn lại ở dropdown. Cùng tên/cùng loại cập nhật mẫu đã có. Mẫu chỉ lưu lời nhắn,
không lưu thời gian/địa điểm/liên hệ của một lịch phỏng vấn cụ thể. **Mẫu đã lưu** được dàn ngang ở cuối form. **Xem trước** mở tab riêng trong hộp soạn,
hiển thị đầy đủ từng lời nhắn và cho quay lại chỉnh sửa; sửa nội dung yêu cầu xem trước lại.
Backend kiểm tra lại tiêu chí, liên hệ và kết quả. Tuyển dụng trực tiếp chỉ cho một
hồ sơ, không phụ thuộc bộ lọc, không tự đối chiếu và không tạo/sửa tiêu chí. Không có thu hồi
thông báo đã gửi. Ít nhất một kênh thành công mới chuyển trạng thái hồ sơ và ghi audit.
Lịch sử lưu từng người/kênh. Lỗi tạm được thử lại; `unknown` cần cảnh báo/xác nhận riêng;
không thử lại những mục đã gửi thành công.

Thông báo in-app lưu thật vào DB. Worker mở <http://localhost:8080/#/notifications>
để đọc; API không gửi kèm điểm/số kỹ năng nội bộ. SMTP chỉ bật khi đủ `SMTP_HOST`,
`SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM`; `SMTP_SECURITY` là `starttls`,
`ssl` hoặc `none`. Gửi riêng từng người, không CC/BCC. SMTP accepted chưa có nghĩa thư
đã vào inbox/đã đọc. Chưa cấu hình thì checkbox email bị khóa.

`NOTIFY_SIMULATE=0` mặc định. Thử lỗi trên bộ dữ liệu cũ bằng cách đặt `1` rồi chạy
`docker compose up -d --no-deps core-api`. Địa chỉ `notify-fail@fail.demo.local` sinh lỗi
 tạm, `notify-timeout@timeout.demo.local` sinh trạng thái chưa rõ. Có nhãn giả lập.
Thử xong tắt về `0` và chạy lại lệnh. Không tự gửi lại sau khởi động lại.



Sau khi lọc, hộp **Ưu tiên hiển thị** bên dưới ngưỡng số kỹ năng cho chọn nhiều kỹ
năng thuộc bộ lọc đã áp dụng. Backend đưa hồ sơ có nhiều kỹ năng ưu tiên có dẫn
chứng lên trước, rồi theo tổng số kỹ năng; vẫn giữ ngưỡng tối thiểu và phân trang.
Đây là ưu tiên thứ tự, không tự loại hồ sơ còn lại và không xác minh năng lực.

**Danh sách ứng viên** hiển thị các kỹ năng trong bộ lọc cho từng hồ sơ: màu xanh
là có dẫn chứng, xám là chưa có/chưa đánh giá (xem tooltip). Mặc định hiện bốn nhãn,
**Xem thêm** mở toàn bộ. Dấu sao nhận diện kỹ năng đang ưu tiên. Bấm dòng hoặc Enter/
Space khi dòng được focus để chọn; checkbox, nút xem hồ sơ và xem thêm giữ chức năng riêng.

Chỉ còn nút **Xem trước** trên thanh tab cạnh **Soạn thông báo**. Nút này kiểm tra
nội dung và báo lỗi đỏ ngay dưới thanh tab khi thiếu thông tin; bản xem trước hợp
lệ cho phép gửi trong tab đó. Form soạn cũng có **Gửi ngay**, không bắt mở tab xem trước.
Hệ thống vẫn kiểm tra server trước khi gửi, giữ đúng danh sách đã chọn (kể cả bỏ chọn
sau Chọn tất cả), báo lỗi thiếu thông tin và dùng mã chống gửi trùng khi thử lại.
Không có nút xem trước thứ hai ở cuối form.

### Kiểm thử

```powershell
docker compose exec -T core-api mkdir -p /app/tests
foreach ($testFile in @('test_evidence.py','test_quick_hire.py','test_notifications.py','test_demo_login.py')) {
  docker compose cp "services/core-api-backend/tests/$testFile" "core-api:/app/tests/$testFile"
}
docker compose exec -T core-api pip install 'pytest>=8,<9'
docker compose exec -T core-api python -m pytest tests -q -p no:cacheprovider
```

Bản nginx HTML đã thử bằng Chrome trên desktop và chiều rộng 390px. SMTP chưa gửi thực tế.
Chi tiết bản mới: [Báo cáo giao diện tuyển dụng](docs/RECRUITMENT_UI_REPORT.md).
Báo cáo giai đoạn trước: [Lọc và thông báo](docs/QUICK_HIRE_MVP_REPORT.md).
