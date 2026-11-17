"""Offline tests: actual SQLite models + real auth dependencies; all LLM calls mocked."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database import Base, get_db
from src.models.user import User
from src.models.job import JobPosting, JobApplication
from src.models.skill import ExtractedSkill
from src.models.evidence import ApplicationEvidence
from src.core.security import create_access_token
from src.routers.application_evidence import router
from src.services import evidence_matcher as m

CV = "CV mẫu 🚀: Dự án dùng Python\n  và SQL; triển khai dịch vụ API trong nhóm sinh viên Cần Thơ."


@pytest.fixture
def system(monkeypatch):
    monkeypatch.setenv("EVIDENCE_PROVIDER", "keyword")
    def no_llm(*args, **kwargs):
        raise AssertionError("LLM must be mocked; no network in tests")
    monkeypatch.setattr(m, "call_llm", no_llm)
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    @event.listens_for(engine, "connect")
    def foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine, expire_on_commit=False)()
    for uid, role in [(1, "employer"), (2, "employer"), (3, "worker"), (4, "course_provider"), (5, "admin"), (6, "provider")]:
        db.add(User(id=uid, email=f"user{uid}@demo.local", password_hash="unused", full_name=role, role=role))
    db.flush()
    db.add(JobPosting(id=1, employer_id=1, title="Backend", company="Demo", industry="IT"))
    db.flush()
    db.add(ExtractedSkill(job_id=1, skill_name="Python"))
    db.add(JobApplication(id=1, job_id=1, candidate_id=3, cv_snapshot_text=CV))
    db.commit()
    app = FastAPI()
    app.include_router(router, prefix="/api")
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as client:
        yield client, db
    db.close()
    engine.dispose()


def auth(uid):
    return {"Authorization": "Bearer " + create_access_token({"sub": str(uid)})}


def test_fake_quote_blocked():
    rows = m.validate_rows(CV, ["Python"], [{"requirement_name": "Python", "result": "supported", "quote": "Expert Python for 10 years"}])
    assert rows[0]["result"] == "needs_review"
    assert rows[0]["quote"] == "" and rows[0]["source_start"] is None
    assert rows[0]["ai_result_original"] == "supported"


def test_whitespace_offsets_original():
    result = m.validate_quote(CV, "Python và SQL")
    assert result["quote"] == "Python\n  và SQL"
    assert CV[result["source_start"]:result["source_end"]] == result["quote"]


def test_mask_contacts():
    result = m.mask_contacts("Email test@demo.local phone +84 901 234 567 hoặc 0901.234.567")
    assert "test@demo.local" not in result and "901" not in result
    assert "[EMAIL]" in result and result.count("[PHONE]") == 2


def test_java_not_javascript():
    rows = m.keyword_rows("Tôi làm JavaScript, dùng Docker và Python trong dự án.", ["Java", "JavaScript", "Docker"])
    assert [r["result"] for r in rows] == ["not_found", "supported", "supported"]


@pytest.mark.parametrize("cv", ["", "Python", "   \n "])
def test_unreadable_skips_llm(monkeypatch, cv):
    def fail(*_):
        pytest.fail("Unreadable CV must never call LLM")
    monkeypatch.setattr(m, "call_llm", fail)
    result = m.analyse(cv, ["Python"], "auto")
    assert result["status"] == "unreadable" and result["rows"][0]["result"] == "unreadable"


@pytest.mark.parametrize("uid,expected", [(None, 401), (2, 403), (3, 403), (4, 403), (6, 403), (1, 200), (5, 200)])
@pytest.mark.parametrize("operation", ["read", "create", "review"])
def test_permissions(system, uid, expected, operation):
    client, _ = system
    created = client.post("/api/applications/1/analyses", headers=auth(1)).json()
    evidence_id = created["evidence"][0]["id"]
    headers = auth(uid) if uid else {}
    if operation == "read":
        response = client.get("/api/applications/1/evidence", headers=headers)
    elif operation == "create":
        response = client.post("/api/applications/1/analyses", headers=headers)
    else:
        response = client.patch(f"/api/evidence/{evidence_id}/review", headers=headers, json={"review_result": "supported"})
    assert response.status_code == (201 if operation == "create" and expected == 200 else expected)


def test_cookie_auth(system):
    client, _ = system
    client.cookies.set("access_token", create_access_token({"sub": "1"}))
    assert client.get("/api/applications/1/evidence").status_code == 200


@pytest.mark.parametrize("uid,expected", [(None, 401), (2, 403), (3, 403), (4, 403), (6, 403), (1, 200), (5, 200)])
def test_original_cv_scoped_and_not_rebuilt_from_analysis(system, uid, expected):
    client, db = system
    application = db.get(JobApplication, 1)
    original = "CV GỐC\nDự án Python và SQL — nội dung chưa sửa.\n"
    application.cv_original_text = original
    application.cv_original_filename = "CV_tu_tao.txt"
    db.commit()
    client.post("/api/applications/1/analyses", headers=auth(1))
    application.cv_snapshot_text = "Bản trích xuất đã thay đổi, không được thay tệp gốc."
    db.commit()
    response = client.get("/api/applications/1/original-cv", headers=auth(uid) if uid else {})
    assert response.status_code == expected
    if expected == 200:
        assert response.json()["content"] == original
        assert response.json()["sha256"] == m.digest(original)
        assert response.json()["filename"] == "CV_tu_tao.txt"


def test_legacy_cv_has_no_fabricated_original(system):
    client, _ = system
    response = client.get("/api/applications/1/original-cv", headers=auth(1))
    assert response.status_code == 404
    assert client.get("/api/applications/999/original-cv", headers=auth(1)).status_code == 404


def test_review_preserves_original_and_requires_reason(system):
    client, db = system
    run = client.post("/api/applications/1/analyses", headers=auth(1)).json()
    row = run["evidence"][0]
    url = f'/api/evidence/{row["id"]}/review'
    assert client.patch(url, headers=auth(1), json={"review_result": "not_found", "review_reason": " "}).status_code == 422
    response = client.patch(url, headers=auth(1), json={"review_result": "not_found", "review_reason": "Dẫn chứng chưa thể hiện yêu cầu này"})
    assert response.status_code == 200
    saved = response.json()["evidence"][0]
    assert saved["ai_result_original"] == "supported" and saved["result"] == "supported"
    assert saved["review_result"] == "not_found" and saved["reviewer_id"] == 1 and saved["reviewed_at"]
    assert db.get(JobApplication, 1).status == "applied"


def test_stale_requirements(system):
    client, db = system
    run = client.post("/api/applications/1/analyses", headers=auth(1)).json()
    assert not run["stale"]
    db.add(ExtractedSkill(job_id=1, skill_name="Docker")); db.commit()
    assert client.get("/api/applications/1/evidence", headers=auth(1)).json()["stale"]
    response = client.patch(f'/api/evidence/{run["evidence"][0]["id"]}/review', headers=auth(1), json={"review_result": "supported"})
    assert response.status_code == 409
    assert not client.post("/api/applications/1/analyses", headers=auth(1)).json()["stale"]


def test_both_llms_fail_fallback_preserves_application(system, monkeypatch):
    client, db = system
    monkeypatch.setenv("EVIDENCE_PROVIDER", "auto")
    monkeypatch.setenv("GEMINI_API_KEY", "mock-not-a-real-key")
    monkeypatch.setenv("GROQ_API_KEY", "mock-not-a-real-key")
    called = []
    def fail(provider, prompt):
        called.append(provider)
        raise RuntimeError("Mock unavailable")
    monkeypatch.setattr(m, "call_llm", fail)
    data = client.post("/api/applications/1/analyses", headers=auth(1)).json()
    assert called == ["gemini", "groq"]
    assert data["provider"] == "keyword" and data["status"] == "error"
    assert data["error_code"] == "LLM_UNAVAILABLE_KEYWORD_FALLBACK"
    assert db.get(JobApplication, 1).cv_snapshot_text == CV


def test_provider_error_persisted_and_retry(system, monkeypatch):
    client, db = system
    monkeypatch.setenv("EVIDENCE_PROVIDER", "groq")
    data = client.post("/api/applications/1/analyses", headers=auth(1)).json()
    assert data["status"] == "error" and data["error_code"] == "LLM_UNAVAILABLE"
    assert db.get(JobApplication, 1) is not None
    assert client.get("/api/applications/1/evidence", headers=auth(1)).json()["status"] == "error"
    monkeypatch.setenv("EVIDENCE_PROVIDER", "keyword")
    assert client.post("/api/applications/1/analyses", headers=auth(1)).json()["status"] == "done"


def test_llm_receives_masked_text_and_quote_checked(system, monkeypatch):
    client, db = system
    application = db.get(JobApplication, 1)
    application.cv_snapshot_text += " Email: hidden@demo.local; phone: 0901 234 567."
    db.commit()
    monkeypatch.setenv("EVIDENCE_PROVIDER", "gemini")
    def mocked(provider, prompt):
        assert "hidden@demo.local" not in prompt and "0901" not in prompt
        return [{"requirement_name": "Python", "result": "supported", "quote": "Fabricated achievement"}]
    monkeypatch.setattr(m, "call_llm", mocked)
    row = client.post("/api/applications/1/analyses", headers=auth(1)).json()["evidence"][0]
    assert row["result"] == "needs_review" and row["quote"] == ""


def test_cv_change_stale_and_review_blocked(system):
    client, db = system
    data = client.post("/api/applications/1/analyses", headers=auth(1)).json()
    db.get(JobApplication, 1).cv_snapshot_text = CV + " Updated CV."
    db.commit()
    assert client.get("/api/applications/1/evidence", headers=auth(1)).json()["cv_stale"]
    assert client.patch(f'/api/evidence/{data["evidence"][0]["id"]}/review', headers=auth(1), json={"review_result": "supported"}).status_code == 409


def test_missing_and_duplicate_llm_rows_need_review():
    rows = m.validate_rows(CV, ["Python", "SQL"], [{"requirement_name": "SQL", "result": "not_found"}] * 2)
    assert all(r["result"] == "needs_review" and not r["quote"] for r in rows)


def test_all_providers_and_keyword_error_keeps_application(system, monkeypatch):
    client, db = system
    monkeypatch.setenv("EVIDENCE_PROVIDER", "auto")
    def fail(*_):
        raise RuntimeError("Mock failure")
    monkeypatch.setattr(m, "call_llm", fail)
    monkeypatch.setattr(m, "keyword_rows", fail)
    data = client.post("/api/applications/1/analyses", headers=auth(1)).json()
    assert data["status"] == "error"
    assert db.get(JobApplication, 1).status == "applied"


def test_auto_without_keys_is_keyword_not_error(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    def never(*_):
        pytest.fail("No keys: must not call a remote LLM")
    monkeypatch.setattr(m, "call_llm", never)
    result = m.analyse(CV, ["Python"], "auto")
    assert result["provider"] == "keyword" and result["status"] == "done"


def test_auto_groq_after_gemini_failure(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "mock-key")
    monkeypatch.setenv("GROQ_API_KEY", "mock-key")
    calls = []
    def mocked(provider, prompt):
        calls.append(provider)
        if provider == "gemini":
            raise RuntimeError("Mock Gemini failure")
        return [{"requirement_name": "Python", "result": "supported", "quote": "Python"}]
    monkeypatch.setattr(m, "call_llm", mocked)
    result = m.analyse(CV, ["Python"], "auto")
    assert calls == ["gemini", "groq"]
    assert result["provider"] == "groq" and result["status"] == "done"


@pytest.mark.parametrize("uid,code",[(None,401),(2,403),(3,403),(4,403),(6,403),(1,200),(5,200)])
@pytest.mark.parametrize("operation",["upload","file"])
def test_original_file_upload_and_download_permissions(system,uid,code,operation):
    client,db=system
    db.get(JobApplication,1).cv_original_text=CV;db.commit()
    headers=auth(uid) if uid else {}
    if operation=="upload":
        r=client.put("/api/applications/1/original-cv",headers=headers,files={"file":("CV.txt",CV.encode(),"text/plain")})
    else:r=client.get("/api/applications/1/original-cv/file",headers=headers)
    assert r.status_code==code


@pytest.mark.parametrize("extension",["pdf","png"])
def test_binary_cv_roundtrip_and_unreadable_is_not_success(system,monkeypatch,extension):
    import io,hashlib
    client,db=system
    if extension=="pdf":
        from pypdf import PdfWriter
        out=io.BytesIO();writer=PdfWriter();writer.add_blank_page(width=400,height=600);writer.write(out);content=out.getvalue()
    else:
        from PIL import Image
        import pytesseract
        monkeypatch.setattr(pytesseract,"image_to_string",lambda *args,**kwargs: "")
        out=io.BytesIO();Image.new("RGB",(40,60),"white").save(out,format="PNG");content=out.getvalue()
    r=client.put("/api/applications/1/original-cv",headers=auth(1),files={"file":(f"CV.{extension}",content,"application/octet-stream")})
    assert r.status_code==200 and r.json()["extraction_status"]=="unreadable"
    doc=client.get("/api/applications/1/original-cv",headers=auth(1)).json()
    assert doc["sha256"]==hashlib.sha256(content).hexdigest()
    assert client.get("/api"+doc["file_url"],headers=auth(1)).content==content
    analysed=client.post("/api/applications/1/analyses",headers=auth(1)).json()
    assert analysed["status"]=="unreadable"
    assert db.get(JobApplication,1).cv_original_blob==content


@pytest.mark.parametrize("filename,content,status",[("CV.txt",b"",422),("CV.png",b"not png",422),("CV.pdf",b"%PDF-invalid",422),("CV.html",b"<script>bad</script>",422),("CV.txt",b"x"*(5*1024*1024+1),413)])
def test_invalid_original_does_not_replace_previous_cv(system,filename,content,status):
    client,db=system
    application=db.get(JobApplication,1);application.cv_original_text=CV;db.commit()
    r=client.put("/api/applications/1/original-cv",headers=auth(1),files={"file":(filename,content,"application/octet-stream")})
    assert r.status_code==status
    db.expire_all()
    assert db.get(JobApplication,1).cv_original_text==CV
    assert db.get(JobApplication,1).cv_snapshot_text==CV
