"""Remove confirmed employer demo records and dependent rows, never candidate users.

Defaults to dry-run. --apply requires the operator to have a database backup.
The allowlist deliberately identifies accounts rather than matching job keywords.
"""
import argparse
import json
from sqlalchemy import MetaData, select, or_, delete
from src.database import engine

DEMO_EMAILS = ("evidence.employer@demo.local", "employer_test@skillgap.com")


def clean_demo(connection, apply=False):
    metadata = MetaData()
    metadata.reflect(bind=connection)
    users = metadata.tables["users"]
    owners = list(connection.execute(select(users.c.id).where(
        users.c.email.in_(DEMO_EMAILS), users.c.role == "employer")).scalars())
    selected = {}
    for table in metadata.sorted_tables:
        if table.name == "users" or len(table.primary_key.columns) != 1:
            continue
        roots = []
        if table.name == "job_postings":
            roots.append(table.c.employer_id.in_(owners))
        if table.name in {"recruiter_contacts", "notification_templates", "filter_profiles"}:
            for name in ("owner_id", "owner_user_id", "employer_id"):
                if name in table.c:
                    roots.append(table.c[name].in_(owners))
        if roots:
            key = list(table.primary_key.columns)[0]
            selected[table.name] = set(connection.execute(select(key).where(or_(*roots))).scalars())
    # Traverse all foreign keys, including legacy tables no longer mapped by ORM.
    changed = True
    while changed:
        changed = False
        for table in metadata.sorted_tables:
            if table.name == "users" or len(table.primary_key.columns) != 1:
                continue
            predicates = [fk.parent.in_(selected[fk.column.table.name])
                          for fk in table.foreign_keys
                          if selected.get(fk.column.table.name)]
            if not predicates:
                continue
            key = list(table.primary_key.columns)[0]
            found = set(connection.execute(select(key).where(or_(*predicates))).scalars())
            before = selected.setdefault(table.name, set())
            if not found.issubset(before):
                before.update(found)
                changed = True
    counts = {name: len(ids) for name, ids in selected.items() if ids}
    if apply:
        for table in reversed(metadata.sorted_tables):
            ids = selected.get(table.name)
            if ids:
                connection.execute(delete(table).where(list(table.primary_key.columns)[0].in_(ids)))
    return counts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    options = parser.parse_args()
    with engine.begin() as connection:
        print(json.dumps({"apply": options.apply, "rows": clean_demo(connection, options.apply)}, sort_keys=True))
