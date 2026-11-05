"""Item count, filtering and employer permissions; all LLM calls mocked."""
import pytest
from test_evidence import system, auth, CV
from src.models.user import User
from src.models.job import JobPosting, JobApplication
from src.models.evidence import ApplicationEvidence
from src.routers.quick_hire import router
from src.routers.notifications import router as notifications_router
from src.services.filter_counts import calculate, select_results

PROFILE={"name":"HR filter","items":[{"label":"Python","kind":"skill","level":"must"},{"label":"SQL","kind":"skill","level":"nice"}]}

@pytest.fixture
def quick(system):
    client,db=system
    client.app.include_router(router,prefix="/api")
    client.app.include_router(notifications_router,prefix="/api")
    db.add_all([User(id=7,email="seven@demo.local",password_hash="unused",full_name="Seven",role="worker"),User(id=8,email="eight@demo.local",password_hash="unused",full_name="Eight",role="worker")])
    db.add(JobPosting(id=2,employer_id=2,title="Other",company="Other",industry="IT"));db.flush()
    db.add_all([JobApplication(id=2,job_id=2,candidate_id=3,cv_snapshot_text=CV),JobApplication(id=3,job_id=1,candidate_id=7,cv_snapshot_text="CV minh họa sử dụng Python trong dự án học tập, chưa bổ sung nội dung khác."),JobApplication(id=4,job_id=1,candidate_id=8,cv_snapshot_text="CV minh họa về công việc hành chính và kinh nghiệm thực tập trong doanh nghiệp."),JobApplication(id=5,job_id=1,candidate_id=3,cv_snapshot_text="CV ngắn.")])
    db.commit()
    assert client.put("/api/jobs/1/filter-profile",headers=auth(1),json=PROFILE).status_code==200
    return client,db

def evaluate(client):
    r=client.post("/api/jobs/1/filter-profile/evaluate",headers=auth(1),json={});assert r.status_code==200,r.text
    return client.get("/api/jobs/1/filter-results",headers=auth(1)).json()

def test_count_hr_override_and_no_implicit_zero():
    result=calculate(PROFILE["items"],[{"requirement_name":"Python","result":"supported","review_result":"not_found"},{"requirement_name":"SQL","result":"not_found","review_result":"supported"}],"done")
    assert (result["x"],result["y"])==(1,2) and result["missing_must"]==["Python"]
    for state in [None,"error","unreadable"]:
        assert calculate(PROFILE["items"],[],state)["x"] is None
    assert calculate([],[],"done")["x"] is None

def test_counts_chips_and_filters(quick):
    client,_=quick;data=evaluate(client)
    assert data["y"]==2 and data["counts_by_x"]=={"0":1,"1":1,"2":1}
    assert data["unassessed_count"]==1 and data["missing_must_count"]==1
    assert [a["x"] for a in data["applications"]]==[2,1,0]
    r=client.get("/api/jobs/1/filter-results?xs=1&xs=2",headers=auth(1)).json();assert r["total"]==2
    r=client.get("/api/jobs/1/filter-results?min_x=1",headers=auth(1)).json();assert r["total"]==2
    r=client.get("/api/jobs/1/filter-results?missing_must=true",headers=auth(1)).json();assert r["applications"][0]["x"]==0
    r=client.get("/api/jobs/1/filter-results?unassessed=true",headers=auth(1)).json();assert r["applications"][0]["x"] is None
    assert client.get("/api/jobs/1/filter-results?xs=3",headers=auth(1)).status_code==422

def test_fixed_page_size_and_all_matching_ids(quick):
    client,db=quick
    for i in range(10,24):db.add(JobApplication(id=i,job_id=1,candidate_id=3,cv_snapshot_text=CV))
    db.commit();evaluate(client)
    data=client.get("/api/jobs/1/filter-results",headers=auth(1)).json()
    assert len(data["applications"])==10 and data["total"]==17 and len(data["matching_ids"])==17
    assert len(client.get("/api/jobs/1/filter-results?page=2",headers=auth(1)).json()["applications"])==7

@pytest.mark.parametrize("uid,status",[(None,401),(2,403),(3,403),(4,403),(6,403),(1,200),(5,200)])
@pytest.mark.parametrize("operation",["profile","save","evaluate","results"])
def test_filter_permissions(quick,uid,status,operation):
    client,_=quick;headers=auth(uid) if uid else {}
    if operation=="profile":r=client.get("/api/jobs/1/filter-profile",headers=headers)
    elif operation=="save":r=client.put("/api/jobs/1/filter-profile",headers=headers,json=PROFILE)
    elif operation=="evaluate":r=client.post("/api/jobs/1/filter-profile/evaluate",headers=headers,json={})
    else:r=client.get("/api/jobs/1/filter-results",headers=headers)
    assert r.status_code==status,r.text

def test_changed_profile_resets_assessment(quick):
    client,_=quick;evaluate(client)
    client.put("/api/jobs/1/filter-profile",headers=auth(1),json={**PROFILE,"name":"New name"})
    data=client.get("/api/jobs/1/filter-results?unassessed=true",headers=auth(1)).json()
    assert data["total"]==4 and all(r["x"] is None for r in data["applications"])

def test_retired_selection_endpoint(quick):
    client,_=quick
    assert client.post("/api/jobs/1/quick-hire",headers=auth(1),json={}).status_code==404


@pytest.mark.parametrize("uid,status",[(None,401),(2,403),(3,403),(4,403),(1,200),(5,200)])
def test_apply_filter_requires_explicit_request_and_ownership(quick,uid,status):
    client,db=quick
    payload={"name":"Tiêu chí tuyển dụng hiện tại","items":[{"label":"SQL"}]}
    response=client.post("/api/jobs/1/filter-profile/apply",headers=auth(uid) if uid else {},json=payload)
    assert response.status_code==status
    if status==200:
        assert response.json()["items"]==[{"label":"SQL","kind":"skill","level":"nice"}]
        # Applying criteria alone never sends, selects or evaluates applications.
        assert db.query(ApplicationEvidence).count()==0
        assert db.get(JobApplication,1).status=="applied"


def test_priority_skills_rank_within_minimum_and_obey_hr_override(quick):
    client,db=quick
    evaluate(client)
    # SQL-only evidence for app 1; app 3 has Python and must be ranked first.
    row=db.query(ApplicationEvidence).filter_by(requirement_name="Python").first()
    row.review_result="not_found";db.commit()
    data=client.get("/api/jobs/1/filter-results?min_x=1&priority_skills=Python",headers=auth(1)).json()
    assert [a["application_id"] for a in data["applications"]]==[3,1]
    assert data["total"]==2
    assert next(v for v in data["applications"][1]["skill_states"] if v["label"]=="Python")["result"]=="not_found"
    assert client.get("/api/jobs/1/filter-results?min_x=2&priority_skills=Python",headers=auth(1)).json()["total"]==0
    assert client.get("/api/jobs/1/filter-results?priority_skills=NotInProfile",headers=auth(1)).status_code==422


def test_priority_sort_across_pages_and_unknown_skill_labels(quick):
    client,db=quick
    for i in range(10,24):db.add(JobApplication(id=i,job_id=1,candidate_id=3,cv_snapshot_text=CV))
    db.commit();evaluate(client)
    # Prefer SQL, and make one later application Python-only via HR review.
    from src.models.evidence import AnalysisRun
    run=db.query(AnalysisRun).filter_by(application_id=10).one()
    row=db.query(ApplicationEvidence).filter_by(run_id=run.id,requirement_name="SQL").one();row.review_result="not_found";db.commit()
    first=client.get("/api/jobs/1/filter-results?min_x=1&priority_skills=SQL&page=1",headers=auth(1)).json()
    second=client.get("/api/jobs/1/filter-results?min_x=1&priority_skills=SQL&page=2",headers=auth(1)).json()
    assert len(first["applications"])==10
    assert len(first["matching_ids"])==16 and first["matching_ids"]==second["matching_ids"]
    assert first["matching_ids"].index(10)>=14
    unknown=client.get("/api/jobs/1/filter-results?unassessed=true&priority_skills=Python",headers=auth(1)).json()["applications"][0]
    assert unknown["x"] is None
    assert all(v["result"] in {"unreadable","unassessed"} for v in unknown["skill_states"])
