"""Non-destructive migration from the prior filter format and selection audit."""
import json
from sqlalchemy import inspect, text
from src.models.quick_hire import FilterProfile
from src.services.evidence_matcher import digest


def migrate(engine, session_factory):
    if engine.dialect.name == "mysql":
        with engine.begin() as connection:
            role = next(c for c in inspect(connection).get_columns("users") if c["name"] == "role")
            existing = getattr(role["type"], "enums", None)
            required = ["admin", "worker", "employer", "course_provider", "candidate", "provider"]
            if existing and any(value not in existing for value in required):
                # Append new values to preserve all historical enum values and their order.
                values = existing + [value for value in required if value not in existing]
                enum = ", ".join("'" + value.replace("'", "''") + "'" for value in values)
                connection.execute(text(f"ALTER TABLE users MODIFY COLUMN role ENUM({enum}) NOT NULL DEFAULT 'worker'"))
            for table, column in [("filter_profiles", "cutpoints"), ("application_status_events", "batch_id")]:
                definition = next((c for c in inspect(connection).get_columns(table) if c["name"] == column), None)
                if definition and not definition["nullable"]:
                    connection.execute(text(f"ALTER TABLE {table} MODIFY COLUMN {column} {definition['type']} NULL"))
    with session_factory() as db:
        for profile in db.query(FilterProfile).all():
            items = [{key: item[key] for key in ("label", "kind", "level")} for item in profile.items]
            name = "[DEMO] Bộ lọc kỹ năng" if profile.name == "[DEMO] Bộ lọc 50/70" else profile.name
            data = {"name": name, "items": items}
            new_hash = digest(json.dumps(data, sort_keys=True, ensure_ascii=False))
            if profile.items != items or profile.profile_hash != new_hash or profile.name != name:
                profile.items, profile.name, profile.profile_hash = items, name, new_hash
        db.commit()
