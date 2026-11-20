from test_evidence import system, auth
from src.routers.auth import router as auth_router
from src.routers.jobs import router as jobs_router
from src.models.user import User
from src.models.job import JobPosting, JobApplication
from src.scripts.clean_employer_demo import clean_demo


def test_demo_endpoint_removed(system, monkeypatch):
    client, _ = system
    monkeypatch.setenv("DEMO_EMPLOYER_LOGIN", "1")
    client.app.include_router(auth_router, prefix="/api/auth")
    assert client.post("/api/auth/demo/employer").status_code == 404


def test_my_jobs_count_and_tenant_isolation(system):
    client, _ = system
    client.app.include_router(jobs_router, prefix="/api/jobs")
    assert client.get("/api/jobs/my-jobs").status_code == 401
    assert client.get("/api/jobs/my-jobs", headers=auth(2)).json() == []
    own = client.get("/api/jobs/my-jobs", headers=auth(1)).json()
    assert len(own) == 1 and own[0]["applications_count"] == 1
    assert client.get("/api/jobs/1/applications", headers=auth(2)).status_code == 403


def test_post_edit_require_auth_and_owned_job(system):
    client, db = system
    client.app.include_router(jobs_router, prefix="/api/jobs")
    data = {"title": "New title", "company": "Company", "industry": "IT", "skills": ["SQL"]}
    assert client.post("/api/jobs/", json=data).status_code == 401
    assert client.post("/api/jobs/", json=data, headers=auth(3)).status_code == 403
    assert client.put("/api/jobs/1", json=data, headers=auth(2)).status_code == 403
    assert client.put("/api/jobs/1", json=data, headers=auth(1)).status_code == 200
    db.expire_all()
    assert db.get(JobPosting, 1).title == "New title"
    assert db.get(JobPosting, 1).employer_id == 1


def test_profile_update_persists_and_cannot_change_role(system):
    client, db = system
    client.app.include_router(auth_router, prefix="/api/auth")
    data = {"full_name": "HR", "company_name": "Company", "role": "admin"}
    assert client.put("/api/auth/profile", json=data).status_code == 401
    assert client.put("/api/auth/profile", json=data, headers=auth(1)).status_code == 200
    db.expire_all()
    assert db.get(User, 1).company_name == "Company"
    assert db.get(User, 1).role == "employer"
    restored = client.get("/api/auth/me", headers=auth(1))
    assert restored.status_code == 200
    assert restored.json()["company_name"] == "Company"


def test_cleanup_dry_run_preserves_other_tenant_and_candidate(system):
    _, db = system
    db.get(User, 1).email = "evidence.employer@demo.local"
    db.add(JobPosting(id=2, employer_id=2, title="Real job", company="Real", industry="IT"))
    db.commit()
    with db.bind.begin() as conn:
        counts = clean_demo(conn)
        assert counts["job_postings"] == 1 and counts["job_applications"] == 1
    db.expire_all()
    assert db.get(JobPosting, 1) is not None
    with db.bind.begin() as conn:
        clean_demo(conn, apply=True)
    db.expire_all()
    assert db.get(JobPosting, 1) is None
    assert db.get(JobApplication, 1) is None
    assert db.get(JobPosting, 2) is not None
    assert db.get(User, 3) is not None
