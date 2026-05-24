import json
from pathlib import Path

from scripts.infra.verify_firebase_rtdb import FirebaseReadinessResult, verify_firebase_rtdb

ROOT = Path(__file__).resolve().parents[2]


def test_firebase_config_points_to_realtime_database_rules_file():
    config = json.loads((ROOT / "firebase.json").read_text(encoding="utf-8"))

    assert config == {"database": {"rules": "database.rules.json"}}
    assert (ROOT / config["database"]["rules"]).exists()


def test_database_rules_match_prd_hackathon_open_rules_with_explicit_acknowledgement():
    rules = json.loads((ROOT / "database.rules.json").read_text(encoding="utf-8"))

    assert rules["rules"][".read"] == "auth != null || true"
    assert rules["rules"][".write"] == "auth != null || true"


def test_verify_firebase_rtdb_reports_existing_project_and_instances(monkeypatch):
    calls = []

    def fake_request_json(url, token, quota_project):
        calls.append((url, token, quota_project))
        if url.endswith("/locations/-/instances"):
            return {"instances": [{"name": "projects/demo/locations/us-central1/instances/demo-default-rtdb"}]}
        return {"projectId": "demo"}

    monkeypatch.setattr("scripts.infra.verify_firebase_rtdb.request_json", fake_request_json)

    result = verify_firebase_rtdb(project_id="demo", token="redacted-token")

    assert result == FirebaseReadinessResult(
        project_id="demo",
        firebase_project_exists=True,
        database_instances=("projects/demo/locations/us-central1/instances/demo-default-rtdb",),
    )
    assert all(call[1] == "redacted-token" for call in calls)
    assert all(call[2] == "demo" for call in calls)
