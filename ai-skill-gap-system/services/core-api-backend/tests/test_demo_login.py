import pytest
from test_evidence import system
from src.routers.auth import router
from src.models.user import User, Employer


@pytest.fixture
def demo(system, monkeypatch):
    client, db = system
    client.app.include_router(router, prefix="/api/auth")
    user = db.get(User, 1)
    user.email = "evidence.employer@demo.local"
    db.add(Employer(user_id=1, contact_name="HR Demo", is_verified=True))
    db.commit()
    monkeypatch.setenv("DEMO_EMPLOYER_LOGIN", "1")
    return client, db


def enter(client, origin="http://localhost:8080", hostname="localhost"):
    return client.post(f"http://{hostname}:8000/api/auth/demo/employer", headers={"Origin": origin})


def test_real_employer_session_without_password(demo):
    client, db = demo
    password_hash = db.get(User, 1).password_hash
    response = enter(client)
    assert response.status_code == 200
    assert response.json()["role"] == "employer" and response.json()["user_id"] == 1
    assert "HttpOnly" in response.headers["set-cookie"]
    me = client.get("http://localhost:8000/api/auth/me")
    assert me.status_code == 200 and me.json()["email"] == "evidence.employer@demo.local"
    assert db.get(User, 1).password_hash == password_hash
    assert client.post("http://localhost:8000/api/auth/login").status_code == 400


@pytest.mark.parametrize("flag", [None, "0", "false"])
def test_demo_disabled_unless_explicit(demo, monkeypatch, flag):
    client, _ = demo
    if flag is None: monkeypatch.delenv("DEMO_EMPLOYER_LOGIN", raising=False)
    else: monkeypatch.setenv("DEMO_EMPLOYER_LOGIN", flag)
    assert enter(client).status_code == 404


@pytest.mark.parametrize("origin,host", [("https://example.com", "localhost"), ("http://localhost:8080", "example.com"), ("null", "localhost")])
def test_demo_rejects_non_local_browser_context(demo, origin, host):
    client, _ = demo
    assert enter(client, origin, host).status_code == 403


@pytest.mark.parametrize("change", ["missing", "admin", "inactive", "deleted", "unapproved"])
def test_demo_cannot_select_another_or_unapproved_account(demo, change):
    client, db = demo
    user = db.get(User, 1)
    if change == "missing": user.email = "other@demo.local"
    if change == "admin": user.role = "admin"
    if change == "inactive": user.is_active = False
    if change == "deleted": user.is_deleted = True
    if change == "unapproved": db.query(Employer).filter_by(user_id=1).one().is_verified = False
    db.commit()
    assert enter(client).status_code == (403 if change == "unapproved" else 409)
