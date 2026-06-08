from datetime import datetime
from api import Api42
from models import Projects_42

def _parse_dt(s: str | None):
    if not s:
        return None
    return datetime.fromisoformat(s.replace("Z", "+00:00"))

def _map_project(raw: dict) -> dict:
	STATUS_MAP = {
    "finished": "done",
    "in_progress": "in_progress",
    "creating_group": "in_progress",
    "searching_a_group": "in_progress",
    "waiting_for_correction": "in_progress"
	}
	return {
		"name": raw["project"]["name"],
		"slug": raw["project"]["slug"],
		"mark": raw["final_mark"],
		"status": STATUS_MAP.get(raw["status"], "todo"),
		"validated": raw["validated?"],
		"validated_at": _parse_dt(raw["marked_at"]),
		"retriable_at": _parse_dt(raw["retriable_at"])
	}

def sync_projects(db) -> dict:
    api = Api42()
    raw_projects = api.get_projects_users()
    raw_projects = [raw for raw in raw_projects if 21 in raw["cursus_ids"]]
    created, updated = 0, 0
    for raw in raw_projects:
        mapped = _map_project(raw)
        existing = db.query(Projects_42).filter_by(slug=mapped["slug"]).first()
        if existing:
            for key, value in mapped.items():
                setattr(existing, key, value)
            updated += 1
        else:
            db.add(Projects_42(**mapped))
            created += 1
    db.commit()
    return {"created": created, "updated": updated}
		