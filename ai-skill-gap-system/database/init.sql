-- ================================================================
--  AI SKILL GAP SYSTEM – DATABASE INITIALIZATION SCRIPT
--  Khởi tạo cơ sở dữ liệu MySQL cho hệ thống phát hiện kỹ năng
-- ================================================================

CREATE DATABASE IF NOT EXISTS skillgap_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE skillgap_db;

-- ─── BẢNG 0: Người dùng & Phân quyền (Authentication & RBAC) ────
CREATE TABLE IF NOT EXISTS users (
  id                  INT AUTO_INCREMENT PRIMARY KEY,
  email               VARCHAR(150) UNIQUE NOT NULL,
  password_hash       VARCHAR(255) NOT NULL,
  full_name           VARCHAR(150) NOT NULL,
  role                ENUM('admin', 'candidate', 'employer', 'provider') NOT NULL DEFAULT 'candidate',
  is_deleted          BOOLEAN DEFAULT FALSE,
  is_active           BOOLEAN NOT NULL DEFAULT TRUE,
  phone               VARCHAR(30) NULL,
  company_name        VARCHAR(200) NULL,
  company_logo_url    VARCHAR(500) NULL,
  company_description TEXT NULL,
  latest_cv_analysis  TEXT NULL,
  created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tài khoản Admin mặc định (mật khẩu: admin123 - bcrypt hash)
INSERT INTO users (id, email, password_hash, full_name, role) VALUES
(1, 'admin@skillgap.com', '$2b$12$7SpBJ3oI.ZvL9uW1Id4MOuUYEHgm.WKCwkuyr93HFuf94q1zeawW2', 'Hệ Thống Admin', 'admin')
ON DUPLICATE KEY UPDATE full_name = VALUES(full_name);

-- ─── BẢNG 0.1: Token Blacklist (Đăng xuất) ──────────────────────
CREATE TABLE IF NOT EXISTS token_blacklist (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  token          VARCHAR(500) UNIQUE NOT NULL,
  blacklisted_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─── BẢNG 0.2: Hồ sơ công ty (Company Profile) ─────────────────
CREATE TABLE IF NOT EXISTS companies (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  employer_id INT NULL,
  name        VARCHAR(200) NOT NULL,
  logo_url    VARCHAR(500),
  description TEXT,
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (employer_id) REFERENCES users(id) ON DELETE SET NULL
);

-- ─── BẢNG 1: Tin tuyển dụng ───────────────────────────────────
CREATE TABLE IF NOT EXISTS job_postings (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  employer_id     INT NULL,
  title           VARCHAR(300) NOT NULL,
  company         VARCHAR(200) NOT NULL,
  location        VARCHAR(100) DEFAULT 'Cần Thơ',
  industry        VARCHAR(50) NOT NULL,
  description     TEXT,
  salary_min      INT,
  salary_max      INT,
  posted_date     DATE,
  source_url      VARCHAR(500),
  source_platform VARCHAR(50),
  ai_classified   BOOLEAN DEFAULT FALSE,
  is_deleted      BOOLEAN DEFAULT FALSE,
  duplicate_hash  VARCHAR(64),
  duplicate_group INT,
  created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (employer_id) REFERENCES users(id) ON DELETE SET NULL
);

-- ─── BẢNG 1.1: Ứng tuyển việc làm (Job Applications) ───────────
CREATE TABLE IF NOT EXISTS job_applications (
  id               INT AUTO_INCREMENT PRIMARY KEY,
  job_id           INT NOT NULL,
  candidate_id     INT NOT NULL,
  cv_snapshot_text TEXT,
  status           VARCHAR(50) DEFAULT 'applied',
  applied_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (job_id) REFERENCES job_postings(id) ON DELETE CASCADE,
  FOREIGN KEY (candidate_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ─── BẢNG 2: Kỹ năng được AI trích xuất ──────────────────────
CREATE TABLE IF NOT EXISTS extracted_skills (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  job_id          INT NOT NULL,
  skill_name      VARCHAR(100) NOT NULL,
  skill_category  VARCHAR(50),
  confidence      FLOAT DEFAULT 0.0,
  FOREIGN KEY (job_id) REFERENCES job_postings(id) ON DELETE CASCADE
);

-- ─── BẢNG 3: Danh mục kỹ năng chuẩn ─────────────────────────
CREATE TABLE IF NOT EXISTS skill_catalog (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  skill_name      VARCHAR(100) UNIQUE NOT NULL,
  industry        VARCHAR(50),
  demand_pct      FLOAT DEFAULT 0.0,
  supply_pct      FLOAT DEFAULT 0.0,
  gap_pct         FLOAT DEFAULT 0.0,
  trend_pct       VARCHAR(20),
  updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ─── BẢNG 4: Khảo sát sinh viên ─────────────────────────────
CREATE TABLE IF NOT EXISTS survey_responses (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  user_id         INT NULL,
  student_code    VARCHAR(20) UNIQUE NOT NULL,
  full_name       VARCHAR(100) NOT NULL,
  major           VARCHAR(100),
  year_of_study   INT,
  institution     VARCHAR(200),
  completed_at    DATE,
  created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- ─── BẢNG 5: Đánh giá kỹ năng từ khảo sát ───────────────────
CREATE TABLE IF NOT EXISTS survey_skill_ratings (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  survey_id       INT NOT NULL,
  skill_id        INT NOT NULL,
  self_rating     INT CHECK (self_rating BETWEEN 0 AND 100),
  FOREIGN KEY (survey_id) REFERENCES survey_responses(id),
  FOREIGN KEY (skill_id)  REFERENCES skill_catalog(id)
);

-- ─── BẢNG 6: Gợi ý khóa học ──────────────────────────────────
CREATE TABLE IF NOT EXISTS course_recommendations (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  provider_id     INT NULL,
  skill_id        INT NOT NULL,
  course_name     VARCHAR(300) NOT NULL,
  platform        VARCHAR(100),
  url             VARCHAR(500),
  priority        INT DEFAULT 1,
  status          VARCHAR(50) DEFAULT 'pending',
  click_count     INT DEFAULT 0,
  is_deleted      BOOLEAN DEFAULT FALSE,
  FOREIGN KEY (skill_id) REFERENCES skill_catalog(id),
  FOREIGN KEY (provider_id) REFERENCES users(id) ON DELETE SET NULL
);

-- ─── DỮ LIỆU MẪU: skill_catalog ─────────────────────────────
INSERT INTO skill_catalog (skill_name, industry, demand_pct, supply_pct, gap_pct, trend_pct) VALUES
('Python',            'IT',       92.0, 32.0, 60.0, '+45%'),
('Data Analysis',     'IT',       68.0, 24.0, 44.0, '+30%'),
('Machine Learning',  'IT',       55.0, 12.0, 43.0, '+45%'),
('AI Ethics',         'IT',       38.0,  8.0, 30.0, '+60%'),
('English',           'Tất cả',   76.6, 42.0, 34.6, '+8%'),
('Digital Marketing', 'Kinh tế',  42.7, 26.7, 16.0, '+22%'),
('Logistics',         'Logistics', 45.0,28.0, 17.0, '+12%'),
('Communication',     'Tất cả',   35.3, 18.3, 17.0, '+4%'),
('Problem Solving',   'Tất cả',   38.1, 22.8, 15.3, '+5%'),
('Customer Service',  'Du lịch',  30.0, 20.0, 10.0, '+6%')
ON DUPLICATE KEY UPDATE demand_pct = VALUES(demand_pct);


-- System announcements: only admins publish, all users can read.
CREATE TABLE IF NOT EXISTS notifications (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  content TEXT NOT NULL,
  author_id INT NULL,
  created_at DATETIME NOT NULL,
  FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE SET NULL
);
