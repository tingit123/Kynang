-- =====================================================================
-- skill_intelligence : SCHEMA SẠCH CHUẨN 3NF (PHIÊN BẢN 2)
-- Hệ thống dự đoán thiếu hụt nhân lực - ngành lập trình/4 ngành - Đà Nẵng
-- Yêu cầu: MySQL 8.0+ (dùng window function và REGEXP_SUBSTR)
--
-- ESCO chỉ là dữ liệu hỗ trợ: schema này KHÔNG có bảng ESCO, chỉ có cột
-- esco_uri (NULL được) ở skill_categories và skills để đối chiếu khi cần.
--
-- Lưu ý collation: các bảng dùng utf8mb4 + collation mặc định của server.
-- Nếu FK tới jobs_raw báo lỗi 3780/1215, chạy SHOW CREATE TABLE jobs_raw
-- rồi thêm đúng COLLATE của bảng đó vào các bảng mới.
-- =====================================================================

USE skill_intelligence;
SET NAMES utf8mb4;

-- ---------------------------------------------------------------------
-- (TÙY CHỌN) Nếu đã chạy clean_schema_3nf.sql (v1) thì bỏ comment khối
-- này để xóa các bảng cũ có cấu trúc khác.
-- ---------------------------------------------------------------------
-- SET FOREIGN_KEY_CHECKS = 0;
-- DROP TABLE IF EXISTS job_occupation_matches, esco_occupation_skills, esco_occupations,
--     job_skills, job_locations, skill_aliases, skills, esco_skills,
--     jobs_clean, industry_isco_groups;
-- SET FOREIGN_KEY_CHECKS = 1;

-- =====================================================================
-- PHẦN 1. BẢNG THAM CHIẾU
-- =====================================================================

CREATE TABLE IF NOT EXISTS industries (
    industry_id      TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,
    industry_code    VARCHAR(20)  NOT NULL,
    industry_name_vi VARCHAR(100) NOT NULL,
    industry_name_en VARCHAR(100) NOT NULL,
    PRIMARY KEY (industry_id),
    UNIQUE KEY uq_industry_code (industry_code),
    UNIQUE KEY uq_industry_name_vi (industry_name_vi)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Vị trí/nghề thuộc một ngành (dùng cho phân loại tin, CV và gợi ý nghề)
CREATE TABLE IF NOT EXISTS positions (
    position_id         INT UNSIGNED NOT NULL AUTO_INCREMENT,
    industry_id         TINYINT UNSIGNED NOT NULL,
    position_name       VARCHAR(150) NOT NULL,
    esco_occupation_uri VARCHAR(255) NULL,           -- ánh xạ sang nghề nghiệp chuẩn ESCO
    isco_group_code     VARCHAR(20)  NULL,           -- mã nhóm nghề ISCO-08
    PRIMARY KEY (position_id),
    UNIQUE KEY uq_position (industry_id, position_name),
    CONSTRAINT fk_pos_industry FOREIGN KEY (industry_id) REFERENCES industries (industry_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS provinces (
    province_id   SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
    province_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (province_id),
    UNIQUE KEY uq_province_name (province_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS education_levels (
    education_level_id TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,
    level_code         VARCHAR(20)  NOT NULL,
    level_name_vi      VARCHAR(100) NOT NULL,
    level_rank         TINYINT UNSIGNED NOT NULL,
    PRIMARY KEY (education_level_id),
    UNIQUE KEY uq_level_code (level_code),
    UNIQUE KEY uq_level_rank (level_rank)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Loại kỹ năng: HARD / SOFT / TOOL / KNOWLEDGE / CERTIFICATION / LANGUAGE
CREATE TABLE IF NOT EXISTS skill_types (
    skill_type_id TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,
    type_code     VARCHAR(20)  NOT NULL,
    type_name_vi  VARCHAR(100) NOT NULL,
    PRIMARY KEY (skill_type_id),
    UNIQUE KEY uq_type_code (type_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================================
-- PHẦN 2. KỸ NĂNG PHÂN CẤP: NHÓM LỚN -> NHÓM NHỎ -> KỸ NĂNG
-- =====================================================================

-- Cây nhóm tự tham chiếu (parent_category_id = NULL là nhóm lớn nhất)
CREATE TABLE IF NOT EXISTS skill_categories (
    category_id        INT UNSIGNED NOT NULL AUTO_INCREMENT,
    parent_category_id INT UNSIGNED NULL,
    category_name      VARCHAR(150) NOT NULL,
    esco_uri           VARCHAR(255) NULL,           -- chỉ để đối chiếu, có thể bỏ trống
    PRIMARY KEY (category_id),
    UNIQUE KEY uq_category_name (category_name),
    UNIQUE KEY uq_category_esco (esco_uri),
    KEY idx_cat_parent (parent_category_id),
    CONSTRAINT fk_cat_parent FOREIGN KEY (parent_category_id)
        REFERENCES skill_categories (category_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS skills (
    skill_id      INT UNSIGNED NOT NULL AUTO_INCREMENT,
    skill_name    VARCHAR(255) NOT NULL,
    skill_type_id TINYINT UNSIGNED NOT NULL,
    category_id   INT UNSIGNED NULL,               -- nhóm nhỏ chứa kỹ năng này
    esco_uri      VARCHAR(255) NULL,
    PRIMARY KEY (skill_id),
    UNIQUE KEY uq_skill_name (skill_name),
    UNIQUE KEY uq_skill_esco (esco_uri),
    KEY idx_skill_type (skill_type_id),
    KEY idx_skill_category (category_id),
    CONSTRAINT fk_skill_type     FOREIGN KEY (skill_type_id) REFERENCES skill_types (skill_type_id),
    CONSTRAINT fk_skill_category FOREIGN KEY (category_id)   REFERENCES skill_categories (category_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tên gọi khác của cùng một kỹ năng (tiếng Việt, viết tắt, biến thể)
CREATE TABLE IF NOT EXISTS skill_aliases (
    alias_id      INT UNSIGNED NOT NULL AUTO_INCREMENT,
    skill_id      INT UNSIGNED NOT NULL,
    alias_text    VARCHAR(255) NOT NULL,
    language_code CHAR(2) NOT NULL DEFAULT 'vi',
    PRIMARY KEY (alias_id),
    UNIQUE KEY uq_alias_text (alias_text),
    KEY idx_alias_skill (skill_id),
    CONSTRAINT fk_alias_skill FOREIGN KEY (skill_id) REFERENCES skills (skill_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================================
-- PHẦN 3. TÀI KHOẢN VÀ CÁC VAI TRÒ (ADMIN / NGƯỜI LAO ĐỘNG / NHÀ TUYỂN DỤNG / NHÀ CUNG CẤP KHÓA HỌC)
-- =====================================================================

CREATE TABLE IF NOT EXISTS users (
    user_id       INT UNSIGNED NOT NULL AUTO_INCREMENT,
    email         VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role          ENUM('admin','worker','employer','course_provider') NOT NULL,
    is_active     TINYINT(1) NOT NULL DEFAULT 1,      -- admin khóa/mở tài khoản
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login_at DATETIME NULL,
    PRIMARY KEY (user_id),
    UNIQUE KEY uq_user_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS companies (
    company_id   INT UNSIGNED NOT NULL AUTO_INCREMENT,
    company_name VARCHAR(255) NOT NULL,
    PRIMARY KEY (company_id),
    UNIQUE KEY uq_company_name (company_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS employers (
    employer_id  INT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id      INT UNSIGNED NOT NULL,
    company_id   INT UNSIGNED NOT NULL,
    contact_name VARCHAR(150) NULL,
    phone        VARCHAR(30)  NULL,
    is_verified  TINYINT(1) NOT NULL DEFAULT 0,       -- admin duyệt nhà tuyển dụng
    PRIMARY KEY (employer_id),
    UNIQUE KEY uq_employer_user (user_id),
    KEY idx_emp_company (company_id),
    CONSTRAINT fk_emp_user    FOREIGN KEY (user_id)    REFERENCES users (user_id) ON DELETE CASCADE,
    CONSTRAINT fk_emp_company FOREIGN KEY (company_id) REFERENCES companies (company_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS course_providers (
    provider_id   INT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id       INT UNSIGNED NOT NULL,
    provider_name VARCHAR(255) NOT NULL,
    website       VARCHAR(500) NULL,
    description   TEXT NULL,
    is_verified   TINYINT(1) NOT NULL DEFAULT 0,
    PRIMARY KEY (provider_id),
    UNIQUE KEY uq_provider_user (user_id),
    UNIQUE KEY uq_provider_name (provider_name),
    CONSTRAINT fk_prov_user FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================================
-- PHẦN 4. NGƯỜI LAO ĐỘNG VÀ CV (500 CV CÀO ĐƯỢC + NGƯỜI DÙNG ĐĂNG KÝ)
-- =====================================================================

-- Dữ liệu thô của CV. Nên ẩn danh hóa họ tên, SĐT, email trước khi lưu.
CREATE TABLE IF NOT EXISTS cvs_raw (
    cv_id         INT UNSIGNED NOT NULL AUTO_INCREMENT,
    source_name   VARCHAR(50)  NULL,
    source_url    VARCHAR(500) NULL,
    raw_text      LONGTEXT NOT NULL,
    crawled_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    llm_processed TINYINT(1) NOT NULL DEFAULT 0,
    PRIMARY KEY (cv_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Một worker là: CV cào được (cv_raw_id) và/hoặc người dùng đăng ký (user_id)
CREATE TABLE IF NOT EXISTS workers (
    worker_id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id            INT UNSIGNED NULL,
    cv_raw_id          INT UNSIGNED NULL,
    full_name          VARCHAR(150) NULL,
    province_id        SMALLINT UNSIGNED NULL,
    education_level_id TINYINT UNSIGNED NULL,
    school_name        VARCHAR(255) NULL,
    major              VARCHAR(255) NULL,
    graduation_year    SMALLINT UNSIGNED NULL,
    experience_years   DECIMAL(3,1) NULL,
    target_position_id INT UNSIGNED NULL,             -- nghề mong muốn (suy ra ngành)
    is_active          TINYINT(1) NOT NULL DEFAULT 1,
    created_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (worker_id),
    UNIQUE KEY uq_worker_user (user_id),
    UNIQUE KEY uq_worker_cv (cv_raw_id),
    KEY idx_w_province (province_id),
    KEY idx_w_edu (education_level_id),
    KEY idx_w_position (target_position_id),
    CONSTRAINT fk_w_user     FOREIGN KEY (user_id)            REFERENCES users (user_id) ON DELETE SET NULL,
    CONSTRAINT fk_w_cv       FOREIGN KEY (cv_raw_id)          REFERENCES cvs_raw (cv_id) ON DELETE SET NULL,
    CONSTRAINT fk_w_province FOREIGN KEY (province_id)        REFERENCES provinces (province_id),
    CONSTRAINT fk_w_edu      FOREIGN KEY (education_level_id) REFERENCES education_levels (education_level_id),
    CONSTRAINT fk_w_position FOREIGN KEY (target_position_id) REFERENCES positions (position_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Kỹ năng người lao động đang có (nguồn của "cung")
CREATE TABLE IF NOT EXISTS worker_skills (
    worker_id         INT UNSIGNED NOT NULL,
    skill_id          INT UNSIGNED NOT NULL,
    proficiency_level TINYINT UNSIGNED NULL,           -- 1..5, có thể để trống
    extraction_source ENUM('cv_llm','self_declared','course') NOT NULL,
    confidence_score  DECIMAL(4,3) NULL,
    PRIMARY KEY (worker_id, skill_id),
    KEY idx_ws_skill (skill_id),
    CONSTRAINT fk_ws_worker FOREIGN KEY (worker_id) REFERENCES workers (worker_id) ON DELETE CASCADE,
    CONSTRAINT fk_ws_skill  FOREIGN KEY (skill_id)  REFERENCES skills (skill_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================================
-- PHẦN 5. TIN TUYỂN DỤNG SẠCH (1.000 TIN TOPCV + TIN NHÀ TUYỂN DỤNG ĐĂNG)
-- =====================================================================

CREATE TABLE IF NOT EXISTS jobs (
    job_id                 INT UNSIGNED NOT NULL AUTO_INCREMENT,
    raw_job_id             VARCHAR(50)  NULL,          -- có giá trị nếu cào từ TopCV
    posted_by_employer_id  INT UNSIGNED NULL,          -- có giá trị nếu nhà tuyển dụng tự đăng
    title                  VARCHAR(255) NOT NULL,
    company_id             INT UNSIGNED NOT NULL,
    position_id            INT UNSIGNED NOT NULL,      -- ngành suy ra qua positions
    education_level_id     TINYINT UNSIGNED NULL,
    experience_min_years   DECIMAL(3,1) NULL,
    experience_max_years   DECIMAL(3,1) NULL,
    salary_min_vnd         BIGINT UNSIGNED NULL,       -- VND/tháng
    salary_max_vnd         BIGINT UNSIGNED NULL,
    is_salary_negotiable   TINYINT(1) NOT NULL DEFAULT 0,
    description            TEXT NULL,
    requirements           TEXT NULL,
    posted_date            DATE NULL,
    deadline               DATE NULL,
    status                 ENUM('active','closed','hidden') NOT NULL DEFAULT 'active',
    created_at             DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at             DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (job_id),
    UNIQUE KEY uq_job_raw (raw_job_id),
    KEY idx_job_employer (posted_by_employer_id),
    KEY idx_job_company (company_id),
    KEY idx_job_position (position_id),
    KEY idx_job_edu (education_level_id),
    KEY idx_job_posted (posted_date),
    CONSTRAINT fk_job_raw      FOREIGN KEY (raw_job_id)            REFERENCES jobs_raw (job_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_job_employer FOREIGN KEY (posted_by_employer_id) REFERENCES employers (employer_id)
        ON DELETE SET NULL,
    CONSTRAINT fk_job_company  FOREIGN KEY (company_id)            REFERENCES companies (company_id),
    CONSTRAINT fk_job_position FOREIGN KEY (position_id)           REFERENCES positions (position_id),
    CONSTRAINT fk_job_edu      FOREIGN KEY (education_level_id)    REFERENCES education_levels (education_level_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS job_locations (
    job_location_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    job_id          INT UNSIGNED NOT NULL,
    province_id     SMALLINT UNSIGNED NOT NULL,
    district_name   VARCHAR(100) NULL,
    PRIMARY KEY (job_location_id),
    KEY idx_jl_job (job_id),
    KEY idx_jl_province (province_id),
    CONSTRAINT fk_jl_job      FOREIGN KEY (job_id)      REFERENCES jobs (job_id) ON DELETE CASCADE,
    CONSTRAINT fk_jl_province FOREIGN KEY (province_id) REFERENCES provinces (province_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Kỹ năng thị trường yêu cầu (nguồn của "cầu")
CREATE TABLE IF NOT EXISTS job_skills (
    job_id            INT UNSIGNED NOT NULL,
    skill_id          INT UNSIGNED NOT NULL,
    requirement_level ENUM('required','preferred') NOT NULL DEFAULT 'required',
    extraction_source ENUM('topcv_tag','llm','employer') NOT NULL,
    confidence_score  DECIMAL(4,3) NULL,
    source            VARCHAR(30) NOT NULL DEFAULT 'explicit', -- 'explicit' | 'esco_essential' | 'esco_optional'
    PRIMARY KEY (job_id, skill_id),
    KEY idx_js_skill (skill_id),
    KEY idx_js_source (source),
    CONSTRAINT fk_js_job   FOREIGN KEY (job_id)   REFERENCES jobs (job_id) ON DELETE CASCADE,
    CONSTRAINT fk_js_skill FOREIGN KEY (skill_id) REFERENCES skills (skill_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================================
-- PHẦN 6. KHÓA HỌC CỦA NHÀ CUNG CẤP
-- =====================================================================

CREATE TABLE IF NOT EXISTS courses (
    course_id      INT UNSIGNED NOT NULL AUTO_INCREMENT,
    provider_id    INT UNSIGNED NOT NULL,
    course_name    VARCHAR(255) NOT NULL,
    description    TEXT NULL,
    course_url     VARCHAR(500) NULL,
    duration_hours SMALLINT UNSIGNED NULL,
    price_vnd      BIGINT UNSIGNED NULL,
    course_level   ENUM('beginner','intermediate','advanced') NULL,
    is_active      TINYINT(1) NOT NULL DEFAULT 1,
    created_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (course_id),
    KEY idx_course_provider (provider_id),
    CONSTRAINT fk_course_provider FOREIGN KEY (provider_id) REFERENCES course_providers (provider_id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Khóa học dạy những kỹ năng nào
CREATE TABLE IF NOT EXISTS course_skills (
    course_id INT UNSIGNED NOT NULL,
    skill_id  INT UNSIGNED NOT NULL,
    PRIMARY KEY (course_id, skill_id),
    KEY idx_cs_skill (skill_id),
    CONSTRAINT fk_cs_course FOREIGN KEY (course_id) REFERENCES courses (course_id) ON DELETE CASCADE,
    CONSTRAINT fk_cs_skill  FOREIGN KEY (skill_id)  REFERENCES skills (skill_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================================
-- PHẦN 7. LỊCH SỬ GỢI Ý (MODEL GỢI Ý NGHỀ + KỸ NĂNG CÒN THIẾU)
-- =====================================================================

CREATE TABLE IF NOT EXISTS worker_recommendations (
    recommendation_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    worker_id         INT UNSIGNED NOT NULL,
    position_id       INT UNSIGNED NOT NULL,
    match_score       DECIMAL(5,4) NOT NULL,
    rank_no           TINYINT UNSIGNED NOT NULL,
    created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (recommendation_id),
    KEY idx_wr_worker (worker_id),
    KEY idx_wr_position (position_id),
    CONSTRAINT fk_wr_worker   FOREIGN KEY (worker_id)   REFERENCES workers (worker_id) ON DELETE CASCADE,
    CONSTRAINT fk_wr_position FOREIGN KEY (position_id) REFERENCES positions (position_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Kỹ năng còn thiếu của worker so với nghề được gợi ý
CREATE TABLE IF NOT EXISTS worker_recommendation_skills (
    recommendation_id INT UNSIGNED NOT NULL,
    skill_id          INT UNSIGNED NOT NULL,
    priority_score    DECIMAL(6,2) NULL,              -- ví dụ lấy từ MSPS
    PRIMARY KEY (recommendation_id, skill_id),
    KEY idx_wrs_skill (skill_id),
    CONSTRAINT fk_wrs_rec   FOREIGN KEY (recommendation_id) REFERENCES worker_recommendations (recommendation_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_wrs_skill FOREIGN KEY (skill_id) REFERENCES skills (skill_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================================
-- PHẦN 8. DỮ LIỆU KHỞI TẠO
-- =====================================================================

INSERT IGNORE INTO industries (industry_code, industry_name_vi, industry_name_en) VALUES
    ('IT',         'Công nghệ Thông tin',                    'Information Technology'),
    ('TOURISM',    'Du lịch - Nhà hàng - Khách sạn',          'Tourism - Restaurant - Hotel'),
    ('LOGISTICS',  'Logistics - Kho vận - Chuỗi cung ứng',    'Logistics - Warehousing - Supply Chain'),
    ('ACCOUNTING', 'Kế toán - Kiểm toán - Tài chính - Thuế',  'Accounting - Auditing - Finance - Tax');

-- Mỗi ngành có sẵn 1 vị trí mặc định để tin chưa phân loại vẫn gắn được vào ngành.
-- Sau này thêm các vị trí cụ thể (Backend Developer, Kế toán tổng hợp...) vào bảng positions.
INSERT IGNORE INTO positions (industry_id, position_name)
SELECT industry_id, 'Chưa phân loại' FROM industries;

INSERT IGNORE INTO provinces (province_name) VALUES
    ('Đà Nẵng'), ('Quảng Nam'), ('Thừa Thiên Huế'), ('Quảng Ngãi');

INSERT IGNORE INTO education_levels (level_code, level_name_vi, level_rank) VALUES
    ('NONE',        'Không yêu cầu', 0),
    ('HIGH_SCHOOL', 'Trung học phổ thông', 1),
    ('VOCATIONAL',  'Trung cấp / Nghề', 2),
    ('COLLEGE',     'Cao đẳng', 3),
    ('BACHELOR',    'Đại học', 4),
    ('MASTER',      'Thạc sĩ', 5),
    ('DOCTORATE',   'Tiến sĩ', 6);

INSERT IGNORE INTO skill_types (type_code, type_name_vi) VALUES
    ('HARD',          'Kỹ năng chuyên môn'),
    ('SOFT',          'Kỹ năng mềm'),
    ('TOOL',          'Công cụ / Công nghệ'),
    ('KNOWLEDGE',     'Kiến thức'),
    ('CERTIFICATION', 'Chứng chỉ'),
    ('LANGUAGE',      'Ngoại ngữ');

-- Cây nhóm kỹ năng mẫu (nhóm lớn). Mở rộng thêm theo skillsHierarchy của ESCO nếu muốn.
INSERT IGNORE INTO skill_categories (parent_category_id, category_name) VALUES
    (NULL, 'Kỹ năng mềm'),
    (NULL, 'Kỹ năng chuyên môn'),
    (NULL, 'Công cụ & Công nghệ'),
    (NULL, 'Ngoại ngữ'),
    (NULL, 'Chứng chỉ');

-- Nhóm nhỏ mẫu của kỹ năng mềm
INSERT IGNORE INTO skill_categories (parent_category_id, category_name)
SELECT p.category_id, v.child_name
FROM skill_categories p
JOIN (
    SELECT 'Giao tiếp' AS child_name
    UNION ALL SELECT 'Tư duy & Giải quyết vấn đề'
    UNION ALL SELECT 'Làm việc nhóm & Lãnh đạo'
    UNION ALL SELECT 'Quản lý bản thân'
) v
WHERE p.category_name = 'Kỹ năng mềm';

-- =====================================================================
-- PHẦN 9. MIGRATE 1.000 TIN TỪ jobs_raw -> companies + jobs
-- Kiểm tra trước:
--   SELECT DISTINCT category FROM jobs_raw;
--   SELECT DISTINCT experience_required FROM jobs_raw;
-- Lương, địa điểm, kỹ năng: xử lý bằng Python rồi nạp vào
-- (salary_*_vnd, job_locations, job_skills).
-- =====================================================================

INSERT IGNORE INTO companies (company_name)
SELECT DISTINCT TRIM(company_name)
FROM jobs_raw
WHERE company_name IS NOT NULL AND TRIM(company_name) <> '';

INSERT INTO jobs
    (raw_job_id, title, company_id, position_id,
     experience_min_years, experience_max_years,
     description, requirements, posted_date, deadline)
SELECT
    r.job_id,
    TRIM(r.title),
    c.company_id,
    p.position_id,
    CASE
        WHEN r.experience_required LIKE '%Không yêu cầu%' OR r.experience_required LIKE '%Dưới%' THEN 0
        WHEN r.experience_required REGEXP '[0-9]'
            THEN CAST(REGEXP_SUBSTR(r.experience_required, '[0-9]+(\\.[0-9]+)?') AS DECIMAL(3,1))
        ELSE NULL
    END,
    CASE
        WHEN r.experience_required LIKE '%Dưới%' AND r.experience_required REGEXP '[0-9]'
            THEN CAST(REGEXP_SUBSTR(r.experience_required, '[0-9]+(\\.[0-9]+)?') AS DECIMAL(3,1))
        WHEN r.experience_required REGEXP '[0-9]+[^0-9]+[0-9]+'
            THEN CAST(REGEXP_SUBSTR(r.experience_required, '[0-9]+(\\.[0-9]+)?', 1, 2) AS DECIMAL(3,1))
        ELSE NULL
    END,
    r.description,
    r.requirements,
    r.posted_date,
    r.deadline
FROM jobs_raw r
JOIN companies c
    ON c.company_name = TRIM(r.company_name)
JOIN industries i
    ON i.industry_code = CASE
        WHEN r.category LIKE '%Công nghệ%'                             THEN 'IT'
        WHEN r.category LIKE '%Du lịch%'                                THEN 'TOURISM'
        WHEN r.category LIKE '%Logistics%' OR r.category LIKE '%Kho%'   THEN 'LOGISTICS'
        WHEN r.category LIKE '%Kế toán%'                                THEN 'ACCOUNTING'
    END
JOIN positions p
    ON p.industry_id = i.industry_id AND p.position_name = 'Chưa phân loại'
ON DUPLICATE KEY UPDATE
    title                = VALUES(title),
    company_id           = VALUES(company_id),
    experience_min_years = VALUES(experience_min_years),
    experience_max_years = VALUES(experience_max_years),
    description          = VALUES(description),
    requirements         = VALUES(requirements),
    posted_date          = VALUES(posted_date),
    deadline             = VALUES(deadline);

-- =====================================================================
-- PHẦN 10. VIEW TÍNH TOÁN THEO CÔNG THỨC TRONG SƠ ĐỒ
-- =====================================================================

-- 10.1 Toàn thị trường, theo từng kỹ năng
CREATE OR REPLACE VIEW v_skill_metrics_overall AS
SELECT
    m.skill_id, m.skill_name, m.skill_type_id, m.category_id,
    m.demand_jobs, m.supply_workers, m.total_jobs, m.total_workers,
    m.demand_pct, m.supply_pct, m.demand_share_pct,
    ROUND(m.demand_pct - m.supply_pct, 2) AS gap_pct,
    ROUND(CASE WHEN m.demand_pct > 0
               THEN (m.demand_pct - m.supply_pct) / m.demand_pct * 100 ELSE 0 END, 2) AS shortage_rate,
    ROUND(CASE WHEN m.demand_pct > 0
               THEN m.demand_share_pct * (m.demand_pct - m.supply_pct) / m.demand_pct ELSE 0 END, 2) AS msps
FROM (
    SELECT
        x.skill_id, x.skill_name, x.skill_type_id, x.category_id,
        x.demand_jobs, x.supply_workers,
        tj.total_jobs, tw.total_workers,
        COALESCE(ROUND(x.demand_jobs  * 100 / NULLIF(tj.total_jobs, 0), 2), 0)    AS demand_pct,
        COALESCE(ROUND(x.supply_workers * 100 / NULLIF(tw.total_workers, 0), 2), 0) AS supply_pct,
        COALESCE(ROUND(x.demand_jobs * 100 / NULLIF(SUM(x.demand_jobs) OVER (), 0), 2), 0) AS demand_share_pct
    FROM (
        SELECT s.skill_id, s.skill_name, s.skill_type_id, s.category_id,
               COALESCE(d.demand_jobs, 0)    AS demand_jobs,
               COALESCE(w.supply_workers, 0) AS supply_workers
        FROM skills s
        LEFT JOIN (
            SELECT js.skill_id, COUNT(*) AS demand_jobs
            FROM job_skills js
            JOIN jobs j ON j.job_id = js.job_id AND j.status <> 'hidden'
            GROUP BY js.skill_id
        ) d ON d.skill_id = s.skill_id
        LEFT JOIN (
            SELECT ws.skill_id, COUNT(*) AS supply_workers
            FROM worker_skills ws
            JOIN workers wk ON wk.worker_id = ws.worker_id AND wk.is_active = 1
            GROUP BY ws.skill_id
        ) w ON w.skill_id = s.skill_id
    ) x
    CROSS JOIN (SELECT COUNT(*) AS total_jobs FROM jobs WHERE status <> 'hidden') tj
    CROSS JOIN (SELECT COUNT(*) AS total_workers FROM workers WHERE is_active = 1) tw
) m
WHERE m.demand_jobs > 0 OR m.supply_workers > 0;

-- 10.2 Theo từng ngành (ngành của tin = positions.industry_id; ngành của worker = nghề mong muốn)
CREATE OR REPLACE VIEW v_skill_metrics_by_industry AS
SELECT
    m.industry_id, m.skill_id, m.skill_name, m.skill_type_id, m.category_id,
    m.demand_jobs, m.supply_workers, m.total_jobs, m.total_workers,
    m.demand_pct, m.supply_pct, m.demand_share_pct,
    ROUND(m.demand_pct - m.supply_pct, 2) AS gap_pct,
    ROUND(CASE WHEN m.demand_pct > 0
               THEN (m.demand_pct - m.supply_pct) / m.demand_pct * 100 ELSE 0 END, 2) AS shortage_rate,
    ROUND(CASE WHEN m.demand_pct > 0
               THEN m.demand_share_pct * (m.demand_pct - m.supply_pct) / m.demand_pct ELSE 0 END, 2) AS msps
FROM (
    SELECT
        x.industry_id, x.skill_id, x.skill_name, x.skill_type_id, x.category_id,
        x.demand_jobs, x.supply_workers,
        COALESCE(tj.total_jobs, 0)    AS total_jobs,
        COALESCE(tw.total_workers, 0) AS total_workers,
        COALESCE(ROUND(x.demand_jobs * 100 / NULLIF(tj.total_jobs, 0), 2), 0)      AS demand_pct,
        COALESCE(ROUND(x.supply_workers * 100 / NULLIF(tw.total_workers, 0), 2), 0) AS supply_pct,
        COALESCE(ROUND(x.demand_jobs * 100
                 / NULLIF(SUM(x.demand_jobs) OVER (PARTITION BY x.industry_id), 0), 2), 0) AS demand_share_pct
    FROM (
        SELECT i.industry_id, s.skill_id, s.skill_name, s.skill_type_id, s.category_id,
               COALESCE(d.demand_jobs, 0)    AS demand_jobs,
               COALESCE(w.supply_workers, 0) AS supply_workers
        FROM industries i
        CROSS JOIN skills s
        LEFT JOIN (
            SELECT p.industry_id, js.skill_id, COUNT(*) AS demand_jobs
            FROM job_skills js
            JOIN jobs j      ON j.job_id = js.job_id AND j.status <> 'hidden'
            JOIN positions p ON p.position_id = j.position_id
            GROUP BY p.industry_id, js.skill_id
        ) d ON d.industry_id = i.industry_id AND d.skill_id = s.skill_id
        LEFT JOIN (
            SELECT p.industry_id, ws.skill_id, COUNT(*) AS supply_workers
            FROM worker_skills ws
            JOIN workers wk  ON wk.worker_id = ws.worker_id AND wk.is_active = 1
            JOIN positions p ON p.position_id = wk.target_position_id
            GROUP BY p.industry_id, ws.skill_id
        ) w ON w.industry_id = i.industry_id AND w.skill_id = s.skill_id
    ) x
    LEFT JOIN (
        SELECT p.industry_id, COUNT(*) AS total_jobs
        FROM jobs j JOIN positions p ON p.position_id = j.position_id
        WHERE j.status <> 'hidden'
        GROUP BY p.industry_id
    ) tj ON tj.industry_id = x.industry_id
    LEFT JOIN (
        SELECT p.industry_id, COUNT(*) AS total_workers
        FROM workers wk JOIN positions p ON p.position_id = wk.target_position_id
        WHERE wk.is_active = 1
        GROUP BY p.industry_id
    ) tw ON tw.industry_id = x.industry_id
) m
WHERE m.demand_jobs > 0 OR m.supply_workers > 0;

-- 10.3 DASHBOARD TRANG ĐẦU: xếp hạng kỹ năng mềm toàn thị trường (3 bảng xếp hạng)
CREATE OR REPLACE VIEW v_rank_soft_skills_overall AS
SELECT
    m.*,
    ROW_NUMBER() OVER (ORDER BY m.demand_pct DESC, m.skill_name) AS rank_demand,
    ROW_NUMBER() OVER (ORDER BY m.supply_pct DESC, m.skill_name) AS rank_supply,
    ROW_NUMBER() OVER (ORDER BY m.msps DESC,       m.skill_name) AS rank_shortage
FROM v_skill_metrics_overall m
JOIN skill_types st ON st.skill_type_id = m.skill_type_id
WHERE st.type_code = 'SOFT';

-- 10.4 DASHBOARD THEO NGÀNH: xếp hạng mọi kỹ năng của từng ngành (lọc rank <= 10)
CREATE OR REPLACE VIEW v_rank_skills_by_industry AS
SELECT
    m.*,
    st.type_code,
    ROW_NUMBER() OVER (PARTITION BY m.industry_id ORDER BY m.demand_pct DESC, m.skill_name) AS rank_demand,
    ROW_NUMBER() OVER (PARTITION BY m.industry_id ORDER BY m.supply_pct DESC, m.skill_name) AS rank_supply,
    ROW_NUMBER() OVER (PARTITION BY m.industry_id ORDER BY m.msps DESC,       m.skill_name) AS rank_shortage
FROM v_skill_metrics_by_industry m
JOIN skill_types st ON st.skill_type_id = m.skill_type_id;

-- 10.5 Nhu cầu kỹ năng theo từng vị trí (dùng cho model gợi ý nghề + kỹ năng thiếu)
CREATE OR REPLACE VIEW v_position_skill_demand AS
SELECT
    j.position_id,
    js.skill_id,
    COUNT(*) AS demand_jobs,
    ROUND(COUNT(*) * 100 / pj.total_jobs, 2) AS demand_pct
FROM job_skills js
JOIN jobs j ON j.job_id = js.job_id AND j.status <> 'hidden'
JOIN (
    SELECT position_id, COUNT(*) AS total_jobs
    FROM jobs WHERE status <> 'hidden'
    GROUP BY position_id
) pj ON pj.position_id = j.position_id
GROUP BY j.position_id, js.skill_id, pj.total_jobs;
