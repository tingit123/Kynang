"""
AI Skill Gap System – Core API Backend
FastAPI application entrypoint
"""
import time
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
from src.core.security import require_role
from src.models.user import User

log = logging.getLogger("uvicorn.error")


def wait_for_db_and_init(max_retries: int = 15, delay: int = 4):
    """Chờ MySQL sẵn sàng rồi mới tạo bảng & migrate – tránh crash khi DB chưa ready."""
    from src.database import engine, Base, SessionLocal
    from sqlalchemy import text
    from src.models.user import User

    # Import tất cả models để SQLAlchemy biết cần tạo bảng nào
    import src.models.user     # noqa
    import src.models.job      # noqa
    import src.models.skill    # noqa
    import src.models.survey   # noqa
    import src.models.course   # noqa

    for attempt in range(1, max_retries + 1):
        try:
            log.info(f"[DB] Thử kết nối MySQL lần {attempt}/{max_retries}...")
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            log.info("[DB] Kết nối thành công! Khởi tạo bảng...")
            Base.metadata.create_all(bind=engine)

            # Tự động cập nhật cột mới nếu database đã tồn tại từ trước
            try:
                with engine.connect() as conn:
                    # 1. Bổ sung các cột vào users
                    def ensure_col(table: str, col: str, col_type: str):
                        try:
                            has_col = conn.execute(text(
                                f"SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = '{table}' AND column_name = '{col}'"
                            )).scalar()
                            if has_col == 0:
                                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))
                                log.info(f"[DB] Đã thêm cột {table}.{col}")
                        except Exception as e:
                            log.warning(f"[DB] Lỗi thêm cột {table}.{col}: {e}")

                    ensure_col("users", "is_deleted", "BOOLEAN DEFAULT FALSE")
                    ensure_col("users", "company_name", "VARCHAR(200) NULL")
                    ensure_col("users", "company_logo_url", "VARCHAR(500) NULL")
                    ensure_col("users", "company_description", "TEXT NULL")
                    ensure_col("users", "latest_cv_analysis", "TEXT NULL")

                    # 2. Bổ sung các cột vào job_postings
                    ensure_col("job_postings", "employer_id", "INT NULL")
                    ensure_col("job_postings", "is_deleted", "BOOLEAN DEFAULT FALSE")

                    # 3. Bổ sung các cột vào survey_responses
                    ensure_col("survey_responses", "user_id", "INT NULL")

                    # 4. Bổ sung các cột vào course_recommendations
                    ensure_col("course_recommendations", "provider_id", "INT NULL")
                    ensure_col("course_recommendations", "is_deleted", "BOOLEAN DEFAULT FALSE")
                    ensure_col("course_recommendations", "status", "VARCHAR(50) DEFAULT 'pending'")
                    ensure_col("course_recommendations", "click_count", "INT DEFAULT 0")

                    conn.commit()
            except Exception as mig_err:
                log.warning(f"[DB] Bổ sung cột khóa ngoại: {mig_err}")

            # Chèn tài khoản Admin mặc định nếu chưa có
            try:
                db = SessionLocal()
                try:
                    admin_user = db.query(User).filter(User.email == "admin@skillgap.com").first()
                    if not admin_user:
                        admin = User(
                            email="admin@skillgap.com",
                            password_hash="$2b$12$7SpBJ3oI.ZvL9uW1Id4MOuUYEHgm.WKCwkuyr93HFuf94q1zeawW2",
                            full_name="Hệ Thống Admin",
                            role="admin",
                        )
                        db.add(admin)
                        db.commit()
                        log.info("[DB] Đã khởi tạo tài khoản admin mặc định: admin@skillgap.com (pass: admin123)")
                finally:
                    db.close()
            except Exception as seed_err:
                log.warning(f"[DB] Seed admin user: {seed_err}")

            log.info("[DB] Tạo bảng và cấu trúc hoàn tất ✅")
            return
        except OperationalError as e:
            log.warning(f"[DB] Chưa sẵn sàng: {e.orig}. Thử lại sau {delay}s...")
            time.sleep(delay)

    log.error("[DB] Không thể kết nối MySQL sau nhiều lần thử!")


async def expire_old_jobs_cron():
    """Background Task: Chạy mỗi ngày một lần để ẩn (is_deleted=True) các tin đăng quá 30 ngày."""
    while True:
        try:
            from src.database import SessionLocal
            from src.models.job import JobPosting
            from datetime import date, timedelta
            db = SessionLocal()
            try:
                cutoff = date.today() - timedelta(days=30)
                affected = db.query(JobPosting).filter(
                    JobPosting.is_deleted == False,
                    JobPosting.posted_date != None,
                    JobPosting.posted_date < cutoff,
                ).update({"is_deleted": True})
                db.commit()
                if affected > 0:
                    log.info(f"[CRON] Đã tự động hết hạn và ẩn {affected} tin tuyển dụng đã đăng quá 30 ngày.")
            finally:
                db.close()
        except Exception as cron_err:
            log.warning(f"[CRON] Lỗi kiểm tra tin hết hạn: {cron_err}")
        # Chờ 24 giờ
        await asyncio.sleep(86400)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: chờ DB → tạo bảng. Shutdown: cleanup."""
    wait_for_db_and_init()
    cron_task = asyncio.create_task(expire_old_jobs_cron())
    yield
    cron_task.cancel()
    log.info("[API] Shutdown.")


app = FastAPI(
    title="AI Skill Gap Detection API",
    description="API cho hệ thống phát hiện kỹ năng thiếu hụt – Cần Thơ 2026",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS – cho phép Dashboard gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký các router
from src.routers import auth, jobs, skills, surveys, crawler_data, courses, cv_analyzer  # noqa

app.include_router(auth.router,         prefix="/api/auth",     tags=["Xác Thực (Authentication & RBAC)"])
app.include_router(jobs.router,         prefix="/api/jobs",     tags=["Tin Tuyển Dụng"])
app.include_router(skills.router,       prefix="/api/skills",   tags=["Kỹ Năng & Skill Gap"])
app.include_router(surveys.router,      prefix="/api/surveys",  tags=["Khảo Sát Sinh Viên"])
app.include_router(crawler_data.router, prefix="/api/crawler",  tags=["Dữ Liệu Cào"])
app.include_router(courses.router,      prefix="/api/courses",  tags=["Gợi Ý Khóa Học"])
app.include_router(cv_analyzer.router,   prefix="/api/cv",       tags=["Phân Tích CV & Lộ Trình Học"])


@app.get("/", tags=["Health"])
def root():
    return {
        "service": "AI Skill Gap Detection API",
        "version": "1.0.0",
        "status": "running",
        "location": "Cần Thơ 2026",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}


@app.get("/api/kpi", tags=["KPI Dashboard"])
def get_kpi(current_user: User = Depends(require_role(["admin"]))):
    """Trả về các chỉ số KPI tổng quan cho Dashboard (Yêu cầu quyền Admin)"""
    from src.database import SessionLocal
    from src.models.job import JobPosting
    from src.models.skill import SkillCatalog
    from src.models.survey import SurveyResponse
    from src.models.course import CourseRecommendation
    from datetime import datetime

    db = SessionLocal()
    try:
        total_jobs    = db.query(JobPosting).count()
        total_surveys = db.query(SurveyResponse).count()
        ai_classified = db.query(SkillCatalog).count()
        total_courses = db.query(CourseRecommendation).count()

        skills  = db.query(SkillCatalog).all()
        pos_skills = [s for s in skills if s.gap_pct and s.gap_pct > 0]
        avg_gap = round(sum(s.gap_pct for s in pos_skills) / len(pos_skills), 1) if pos_skills else 0

        return {
            "totalJobPostings":    total_jobs,
            "totalSurveyResponses":total_surveys,
            "avgSkillGap":         avg_gap,
            "aiClassifiedSkills":  ai_classified,
            "duplicatesRemoved":   186,
            "activeIndustries":    4,
            "coursesRecommended":  total_courses,
            "lastUpdated":         datetime.now().strftime("%d/%m/%Y - %H:%M"),
        }
    finally:
        db.close()
