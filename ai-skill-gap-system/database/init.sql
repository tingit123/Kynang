-- ================================================================
--  AI SKILL GAP SYSTEM – DATABASE INITIALIZATION SCRIPT
--  Khởi tạo cơ sở dữ liệu MySQL cho hệ thống phát hiện kỹ năng
-- ================================================================

CREATE DATABASE IF NOT EXISTS skillgap_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE skillgap_db;

-- ─── BẢNG 1: Tin tuyển dụng ───────────────────────────────────
CREATE TABLE IF NOT EXISTS job_postings (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  title           VARCHAR(300) NOT NULL,
  company         VARCHAR(200) NOT NULL,
  location        VARCHAR(100) DEFAULT 'Cần Thơ',
  industry        ENUM('IT', 'Du lịch', 'Logistics', 'Kinh tế', 'Khác') NOT NULL,
  description     TEXT,
  salary_min      INT,
  salary_max      INT,
  posted_date     DATE,
  source_url      VARCHAR(500),
  source_platform VARCHAR(50),
  ai_classified   BOOLEAN DEFAULT FALSE,
  duplicate_hash  VARCHAR(64),
  duplicate_group INT,
  created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
  student_code    VARCHAR(20) UNIQUE NOT NULL,
  full_name       VARCHAR(100) NOT NULL,
  major           VARCHAR(100),
  year_of_study   INT,
  institution     VARCHAR(200),
  completed_at    DATE,
  created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
  skill_id        INT NOT NULL,
  course_name     VARCHAR(300) NOT NULL,
  platform        VARCHAR(100),
  url             VARCHAR(500),
  priority        INT DEFAULT 1,
  FOREIGN KEY (skill_id) REFERENCES skill_catalog(id)
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
('Customer Service',  'Du lịch',  30.0, 20.0, 10.0, '+6%');
