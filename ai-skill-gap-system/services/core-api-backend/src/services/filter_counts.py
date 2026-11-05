"""Equal-item CV evidence counts. No inferred proficiency assessment."""


def calculate(items, evidence, run_status):
    counts = {"supported": 0, "not_found": 0, "needs_review": 0, "unreadable": 0}
    value = {"x": None, "y": len(items), "missing_must": [], "counts": counts,
             "skill_states": [{"label": item["label"], "result": "unreadable" if run_status == "unreadable" else "unassessed"} for item in items]}
    if not items or run_status != "done":
        return value
    by_label = {row["requirement_name"]: row for row in evidence}
    missing = []
    states = []
    for item in items:
        row = by_label.get(item["label"], {})
        result = row.get("review_result") or row.get("result", "needs_review")
        if result not in counts:
            result = "needs_review"
        counts[result] += 1
        states.append({"label": item["label"], "result": result})
        if item["level"] == "must" and result != "supported":
            missing.append(item["label"])
    return {**value, "x": counts["supported"], "missing_must": missing, "skill_states": states}


def select_results(rows, xs=None, min_x=None, missing=False, unassessed=False, priority_skills=None):
    """Numeric chips and the two special chips are combined with OR."""
    active = bool(xs) or min_x is not None or missing or unassessed
    selected = []
    for row in rows:
        match = ((row["x"] is not None and (row["x"] in (xs or []) or (min_x is not None and row["x"] >= min_x)))
                 or (missing and bool(row["missing_must"])) or (unassessed and row["x"] is None))
        if match or (not active and row["x"] is not None):
            selected.append(row)
    priorities = set(priority_skills or [])
    return sorted(selected, key=lambda row: (-sum(s["label"] in priorities and s["result"] == "supported" for s in row.get("skill_states", [])),
                  -(row["x"] if row["x"] is not None else -1),
                  str(row.get("applied_at") or "9999"), row["application_id"]))
