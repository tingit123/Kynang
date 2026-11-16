import json
import smtplib
import pytest
from sqlalchemy.orm import sessionmaker
from test_evidence import system, auth
from test_quick_hire import quick, evaluate
from src.models.job import JobApplication
from src.models.evidence import ApplicationEvidence
from src.models.notification import NotificationBatch, NotificationRecipient, UserNotification
from src.models.quick_hire import ApplicationStatusEvent
from src.models.user import User
from src.services import notification_delivery as d


@pytest.fixture
def messaging(quick, monkeypatch):
    client, db = quick
    monkeypatch.setattr(d, "SessionLocal", sessionmaker(bind=db.get_bind(), expire_on_commit=False))
    monkeypatch.delenv("NOTIFY_SIMULATE", raising=False)
    for key in ("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS", "SMTP_FROM"):
        monkeypatch.delenv(key, raising=False)
    def no_network(*args, **kwargs):
        pytest.fail("SMTP must be mocked; no external service in tests")
    monkeypatch.setattr(d.smtplib, "SMTP", no_network)
    monkeypatch.setattr(d.smtplib, "SMTP_SSL", no_network)
    return client, db


def preview(client, ids=None, channels=None, action="acknowledge", **extra):
    profile = client.get("/api/jobs/1/filter-profile", headers=auth(1)).json()
    data = {"application_ids": [1] if ids is None else ids, "profile_hash": profile.get("profile_hash"),
            "action_type": action, "channels": channels or ["in_app"], **extra}
    if action == "invite":
        data["fields"] = {"interview_time": "Sáng thứ Hai", "interview_location": "Văn phòng Demo", "reply_contact": "HR Demo"}
    response = client.post("/api/jobs/1/notification-batches/preview", headers=auth(1), json=data)
    assert response.status_code == 200, response.text
    value = response.json()
    return {**data, "profile_hash": value["profile"]["profile_hash"], "application_ids": [row["application_id"] for row in value["applications"]], "all_matching": False,
            "expected_x": {str(row["application_id"]): row["x"] for row in value["applications"]},
            "preview_token": value["preview_token"], "idempotency_key": "message-test-12345"}


def send(client, payload):
    response = client.post("/api/jobs/1/notification-batches", headers=auth(1), json=payload)
    assert response.status_code == 202, response.text
    return response.json()


def get_batch(client, batch_id):
    return client.get(f"/api/notification-batches/{batch_id}", headers=auth(1)).json()


def enable_smtp(monkeypatch):
    for key, value in {"SMTP_HOST": "mock", "SMTP_PORT": "1025", "SMTP_USER": "mock", "SMTP_PASS": "mock", "SMTP_FROM": "hr@demo.local"}.items():
        monkeypatch.setenv(key, value)


def test_real_in_app_delivery_and_private_worker_read(messaging):
    client, db = messaging
    evaluate(client)
    payload = preview(client)
    assert db.query(NotificationBatch).count() == 0 and db.get(JobApplication, 1).status == "applied"
    initial = send(client, payload)
    assert initial["status"] == "processing" and initial["counts"]["queued"] == 1
    result = get_batch(client, initial["id"])
    assert result["counts"]["sent"] == 1 and result["recipients"][0]["attempt_count"] == 1
    db.expire_all()
    assert db.get(JobApplication, 1).status == "acknowledged"
    assert db.query(ApplicationStatusEvent).one().notification_batch_id == initial["id"]
    worker = client.get("/api/me/notifications", headers=auth(3)).json()
    assert worker["unread_count"] == 1 and len(worker["notifications"]) == 1
    notification = worker["notifications"][0]
    assert set(notification) == {"id", "title", "body", "created_at", "read_at", "simulated"}
    assert client.get("/api/me/notifications", headers=auth(7)).json()["notifications"] == []
    assert client.post(f'/api/me/notifications/{notification["id"]}/read', headers=auth(7)).status_code == 404
    assert client.post(f'/api/me/notifications/{notification["id"]}/read', headers=auth(3)).status_code == 200
    assert get_batch(client, initial["id"])["counts"]["read"] == 1


def test_idempotent_batch_and_success_never_retried(messaging):
    client, db = messaging
    evaluate(client)
    payload = preview(client)
    first = send(client, payload)
    second = send(client, payload)
    assert first["id"] == second["id"] and db.query(NotificationBatch).count() == 1
    assert db.query(UserNotification).count() == 1
    client.post(f'/api/notification-batches/{first["id"]}/retry', headers=auth(1), json={"include_unknown": True})
    assert get_batch(client, first["id"])["recipients"][0]["attempt_count"] == 1


def test_stale_count_and_foreign_application_rejected(messaging):
    client, db = messaging
    evaluate(client)
    payload = preview(client)
    row = db.query(ApplicationEvidence).filter_by(requirement_name="Python").first()
    row.review_result = "not_found"
    db.commit()
    assert client.post("/api/jobs/1/notification-batches", headers=auth(1), json=payload).status_code == 409
    assert db.query(NotificationBatch).count() == 0
    payload["application_ids"] = [2]
    assert client.post("/api/jobs/1/notification-batches", headers=auth(1), json=payload).status_code == 400


def test_unreplaced_variables_blocked(messaging):
    client, db = messaging
    evaluate(client)
    profile = client.get("/api/jobs/1/filter-profile", headers=auth(1)).json()
    response = client.post("/api/jobs/1/notification-batches/preview", headers=auth(1), json={
        "profile_hash": profile.get("profile_hash"), "application_ids": [1], "action_type": "acknowledge", "channels": ["in_app"], "body_template": "Hello {{unknown_value}}"})
    assert response.status_code == 422 and db.query(NotificationBatch).count() == 0


def test_all_pages_selection_and_hundred_limit(messaging):
    client, db = messaging
    for index in range(10, 22):
        db.add(JobApplication(id=index, job_id=1, candidate_id=3, cv_snapshot_text="CV minh họa sử dụng Python và SQL trong dự án của nhóm sinh viên."))
    db.commit()
    evaluate(client)
    payload = preview(client, ids=[], all_matching=True, filters={"min_x": 0})
    assert len(payload["application_ids"]) == 15
    assert client.post("/api/jobs/1/notification-batches/preview", headers=auth(1), json={
        "application_ids": list(range(101)), "profile_hash": payload["profile_hash"], "action_type": "acknowledge", "channels": ["in_app"]}).status_code == 422


def test_smtp_disabled_and_defaults_simulation_off(messaging):
    client, _ = messaging
    config = client.get("/api/notifications/capabilities", headers=auth(1)).json()
    assert config == {"email_enabled": False, "email_error": d.smtp_configuration_error(),
                      "in_app_enabled": True, "simulated": False}
    assert "SMTP_PASS" in config["email_error"]
    profile = client.get("/api/jobs/1/filter-profile", headers=auth(1)).json()
    assert client.post("/api/jobs/1/notification-batches/preview", headers=auth(1), json={
        "application_ids": [1], "profile_hash": profile.get("profile_hash"), "action_type": "acknowledge", "channels": ["email"]}).status_code == 422


def test_all_matching_above_hundred_rejected_without_truncation(messaging):
    client, db = messaging
    for index in range(10, 110):
        db.add(JobApplication(id=index, job_id=1, candidate_id=3, cv_snapshot_text="CV"))
    db.commit()
    profile = client.get("/api/jobs/1/filter-profile", headers=auth(1)).json()
    response = client.post("/api/jobs/1/notification-batches/preview", headers=auth(1), json={
        "all_matching": True, "filters": {"unassessed": True}, "profile_hash": profile.get("profile_hash"),
        "action_type": "acknowledge", "channels": ["in_app"]})
    assert response.status_code == 422
    assert db.query(NotificationBatch).count() == 0


def test_missing_account_does_not_change_application(messaging):
    client, db = messaging
    db.get(User, 3).is_active = False
    db.commit()
    evaluate(client)
    initial = send(client, preview(client))
    result = get_batch(client, initial["id"])
    assert result["counts"]["missing_contact"] == 1
    db.expire_all()
    assert db.get(JobApplication, 1).status == "applied"
    assert db.query(UserNotification).count() == 0


def test_simulation_retry_never_automatically_touches_unknown(messaging, monkeypatch):
    client, db = messaging
    db.get(User, 3).email = "test@fail.demo.local"
    db.get(User, 7).email = "test@timeout.demo.local"
    db.commit()
    monkeypatch.setenv("NOTIFY_SIMULATE", "1")
    evaluate(client)
    initial = send(client, preview(client, [1, 3]))
    result = get_batch(client, initial["id"])
    assert result["counts"]["failed"] == result["counts"]["unknown"] == 1
    db.expire_all()
    assert db.get(JobApplication, 1).status == db.get(JobApplication, 3).status == "applied"
    assert db.query(UserNotification).count() == 0
    monkeypatch.setenv("NOTIFY_SIMULATE", "0")
    client.post(f'/api/notification-batches/{initial["id"]}/retry', headers=auth(1), json={})
    result = get_batch(client, initial["id"])
    assert result["counts"]["sent"] == 1 and result["counts"]["unknown"] == 1
    assert next(r for r in result["recipients"] if r["status"] == "unknown")["attempt_count"] == 1
    client.post(f'/api/notification-batches/{initial["id"]}/retry', headers=auth(1), json={"include_unknown": True})
    result = get_batch(client, initial["id"])
    assert result["counts"]["sent"] == 2 and db.query(UserNotification).count() == 2


@pytest.mark.parametrize("outcome,state", [("ok", "sent"), ("error", "failed"), ("timeout", "unknown")])
def test_smtp_states_and_profile_changes_only_on_success(messaging, monkeypatch, outcome, state):
    client, db = messaging
    enable_smtp(monkeypatch)
    observed = []
    def mocked(*args):
        db.expire_all()
        observed.append(db.query(NotificationRecipient).one().status)
        if outcome == "error":
            raise d.DeliveryError("Mock temporary")
        if outcome == "timeout":
            raise d.DeliveryError("Mock timeout", "unknown", "uncertain", False)
    monkeypatch.setattr(d, "send_email", mocked)
    evaluate(client)
    initial = send(client, preview(client, channels=["email"], action="invite"))
    assert get_batch(client, initial["id"])["recipients"][0]["status"] == state
    db.expire_all()
    assert db.get(JobApplication, 1).status == ("invited" if state == "sent" else "applied")
    assert observed == ["sending"]


def test_legacy_selected_can_receive_notification(messaging):
    client, db = messaging
    db.get(JobApplication, 1).status = "selected"
    db.commit()
    evaluate(client)
    initial = send(client, preview(client, action="invite"))
    assert get_batch(client, initial["id"])["counts"]["sent"] == 1
    db.expire_all()
    assert db.get(JobApplication, 1).status == "invited"
    assert db.query(ApplicationStatusEvent).one().from_status == "selected"


def test_queued_batch_requires_wait_and_never_claims_delivery(messaging, monkeypatch):
    client, db = messaging
    monkeypatch.setattr(d, "process_batch", lambda *_: None)
    evaluate(client)
    initial = send(client, preview(client))
    assert get_batch(client, initial["id"])["counts"]["queued"] == 1
    assert client.post(f'/api/notification-batches/{initial["id"]}/retry', headers=auth(1), json={}).status_code == 409
    assert db.query(UserNotification).count() == 0
    assert db.get(JobApplication, 1).status == "applied"


def test_interrupted_sending_is_unknown_not_automatically_retried(messaging, monkeypatch):
    client, db = messaging
    monkeypatch.setattr(d, "process_batch", lambda *_: None)
    evaluate(client)
    initial = send(client, preview(client, [1, 3]))
    targets = db.query(NotificationRecipient).filter_by(batch_id=initial["id"]).order_by(NotificationRecipient.id).all()
    targets[1].status = "sending"
    db.commit()
    d.recover_interrupted(db)
    result = get_batch(client, initial["id"])
    assert result["counts"]["failed"] == result["counts"]["unknown"] == 1
    assert db.query(UserNotification).count() == 0


def test_invalid_smtp_destination_and_header_are_input_errors(messaging, monkeypatch):
    enable_smtp(monkeypatch)
    with pytest.raises(d.DeliveryError) as error:
        d.send_email("name,extra@demo.local", "Title", "Body")
    assert error.value.status == "failed" and error.value.kind == "input"
    monkeypatch.setenv("SMTP_FROM", "hr@demo.local\r\nBcc: nobody@demo.local")
    with pytest.raises(d.DeliveryError) as error:
        d.send_email("one@demo.local", "Title", "Body")
    assert error.value.status == "failed" and error.value.kind == "configuration"


def test_smtp_individual_addresses_and_timeout_classification(messaging, monkeypatch):
    enable_smtp(monkeypatch)
    messages = []
    class Fake:
        def __init__(self, *args, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def starttls(self, **kwargs): pass
        def login(self, *args): pass
        def send_message(self, message, to_addrs):
            messages.append((message, to_addrs))
            return {}
    monkeypatch.setattr(d.smtplib, "SMTP", Fake)
    d.send_email("one@demo.local", "Title", "Body")
    d.send_email("two@demo.local", "Title", "Body")
    assert [addresses for _, addresses in messages] == [["one@demo.local"], ["two@demo.local"]]
    assert all(message["Cc"] is None and message["Bcc"] is None for message, _ in messages)
    def timeout(*args, **kwargs): raise TimeoutError()
    monkeypatch.setattr(Fake, "send_message", timeout)
    with pytest.raises(d.DeliveryError) as caught:
        d.send_email("one@demo.local", "Title", "Body")
    assert caught.value.status == "unknown" and not caught.value.retryable


def test_gmail_tls_authentication_and_mime_headers(messaging, monkeypatch):
    for key, value in {
        "SMTP_HOST": "smtp.gmail.com", "SMTP_PORT": "465", "SMTP_SECURITY": "ssl",
        "SMTP_USER": "sender@gmail.com", "SMTP_FROM": "sender@gmail.com",
        "SMTP_PASS": "abcd efgh ijkl mnop",
    }.items():
        monkeypatch.setenv(key, value)
    captured = {}
    class FakeSSL:
        def __init__(self, host, port, **kwargs):
            assert host == "smtp.gmail.com" and port == 465
            assert kwargs["context"].verify_mode == 2
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def login(self, user, password):
            assert user == "sender@gmail.com" and password == "abcdefghijklmnop"
        def send_message(self, message, to_addrs):
            captured["message"] = message
            assert to_addrs == ["recipient@gmail.com"]
            return {}
    monkeypatch.setattr(d.smtplib, "SMTP_SSL", FakeSSL)
    d.send_email("recipient@gmail.com", "Lời mời phỏng vấn", "Nội dung tiếng Việt")
    message = captured["message"]
    assert message["Date"] and message["Message-ID"]
    assert str(message["Subject"]) == "Lời mời phỏng vấn"
    assert message.get_content().strip() == "Nội dung tiếng Việt"
    monkeypatch.setenv("SMTP_SECURITY", "none")
    assert not d.smtp_enabled()
    assert "Gmail" in d.smtp_configuration_error()


@pytest.mark.parametrize("disconnect", [False, True])
def test_gmail_login_failure_is_not_reported_as_sent(messaging, monkeypatch, disconnect):
    enable_smtp(monkeypatch)
    monkeypatch.setenv("SMTP_SECURITY", "starttls")
    class AuthFailure:
        def __init__(self, *args, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def starttls(self, **kwargs): pass
        def login(self, *args):
            if disconnect:
                raise smtplib.SMTPServerDisconnected("Disconnected during AUTH")
            raise smtplib.SMTPAuthenticationError(535, b"Invalid login")
    monkeypatch.setattr(d.smtplib, "SMTP", AuthFailure)
    client, _ = messaging
    evaluate(client)
    batch = send(client, preview(client, channels=["email"]))
    result = get_batch(client, batch["id"])
    assert result["counts"]["failed"] == 1
    assert result["counts"].get("sent", 0) == 0
    assert "Mật khẩu ứng dụng" in result["recipients"][0]["last_error"]


@pytest.mark.parametrize("uid,code", [(None, 401), (2, 403), (3, 403), (4, 403), (6, 403), (1, 200), (5, 200)])
@pytest.mark.parametrize("operation", ["preview", "send", "get", "history", "retry"])
def test_sender_permissions(messaging, uid, code, operation):
    client, db = messaging
    evaluate(client)
    payload = preview(client)
    initial = send(client, payload)
    headers = auth(uid) if uid else {}
    if operation == "preview":
        args = {k: v for k, v in payload.items() if k not in {"expected_x", "preview_token", "idempotency_key"}}
        response = client.post("/api/jobs/1/notification-batches/preview", headers=headers, json=args)
    elif operation == "send":
        if uid == 5:
            payload["idempotency_key"] = "admin-message-123"
            args = {k: v for k, v in payload.items() if k not in {"expected_x", "preview_token", "idempotency_key"}}
            payload["preview_token"] = client.post("/api/jobs/1/notification-batches/preview", headers=headers, json=args).json()["preview_token"]
        response = client.post("/api/jobs/1/notification-batches", headers=headers, json=payload)
    elif operation == "get": response = client.get(f'/api/notification-batches/{initial["id"]}', headers=headers)
    elif operation == "history": response = client.get("/api/jobs/1/notification-batches", headers=headers)
    else: response = client.post(f'/api/notification-batches/{initial["id"]}/retry', headers=headers, json={})
    assert response.status_code == (202 if code == 200 and operation in {"send", "retry"} else code), response.text


@pytest.mark.parametrize("uid,code",[(None,401),(3,403),(4,403),(6,403),(1,200),(2,200),(5,200)])
@pytest.mark.parametrize("method",["get","post"])
def test_notification_templates_permissions(messaging,uid,code,method):
    client,_=messaging
    headers=auth(uid) if uid else {}
    payload={"name":"Mẫu xác nhận","action_type":"acknowledge","title_template":"Gửi {{candidate_name}}","body_template":"Cảm ơn bạn đã nộp hồ sơ."}
    r=client.get("/api/notification-templates",headers=headers) if method=="get" else client.post("/api/notification-templates",headers=headers,json=payload)
    assert r.status_code==code


def test_saved_message_templates_are_private_persistent_and_update_by_name(messaging):
    client,db=messaging
    payload={"name":"Lời mời của HR","action_type":"invite","title_template":"Phỏng vấn {{job_title}}","body_template":"Chào {{candidate_name}}, hẹn bạn lúc {{interview_time}}."}
    first=client.post("/api/notification-templates",headers=auth(1),json=payload).json()
    payload["body_template"]="Nội dung HR đã sửa cho {{candidate_name}}."
    changed=client.post("/api/notification-templates",headers=auth(1),json=payload).json()
    assert changed["id"]==first["id"]
    assert client.get("/api/notification-templates",headers=auth(1)).json()["templates"]==[changed]
    assert client.get("/api/notification-templates",headers=auth(2)).json()["templates"]==[]
    assert client.get("/api/notification-templates",headers=auth(5)).json()["templates"]==[]
    assert db.query(NotificationBatch).count()==db.query(UserNotification).count()==0


@pytest.mark.parametrize("field,value",[("name"," "),("title_template"," "),("body_template"," "),("title_template","Title\nBcc: bad"),("body_template","{{not_supported}}"),("body_template","{{candidate_name")])
def test_invalid_message_template_cannot_be_saved(messaging,field,value):
    client,_=messaging
    payload={"name":"Mẫu","action_type":"acknowledge","title_template":"Tiêu đề","body_template":"Nội dung"}
    payload[field]=value
    assert client.post("/api/notification-templates",headers=auth(1),json=payload).status_code==422


def test_custom_notification_is_rendered_and_edit_requires_new_preview(messaging):
    client,db=messaging
    evaluate(client)
    payload=preview(client,title_template="HR: {{candidate_name}}",body_template="Nội dung do HR soạn cho {{job_title}} tại {{company_name}}.")
    changed={**payload,"body_template":"Lời khác sau khi xem trước."}
    assert client.post("/api/jobs/1/notification-batches",headers=auth(1),json=changed).status_code==409
    assert db.query(UserNotification).count()==0
    result=get_batch(client,send(client,payload)["id"])
    assert result["recipients"][0]["title"]=="HR: worker"
    assert "Nội dung do HR soạn cho Backend tại Demo."==db.query(UserNotification).one().body


def test_direct_recruitment_without_filter_or_evaluation(messaging):
    from src.models.quick_hire import FilterProfile
    client,db=messaging
    db.query(FilterProfile).delete();db.commit()
    payload=preview(client,direct_application=True,profile_hash=None)
    assert payload["expected_x"]=={"1":None}
    result=get_batch(client,send(client,payload)["id"])
    assert result["counts"]["sent"]==1
    assert db.query(FilterProfile).count()==db.query(ApplicationEvidence).count()==0
    assert db.query(UserNotification).count()==1


def test_sending_message_does_not_advance_or_reset_recruitment_round(messaging):
    from src.models.recruitment_process import ApplicationProcess, ApplicationProcessEvent
    client,db=messaging
    db.add(ApplicationProcess(application_id=1,stage="interviewing",version=3))
    db.commit()
    evaluate(client)
    send(client,preview(client))
    db.expire_all()
    process=db.get(ApplicationProcess,1)
    assert process.stage=="interviewing" and process.version==3
    assert db.query(ApplicationProcessEvent).count()==0


@pytest.mark.parametrize("ids,all_matching,status",[([1,3],False,422),([1],True,422),([2],False,400)])
def test_direct_recruitment_never_changes_target_scope(messaging,ids,all_matching,status):
    client,_=messaging
    r=client.post("/api/jobs/1/notification-batches/preview",headers=auth(1),json={"application_ids":ids,"all_matching":all_matching,"direct_application":True,"action_type":"acknowledge","channels":["in_app"]})
    assert r.status_code==status
