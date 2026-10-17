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
