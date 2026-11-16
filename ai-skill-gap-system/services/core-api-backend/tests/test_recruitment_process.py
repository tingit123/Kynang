import pytest
from test_evidence import system, auth, CV
from src.models.user import User
from src.models.job import JobPosting, JobApplication
from src.models.recruitment_process import RecruiterContact, ApplicationProcess, ApplicationProcessEvent
from src.models.notification import UserNotification
from src.routers.recruitment_process import router


@pytest.fixture
def workflow(system):
    client, db = system
    client.app.include_router(router, prefix="/api")
    db.add_all([RecruiterContact(id=1, owner_id=1, name="HR One", email="one@demo.local"),
                RecruiterContact(id=2, owner_id=2, name="Other HR", email="other@demo.local")])
    db.add(JobPosting(id=2, employer_id=2, title="Private", company="Other", industry="IT"))
    db.flush()
    db.add_all([JobApplication(id=2, job_id=2, candidate_id=3, cv_snapshot_text=CV),
                JobApplication(id=3, job_id=1, candidate_id=3, cv_snapshot_text=CV)])
    db.commit()
    return client, db


def read(client, uid=1):
    return client.get("/api/applications/1/process", headers=auth(uid)).json()


def update(client, **changes):
    payload={"expected_version":0,"stage":"screening","reason":"Đã kiểm tra nội dung CV",**changes}
    return client.patch("/api/applications/1/process", headers=auth(1), json=payload)


@pytest.mark.parametrize("uid,code", [(None,401),(2,403),(3,403),(4,403),(6,403),(1,200),(5,200)])
@pytest.mark.parametrize("operation", ["list","read","update","note"])
def test_workflow_permissions(workflow, uid, code, operation):
    client, _=workflow;headers=auth(uid) if uid else {}
    if operation=="list":r=client.get("/api/jobs/1/pipeline", headers=headers)
    elif operation=="read":r=client.get("/api/applications/1/process", headers=headers)
    elif operation=="update":r=client.patch("/api/applications/1/process",headers=headers,json={"expected_version":0,"stage":"screening","reason":"Đã xem xét hồ sơ"})
    elif operation=="contact":r=client.post("/api/jobs/1/recruitment-assignees",headers=headers,json={"name":"HR New","email":"new@demo.local"})
    else:r=client.post("/api/applications/1/process/notes",headers=headers,json={"note":"Ghi chú nội bộ"})
    assert r.status_code==(201 if code==200 and operation in {"contact","note"} else code),r.text


def test_pipeline_defaults_and_communication_are_independent(workflow):
    client, db=workflow
    db.get(JobApplication,1).status="invited";db.commit()
    data=client.get("/api/jobs/1/pipeline",headers=auth(1)).json()
    assert data["counts"]["new"]==2
    assert data["managed_by"]=={"id":1}
    assert "assignees" not in data
    assert db.query(ApplicationProcess).count()==0  # GET must not write.
    assert read(client)["version"]==0
    assert {a["id"] for a in data["applications"]}=={1,3}
    assert "cv_snapshot_text" not in data["applications"][0]


def test_stage_assignment_and_audit_are_atomic_and_survive_reload(workflow):
    client,db=workflow
    data=update(client).json()
    assert (data["stage"],data["version"])==("screening",1)
    event=data["events"][0]
    assert event["actor_id"]==1 and event["actor_name"]=="employer"
    assert event["details"]["stage"]=={"from":"new","to":"screening"}
    assert "assignee" not in event["details"]
    assert read(client)["events"]==data["events"]
    db.get(User,1).full_name="New name";db.commit()
    assert read(client)["events"][0]["actor_name"]=="employer"
    assert db.get(JobApplication,1).cv_snapshot_text==CV
    assert db.get(JobApplication,1).status=="applied"
    assert db.query(UserNotification).count()==0


def test_stale_version_and_unchanged_save_do_not_add_audit(workflow):
    client,db=workflow
    assert update(client).status_code==200
    assert update(client,stage="offer").status_code==409
    assert update(client,expected_version=1).status_code==422
    assert read(client)["stage"]=="screening"
    assert db.query(ApplicationProcessEvent).count()==1


def test_assignment_cannot_cross_employer_boundary(workflow):
    client,db=workflow
    assert update(client,assignee_id=2).status_code==422
    assert db.query(ApplicationProcessEvent).count()==db.query(ApplicationProcess).count()==0


def test_all_rounds_backtracking_have_history(workflow):
    client,db=workflow
    for version,stage in enumerate(["screening","interviewing","offer","hired","rejected","new"]):
        assert update(client,stage=stage,expected_version=version).status_code==200
    assert read(client)["event_count"]==6
    assert db.get(JobApplication,1).status=="applied"


def test_legacy_interview_rounds_share_one_stage_and_keep_audit(workflow):
    client, db = workflow
    db.add_all([
        ApplicationProcess(application_id=1, stage="interview_1", version=2),
        ApplicationProcess(application_id=3, stage="interview_2", version=4),
        ApplicationProcessEvent(
            application_id=1, actor_id=1, actor_name="HR One",
            event_type="process_updated", reason="Lịch sử trước khi gộp",
            details={"stage": {"from": "screening", "to": "interview_1"}},
        ),
    ])
    db.commit()

    data = client.get("/api/jobs/1/pipeline", headers=auth(1)).json()
    assert data["counts"]["interviewing"] == 2
    assert len(data["stages"]) == 6
    assert {row["stage"] for row in data["applications"]} == {"interviewing"}
    assert read(client)["stage"] == "interviewing"
    assert update(client, stage="interviewing", expected_version=2).status_code == 422

    changed = update(client, stage="offer", expected_version=2)
    assert changed.status_code == 200
    events = changed.json()["events"]
    assert events[0]["details"]["stage"]["to"] == "interview_1"
    assert events[1]["details"]["stage"]["to"] == "offer"
    assert db.get(ApplicationProcess, 1).stage == "offer"


@pytest.mark.parametrize("changes", [{"stage":"not-a-stage"},{"reason":"   "},{"reason":"abcd"},{"actor_id":5},{"expected_version":-1}])
def test_invalid_process_change_is_rejected_without_write(workflow,changes):
    client,db=workflow
    assert update(client,**changes).status_code==422
    assert db.query(ApplicationProcessEvent).count()==0


def test_notes_are_append_only_and_not_visible_to_candidate(workflow):
    client,db=workflow
    assert update(client).status_code==200
    r=client.post("/api/applications/1/process/notes",headers=auth(1),json={"note":"Cần xác nhận thời gian có thể nhận việc."})
    assert r.status_code==201
    assert r.json()["version"]==1 and r.json()["event_count"]==2
    assert r.json()["events"][-1]["event_type"]=="note"
    assert client.get("/api/applications/1/process",headers=auth(3)).status_code==403
    assert client.delete("/api/applications/1/process",headers=auth(1)).status_code==405
    assert client.post("/api/applications/1/process/notes",headers=auth(1),json={"note":"  "}).status_code==422


def test_multiple_hr_management_removed(workflow):
    client,db=workflow
    assert client.post("/api/jobs/1/recruitment-assignees",headers=auth(1),json={"name":"HR"}).status_code==404
    assert update(client,assignee_id=1).status_code==422
    assert "assignee_id" not in read(client)
    assert db.query(ApplicationProcess).count()==0


def test_missing_application_and_job(workflow):
    client,_=workflow
    assert client.get("/api/jobs/999/pipeline",headers=auth(1)).status_code==404
    assert client.get("/api/applications/999/process",headers=auth(1)).status_code==404


def test_pipeline_skills_use_saved_job_evidence_and_hr_review(workflow):
    from src.models.evidence import ApplicationEvidence
    client, db = workflow
    before = client.get("/api/jobs/1/pipeline", headers=auth(1)).json()
    assert all(a["skill_states"] == [{"label":"Python","result":"unassessed"}] for a in before["applications"])
    run = client.post("/api/applications/1/analyses", headers=auth(1)).json()
    data = client.get("/api/jobs/1/pipeline", headers=auth(1)).json()
    a = next(a for a in data["applications"] if a["id"] == 1)
    assert a["skills_assessed"] and a["skill_states"] == [{"label":"Python","result":"supported"}]
    evidence = db.get(ApplicationEvidence, run["evidence"][0]["id"])
    evidence.review_result = "not_found"; db.commit()
    data = client.get("/api/jobs/1/pipeline", headers=auth(1)).json()
    assert next(a for a in data["applications"] if a["id"]==1)["skill_states"][0]["result"]=="not_found"
    db.get(JobApplication,1).cv_snapshot_text="CV mới chưa được đối chiếu.";db.commit()
    data = client.get("/api/jobs/1/pipeline", headers=auth(1)).json()
    assert next(a for a in data["applications"] if a["id"]==1)["skill_states"][0]["result"]=="unassessed"


def test_pipeline_uses_its_own_priorities_without_changing_quick_filter(workflow):
    from src.models.quick_hire import FilterProfile
    from src.models.evidence import AnalysisRun
    from src.routers.application_evidence import persist_analysis
    client,db=workflow
    profile = FilterProfile(job_id=1, owner_user_id=1, name="Active",
                            items=[{"label": "SQL", "kind": "skill", "level": "nice"}],
                            profile_hash="a" * 64)
    db.add(profile)
    db.flush()
    persist_analysis(db, db.get(JobApplication, 1), ["SQL"], profile.profile_hash)
    db.get(JobApplication, 1).cv_snapshot_text = "Đã sử dụng Apache Airflow để điều phối dữ liệu của nhóm."
    db.get(JobApplication, 3).cv_snapshot_text = "CV ngắn."
    db.commit()
    before = db.query(AnalysisRun).count()
    path = "/api/jobs/1/pipeline"
    baseline = client.get(path, headers=auth(1)).json()
    assert baseline["applications"][0]["skill_states"] == [{"label": "Python", "result": "unassessed"}]
    selected = [("priority_skills", label) for label in ("Apache Airflow", " apache  airflow ", "Docker")]
    response = client.get(path, headers=auth(1), params=selected)
    assert response.status_code == 200
    by_id = {row["id"]: row["skill_states"] for row in response.json()["applications"]}
    assert by_id[1] == [
        {"label": "Apache Airflow", "result": "supported", "source": "keyword"},
        {"label": "Docker", "result": "not_found", "source": "keyword"},
        {"label": "Python", "result": "unassessed"},
    ]
    assert by_id[3][0]["result"] == "unreadable"
    assert client.get(path, headers=auth(2), params=selected).status_code == 403
    assert client.get(path, headers=auth(1), params=selected * 5).status_code == 422
    assert db.query(AnalysisRun).count() == before
    assert db.query(FilterProfile).one().items == [{"label": "SQL", "kind": "skill", "level": "nice"}]
