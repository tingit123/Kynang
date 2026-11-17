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
  role                ENUM('admin', 'worker', 'employer', 'course_provider', 'candidate', 'provider') NOT NULL DEFAULT 'worker',
  is_active           BOOLEAN DEFAULT TRUE,
  is_deleted          BOOLEAN DEFAULT FALSE,
  last_login_at       TIMESTAMP NULL,
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

-- ─── BẢNG 0.3: Người lao động / Ứng viên (Workers) ──────────────
CREATE TABLE IF NOT EXISTS workers (
  worker_id   INT AUTO_INCREMENT PRIMARY KEY,
  user_id     INT UNIQUE NULL,
  full_name   VARCHAR(150) NULL,
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ─── BẢNG 0.4: Nhà tuyển dụng (Employers) ─────────────────────
CREATE TABLE IF NOT EXISTS employers (
  employer_id  INT AUTO_INCREMENT PRIMARY KEY,
  user_id      INT UNIQUE,
  company_id   INT NULL,
  contact_name VARCHAR(150) NULL,
  phone        VARCHAR(50) NULL,
  is_verified  TINYINT(1) DEFAULT 0,
  created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ─── BẢNG 0.5: Đơn vị đào tạo (Course Providers) ───────────────
CREATE TABLE IF NOT EXISTS course_providers (
  provider_id   INT AUTO_INCREMENT PRIMARY KEY,
  user_id       INT UNIQUE,
  provider_name VARCHAR(200) UNIQUE,
  website       VARCHAR(500) NULL,
  description   TEXT NULL,
  is_verified   TINYINT(1) DEFAULT 0,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
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
  cv_original_text TEXT,
  cv_original_filename VARCHAR(255),
  cv_original_blob MEDIUMBLOB,
  cv_original_mime VARCHAR(80),
  status           VARCHAR(50) DEFAULT 'applied',
  applied_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (job_id) REFERENCES job_postings(id) ON DELETE CASCADE,
  FOREIGN KEY (candidate_id) REFERENCES users(id) ON DELETE CASCADE
);

-- CV evidence MVP: also created by SQLAlchemy for existing databases.
CREATE TABLE IF NOT EXISTS analysis_runs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  application_id INT NOT NULL,
  requirements_hash VARCHAR(64) NOT NULL,
  filter_profile_hash VARCHAR(64) NULL,
  requirements_snapshot TEXT NOT NULL,
  cv_hash VARCHAR(64) NOT NULL,
  provider VARCHAR(20) NOT NULL,
  status VARCHAR(20) NOT NULL,
  error_code VARCHAR(80) NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX ix_analysis_runs_application_id (application_id),
  FOREIGN KEY (application_id) REFERENCES job_applications(id)
);
CREATE TABLE IF NOT EXISTS application_evidence (
  id INT AUTO_INCREMENT PRIMARY KEY,
  run_id INT NOT NULL,
  requirement_name VARCHAR(100) NOT NULL,
  result VARCHAR(20) NOT NULL,
  quote TEXT NOT NULL,
  source_start INT NULL,
  source_end INT NULL,
  ai_result_original VARCHAR(20) NOT NULL,
  reviewer_id INT NULL,
  review_result VARCHAR(20) NULL,
  review_reason TEXT NULL,
  reviewed_at DATETIME NULL,
  INDEX ix_application_evidence_run_id (run_id),
  FOREIGN KEY (run_id) REFERENCES analysis_runs(id),
  FOREIGN KEY (reviewer_id) REFERENCES users(id)
);

-- Employer-owned filter and confirmed internal selection.
CREATE TABLE IF NOT EXISTS filter_profiles (
  id INT AUTO_INCREMENT PRIMARY KEY,
  job_id INT NOT NULL UNIQUE,
  owner_user_id INT NOT NULL,
  name VARCHAR(150) NOT NULL,
  items JSON NOT NULL,
  profile_hash VARCHAR(64) NOT NULL,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (job_id) REFERENCES job_postings(id),
  FOREIGN KEY (owner_user_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS quick_hire_batches (
  id INT AUTO_INCREMENT PRIMARY KEY,
  job_id INT NOT NULL,
  actor_id INT NOT NULL,
  profile_snapshot JSON NOT NULL,
  idempotency_key VARCHAR(100) NOT NULL UNIQUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (job_id) REFERENCES job_postings(id),
  FOREIGN KEY (actor_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS notification_templates (
  id INT AUTO_INCREMENT PRIMARY KEY,
  owner_id INT NOT NULL,
  action_type VARCHAR(30) NOT NULL,
  name VARCHAR(100) NOT NULL,
  title_template VARCHAR(300) NOT NULL,
  body_template TEXT NOT NULL,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_notification_template_owner (owner_id, action_type, name),
  INDEX ix_notification_templates_owner_id (owner_id),
  FOREIGN KEY (owner_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS notification_batches (
  id INT AUTO_INCREMENT PRIMARY KEY,
  job_id INT NOT NULL,
  actor_id INT NOT NULL,
  action_type VARCHAR(30) NOT NULL,
  channels JSON NOT NULL,
  content JSON NOT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'processing',
  idempotency_key VARCHAR(100) NOT NULL UNIQUE,
  request_hash VARCHAR(64) NOT NULL,
  simulated BOOLEAN NOT NULL DEFAULT FALSE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX ix_notification_batches_job_id (job_id),
  FOREIGN KEY (job_id) REFERENCES job_postings(id),
  FOREIGN KEY (actor_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS notification_recipients (
  id INT AUTO_INCREMENT PRIMARY KEY,
  batch_id INT NOT NULL,
  application_id INT NOT NULL,
  channel VARCHAR(20) NOT NULL,
  user_id INT NULL,
  address VARCHAR(150),
  candidate_name VARCHAR(150) NOT NULL,
  title VARCHAR(300) NOT NULL,
  body TEXT NOT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'queued',
  attempt_count INT NOT NULL DEFAULT 0,
  last_error TEXT,
  error_kind VARCHAR(30),
  retryable BOOLEAN NOT NULL DEFAULT FALSE,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_notification_target (batch_id, application_id, channel),
  INDEX ix_notification_recipients_batch_id (batch_id),
  FOREIGN KEY (batch_id) REFERENCES notification_batches(id),
  FOREIGN KEY (application_id) REFERENCES job_applications(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS user_notifications (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  recipient_id INT NOT NULL UNIQUE,
  title VARCHAR(300) NOT NULL,
  body TEXT NOT NULL,
  simulated BOOLEAN NOT NULL DEFAULT FALSE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  read_at DATETIME NULL,
  INDEX ix_user_notifications_user_id (user_id),
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (recipient_id) REFERENCES notification_recipients(id)
);
CREATE TABLE IF NOT EXISTS application_status_events (
  id INT AUTO_INCREMENT PRIMARY KEY,
  application_id INT NOT NULL,
  actor_id INT NOT NULL,
  from_status VARCHAR(50) NOT NULL,
  to_status VARCHAR(50) NOT NULL,
  batch_id INT NULL,
  notification_batch_id INT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX ix_application_status_events_application_id (application_id),
  INDEX ix_application_status_events_batch_id (batch_id),
  FOREIGN KEY (application_id) REFERENCES job_applications(id),
  FOREIGN KEY (actor_id) REFERENCES users(id),
  FOREIGN KEY (batch_id) REFERENCES quick_hire_batches(id),
  FOREIGN KEY (notification_batch_id) REFERENCES notification_batches(id)
);

-- ─── BẢNG 2: Kỹ năng được AI trích xuất ──────────────────────
CREATE TABLE IF NOT EXISTS recruiter_contacts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  owner_id INT NOT NULL,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL DEFAULT '',
  title VARCHAR(100) NOT NULL DEFAULT '',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_recruiter_contact (owner_id, name, email),
  INDEX ix_recruiter_contacts_owner_id (owner_id),
  FOREIGN KEY (owner_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS application_processes (
  application_id INT PRIMARY KEY,
  stage VARCHAR(40) NOT NULL DEFAULT 'new',
  assignee_id INT NULL,
  version INT NOT NULL DEFAULT 0,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX ix_application_processes_stage (stage),
  INDEX ix_application_processes_assignee_id (assignee_id),
  FOREIGN KEY (application_id) REFERENCES job_applications(id),
  FOREIGN KEY (assignee_id) REFERENCES recruiter_contacts(id)
);
CREATE TABLE IF NOT EXISTS application_process_events (
  id INT AUTO_INCREMENT PRIMARY KEY,
  application_id INT NOT NULL,
  actor_id INT NOT NULL,
  actor_name VARCHAR(150) NOT NULL,
  event_type VARCHAR(40) NOT NULL,
  details JSON NOT NULL,
  reason TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX ix_application_process_events_application_id (application_id),
  FOREIGN KEY (application_id) REFERENCES job_applications(id),
  FOREIGN KEY (actor_id) REFERENCES users(id)
);

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
