import pytest
from test_evidence import system, auth, CV
from src.models.job import JobApplication, JobPosting
from src.routers.jobs import router


@pytest.fixture
def applications(system):
    client, db = system
    client.app.include_router(router, prefix="/api/jobs")
    db.add(JobPosting(id=2, employer_id=1, title="Open QA", company="Demo", industry="IT"))
    db.commit()
    return client, db


def test_file_application_persists_exact_cv_and_prevents_duplicate(applications):
    client, db = applications
    content = CV.encode("utf-8")
    result = client.post("/api/jobs/2/apply-cv", headers=auth(3), files={"file":("CV.txt",content,"text/plain")})
    assert result.status_code == 201, result.text
    row = db.get(JobApplication, result.json()["application_id"])
    assert row.candidate_id == 3 and row.job_id == 2
    assert row.cv_snapshot_text == CV and row.cv_original_blob == content
    assert row.cv_original_filename == "CV.txt"
    assert client.post("/api/jobs/2/apply",headers=auth(3),json={"cv_snapshot_text":CV}).status_code == 400
    assert client.post("/api/jobs/2/apply-cv",headers=auth(3),files={"file":("CV.txt",content)}).status_code == 400
    mine = client.get("/api/jobs/my-applications",headers=auth(3)).json()
    assert {a["jobId"] for a in mine} == {1,2}
    assert all("cv_snapshot_text" not in a for a in mine)


@pytest.mark.parametrize("name,content,code",[("CV.txt",b"",422),("CV.pdf",b"fake pdf",422),("CV.exe",b"binary",422),("CV.txt",b"x"*(5*1024*1024+1),413)])
def test_invalid_file_does_not_create_application(applications,name,content,code):
    client,db=applications
    before=db.query(JobApplication).count()
    result=client.post("/api/jobs/2/apply-cv",headers=auth(3),files={"file":(name,content)})
    assert result.status_code == code
    assert db.query(JobApplication).count() == before


@pytest.mark.parametrize("uid,code",[(None,401),(1,403),(2,403),(4,403),(3,201)])
def test_file_submission_role_and_own_list(applications,uid,code):
    client,db=applications
    headers=auth(uid) if uid else {}
    result=client.post("/api/jobs/2/apply-cv",headers=headers,files={"file":("CV.txt",CV.encode("utf-8"))})
    assert result.status_code == code
    assert client.get("/api/jobs/my-applications",headers=headers).status_code == (200 if code==201 else code)


def test_text_submission_stores_original_and_closed_job_rejects(applications):
    client,db=applications
    result=client.post("/api/jobs/2/apply",headers=auth(3),json={"cv_snapshot_text":CV})
    assert result.status_code == 201
    row=db.get(JobApplication,result.json()["application_id"])
    assert row.cv_original_text == CV and row.cv_original_filename == "CV.txt"
    mine=client.get("/api/jobs/my-applications",headers=auth(3)).json()
    assert mine[0]["candidateEmail"] == "user3@demo.local"
    job=db.get(JobPosting,2);job.is_deleted=True;db.commit()
    assert client.post("/api/jobs/2/apply-cv",headers=auth(3),files={"file":("CV.txt",CV.encode())}).status_code == 404


def test_pdf_with_leading_whitespace_is_accepted_and_original_bytes_preserved(applications):
    import io
    from pypdf import PdfWriter
    from src.services.cv_original import validate_extract
    writer=PdfWriter(); writer.add_blank_page(width=595,height=842)
    stream=io.BytesIO();writer.write(stream)
    content=b"\n \t\r\n"+stream.getvalue()
    name,mime,text=validate_extract("CV.pdf",content)
    assert name=="CV.pdf" and mime=="application/pdf" and text==""
    client,db=applications
    response=client.post("/api/jobs/2/apply-cv",headers=auth(3),files={"file":("CV.pdf",content,"application/pdf")})
    assert response.status_code==201,response.text
    assert response.json()["extraction_status"]=="unreadable"
    saved=db.get(JobApplication,response.json()["application_id"])
    assert saved.cv_original_blob==content and saved.cv_original_mime=="application/pdf"


@pytest.mark.parametrize("prefix",[b"fake", b"<html>",b" "*1025])
def test_pdf_rejects_non_whitespace_or_excessive_prefix(applications,prefix):
    import io
    from pypdf import PdfWriter
    writer=PdfWriter();writer.add_blank_page(width=100,height=100)
    stream=io.BytesIO();writer.write(stream)
    client,db=applications
    before=db.query(JobApplication).count()
    result=client.post("/api/jobs/2/apply-cv",headers=auth(3),files={"file":("CV.pdf",prefix+stream.getvalue())})
    assert result.status_code==422
    assert db.query(JobApplication).count()==before
