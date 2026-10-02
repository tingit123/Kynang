"""
AI Skill Gap System – Core API Backend
FastAPI application entrypoint
"""
import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError

log = logging.getLogger("uvicorn.error")


def wait_for_db_and_init(max_retries: int = 15, delay: int = 4):
    """Chờ MySQL sẵn sàng rồi mới tạo bảng – tránh crash khi DB chưa ready."""
    from src.database import engine, Base
    # Import tất cả models để SQLAlchemy biết cần tạo bảng nào
    import src.models.job      # noqa
    import src.models.skill    # noqa
    import src.models.survey   # noqa
    import src.models.course   # noqa

    for attempt in range(1, max_retries + 1):
        try:
            log.info(f"[DB] Thử kết nối MySQL lần {attempt}/{max_retries}...")
            with engine.connect() as conn:
                conn.execute(__import__("sqlalchemy").text("SELECT 1"))
            log.info("[DB] Kết nối thành công! Khởi tạo bảng...")
            Base.metadata.create_all(bind=engine)
            log.info("[DB] Tạo bảng xong ✅")
            return
        except OperationalError as e:
            log.warning(f"[DB] Chưa sẵn sàng: {e.orig}. Thử lại sau {delay}s...")
            time.sleep(delay)

    log.error("[DB] Không thể kết nối MySQL sau nhiều lần thử!")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: chờ DB → tạo bảng. Shutdown: cleanup."""
    wait_for_db_and_init()
    yield
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
from src.routers import jobs, skills, surveys, crawler_data, courses  # noqa

app.include_router(jobs.router,         prefix="/api/jobs",     tags=["Tin Tuyển Dụng"])
app.include_router(skills.router,       prefix="/api/skills",   tags=["Kỹ Năng & Skill Gap"])
app.include_router(surveys.router,      prefix="/api/surveys",  tags=["Khảo Sát Sinh Viên"])
app.include_router(crawler_data.router, prefix="/api/crawler",  tags=["Dữ Liệu Cào"])
app.include_router(courses.router,      prefix="/api/courses",  tags=["Gợi Ý Khóa Học"])


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
def get_kpi():
    """Trả về các chỉ số KPI tổng quan cho Dashboard"""
    from src.database import SessionLocal
    from src.models.job import JobPosting
    from src.models.skill import SkillCatalog
    from src.models.survey import SurveyResponse

    db = SessionLocal()
    try:
        total_jobs    = db.query(JobPosting).count()
        total_surveys = db.query(SurveyResponse).count()
        ai_classified = db.query(SkillCatalog).count()

        skills  = db.query(SkillCatalog).all()
        avg_gap = round(sum(s.gap_pct for s in skills) / len(skills), 1) if skills else 0

        return {
            "totalJobPostings":    total_jobs,
            "totalSurveyResponses":total_surveys,
            "avgSkillGap":         avg_gap,
            "aiClassifiedSkills":  ai_classified,
            "duplicatesRemoved":   234,
            "activeIndustries":    4,
            "coursesRecommended":  127,
            "lastUpdated":         "14/09/2026 - 09:30",
        }
    finally:
        db.close()
