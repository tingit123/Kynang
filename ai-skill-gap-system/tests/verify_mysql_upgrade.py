"""Run ONLY against a disposable MySQL initialized with the original main schema."""
import os
if os.getenv('MERGE_TEST_DATABASE') != '1':
    raise SystemExit('This check requires MERGE_TEST_DATABASE=1 and a disposable database.')

from sqlalchemy import inspect, text
from src.database import engine
from src.main import wait_for_db_and_init

with engine.begin() as conn:
    conn.execute(text("INSERT INTO job_postings (title, company, industry) VALUES ('Legacy job', 'Legacy company', 'IT')"))
    original_skills = conn.execute(text('SELECT COUNT(*) FROM skill_catalog')).scalar()
    assert original_skills > 0

wait_for_db_and_init(max_retries=1, delay=0)
wait_for_db_and_init(max_retries=1, delay=0)

columns = {c['name'] for c in inspect(engine).get_columns('users')}
assert {'is_active', 'phone', 'is_deleted', 'latest_cv_analysis'} <= columns
with engine.begin() as conn:
    assert conn.execute(text('SELECT COUNT(*) FROM skill_catalog')).scalar() == original_skills
    assert conn.execute(text("SELECT COUNT(*) FROM job_postings WHERE title='Legacy job' AND industry='IT'")).scalar() == 1
    assert conn.execute(text("SELECT COUNT(*) FROM users WHERE email='admin@skillgap.com' AND is_active=1")).scalar() == 1
    conn.execute(text("INSERT INTO job_postings (title, company, industry) VALUES ('Tin job', 'Tin company', 'Cong nghe thong tin')"))
    assert conn.execute(text("SELECT COUNT(*) FROM job_postings WHERE title='Tin job'")).scalar() == 1
print('MySQL legacy upgrade: PASS (existing data retained, new columns, wider industry, idempotent startup)')
