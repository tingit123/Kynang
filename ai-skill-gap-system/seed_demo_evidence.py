"""Idempotent evidence demo only. Does not replace or delete existing project data."""
import os
import json
from pathlib import Path
import secrets
import sys
from datetime import date
from sqlalchemy import inspect

sys.path.insert(0, str(Path(__file__).parent / "services" / "core-api-backend"))
from src.database import Base, SessionLocal, engine
from src.core.security import get_password_hash
from src.models.user import User, Employer, Company, Worker
from src.models.job import JobPosting, JobApplication
from src.models.skill import ExtractedSkill
from src.models.evidence import AnalysisRun, ApplicationEvidence  # noqa
from src.models.quick_hire import FilterProfile, QuickHireBatch, ApplicationStatusEvent  # noqa
from src.services.evidence_matcher import digest

SKILLS = ["Python", "SQL", "FastAPI", "Docker", "Java", "Communication"]
CVS = [
    ("Bản rõ", "CV mẫu — Nguyễn An\nDự án sinh viên: xây dựng API bằng Python và FastAPI. Viết truy vấn SQL, đóng gói bằng Docker. Tôi dùng Java trong đồ án khác và luyện giao tiếp khi làm việc nhóm."),
    ("Thiếu thông tin", "CV mẫu — Trần Bình\nSinh viên mới tốt nghiệp tại Cần Thơ. Mong muốn tìm việc phát triển phần mềm. Thông tin về công nghệ và dự án chưa được cung cấp trong hồ sơ này."),
    ("Song ngữ", "DEMO CV — Lê Chi\nBuilt a REST service with Python and FastAPI. Used structured query language for reporting. Kinh nghiệm giao tiếp với nhóm trong dự án sinh viên. Deployed with Docker."),
    ("Quá ngắn", "CV mẫu. Python."),
    ("Tên gần giống", "CV mẫu — Phạm Dũng\nDự án giao diện dùng JavaScript và HTML. Đây là hồ sơ minh họa việc tránh nhầm tên công nghệ gần giống nhau; chỉ ghi các công nghệ được nêu trong văn bản."),
    ("Unicode và xuống dòng", "CV mẫu — Võ Hà 🚀\nDự án học tập dùng Python\n\nvà SQL.\nTôi thực hành FastAPI, Docker và Java.\nCommunication: trình bày kết quả cho nhóm.\nLiên hệ: cv6@demo.local; 0901 234 567."),
]


def seed():
    password = os.getenv("DEMO_PASSWORD") or secrets.token_urlsafe(16)
    hashed = get_password_hash(password)
    Base.metadata.create_all(engine)
    # Older installations store candidate rather than worker in the MySQL ENUM.
    role_type = next(c["type"] for c in inspect(engine).get_columns("users") if c["name"] == "role")
    candidate_role = "worker" if "worker" in getattr(role_type, "enums", ["worker"]) else "candidate"
    with SessionLocal() as db:
        email = "evidence.employer@demo.local"
        employer = db.query(User).filter_by(email=email).first()
        if not employer:
            employer = User(email=email, full_name="HR Demo đối chiếu", role="employer", password_hash=hashed,
                            company_name="SkillGap Evidence Demo", is_active=True, is_deleted=False)
            db.add(employer)
            db.flush()
        employer.password_hash = hashed
        employer.is_active = True
        employer.is_deleted = False
        company = db.query(Company).filter_by(employer_id=employer.id).first()
        if not company:
            company = Company(employer_id=employer.id, name="SkillGap Evidence Demo")
            db.add(company)
            db.flush()
        profile = db.query(Employer).filter_by(user_id=employer.id).first()
        if not profile:
            profile = Employer(user_id=employer.id, company_id=company.id, contact_name="HR Demo")
            db.add(profile)
        profile.is_verified = True
        job = db.query(JobPosting).filter_by(employer_id=employer.id, title="[DEMO] Backend — đối chiếu dẫn chứng").first()
        if not job:
            job = JobPosting(employer_id=employer.id, title="[DEMO] Backend — đối chiếu dẫn chứng", company=company.name,
                             industry="IT", description="Tin minh họa, không phải nhu cầu tuyển dụng thật.", source_platform="Demo", posted_date=date.today())
            db.add(job)
            db.flush()
        job.is_deleted = False
        job.posted_date = date.today()
        existing = {r.skill_name for r in db.query(ExtractedSkill).filter_by(job_id=job.id)}
        for skill in SKILLS:
            if skill not in existing:
                db.add(ExtractedSkill(job_id=job.id, skill_name=skill, skill_category="IT"))
        for index, (name, cv) in enumerate(CVS, 1):
            candidate = db.query(User).filter_by(email=f"evidence.cv{index}@demo.local").first()
            if not candidate:
                candidate = User(email=f"evidence.cv{index}@demo.local", full_name=f"Hồ sơ mẫu {index} — {name}",
                                 role=candidate_role, password_hash=hashed, is_active=True, is_deleted=False)
                db.add(candidate)
                db.flush()
                db.add(Worker(user_id=candidate.id, full_name=candidate.full_name))
            candidate.password_hash = hashed
            application = db.query(JobApplication).filter_by(job_id=job.id, candidate_id=candidate.id).first()
            if not application:
                db.add(JobApplication(job_id=job.id, candidate_id=candidate.id, cv_snapshot_text=cv, status="applied"))
        # Thirty additional illustrative CVs. No automatic evaluation or selection.
        coverage = [SKILLS[:n] for n in range(7)] + [None]
        for index in range(1, 31):
            email = f"quickhire.cv{index:02d}@demo.local"
            candidate = db.query(User).filter_by(email=email).first()
            if not candidate:
                candidate = User(email=email, full_name=f"Hồ sơ mẫu lọc {index:02d}", role=candidate_role,
                                 password_hash=hashed, is_active=True, is_deleted=False)
                db.add(candidate)
                db.flush()
                db.add(Worker(user_id=candidate.id, full_name=candidate.full_name))
            candidate.password_hash = hashed
            application = db.query(JobApplication).filter_by(job_id=job.id, candidate_id=candidate.id).first()
            skills = coverage[(index-1) % len(coverage)]
            cv = ("CV mẫu quá ngắn." if skills is None else
                  f"CV mẫu minh họa số {index:02d}. Dự án học tập ghi nhận các công cụ và nội dung: "
                  + ", ".join(skills) + ". Đây là dữ liệu tự sinh để thử bộ lọc, chưa xác minh năng lực thực tế.")
            if not application:
                db.add(JobApplication(job_id=job.id, candidate_id=candidate.id, cv_snapshot_text=cv, status="applied"))
            else:
                application.cv_snapshot_text = cv
        for tag in ("fail", "timeout"):
            email = f"notify-{tag}@{tag}.demo.local"
            candidate = db.query(User).filter_by(email=email).first()
            if not candidate:
                candidate = User(email=email, full_name=f"Hồ sơ mẫu thử lỗi {tag}", role=candidate_role,
                                 password_hash=hashed, is_active=True, is_deleted=False)
                db.add(candidate)
                db.flush()
                db.add(Worker(user_id=candidate.id, full_name=candidate.full_name))
            candidate.password_hash = hashed
            if not db.query(JobApplication).filter_by(job_id=job.id,candidate_id=candidate.id).first():
                db.add(JobApplication(job_id=job.id,candidate_id=candidate.id,status="applied",
                    cv_snapshot_text="CV mẫu để kiểm tra kết quả gửi thông báo. Dự án học tập sử dụng Python và SQL, có nội dung minh họa để đối chiếu."))
        if not db.query(FilterProfile).filter_by(job_id=job.id).first():
            data = {"name": "[DEMO] Bộ lọc kỹ năng", "items": [
                {"label": skill, "kind": "skill", "level": "must" if index == 0 else "nice"}
                for index, skill in enumerate(SKILLS)]}
            db.add(FilterProfile(job_id=job.id, owner_user_id=employer.id, name=data["name"],
                                 items=data["items"],
                                 profile_hash=digest(json.dumps(data, ensure_ascii=False, sort_keys=True))))
        db.commit()
        print(f"DEMO ONLY: {employer.email}\nPassword: {password}\nJob ID: {job.id}\n38 sample applications, 6 requirements; two optional simulation recipients.")
        print("Worker demo: evidence.cv1@demo.local (same demo password). Notification page: http://localhost:8080/#/notifications")
        print("Temporary demo marker: candidate email ends with @demo.local.")


if __name__ == "__main__":
    seed()
