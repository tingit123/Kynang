"""Add a small workflow trial to authored CVs; preserve any existing process edits."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent / "services" / "core-api-backend"))
from src.database import SessionLocal
from src.models.user import User
from src.models.job import JobPosting, JobApplication
from src.models.recruitment_process import ApplicationProcess, ApplicationProcessEvent


def seed():
    with SessionLocal() as db:
        owner = db.query(User).filter_by(email="evidence.employer@demo.local").one()
        job = db.query(JobPosting).filter_by(employer_id=owner.id, title="[CV tự tạo] Backend Developer").one()
        data = [("authored.cv1-1@demo.local", "interviewing"),
                ("authored.cv1-2@demo.local", "screening"),
                ("authored.cv1-3@demo.local", "offer"),
                ("authored.cv1-4@demo.local", "new")]
        count = 0
        for email, stage in data:
            candidate = db.query(User).filter_by(email=email).one()
            application = db.query(JobApplication).filter_by(job_id=job.id, candidate_id=candidate.id).one()
            if db.get(ApplicationProcess, application.id): continue
            db.add(ApplicationProcess(application_id=application.id, stage=stage, version=1))
            db.add(ApplicationProcessEvent(application_id=application.id, actor_id=owner.id, actor_name=owner.full_name or owner.email,
                event_type="demo_setup", details={"stage": {"from": "new", "to": stage}},
                reason="Khởi tạo bản thử tiến trình trên CV hư cấu; không phải hoạt động tuyển dụng thật."))
            count += 1
        db.commit()
        print(f"Added {count} workflow trials; kept existing edits.")


if __name__ == "__main__": seed()
