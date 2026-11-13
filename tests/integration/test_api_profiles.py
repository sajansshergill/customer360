from fastapi.testclient import TestClient

import duckdb

from api.main import app


def test_get_profile(seeded_warehouse):
    settings = seeded_warehouse
    client = TestClient(app)
    con = duckdb.connect(str(settings.warehouse_path), read_only=True)
    try:
        gid = con.execute("SELECT golden_profile_id FROM gold_consumer_360 LIMIT 1").fetchone()
        if not gid:
            gid = con.execute(
                "SELECT golden_profile_id FROM gold_professional_360 LIMIT 1"
            ).fetchone()
    finally:
        con.close()

    assert gid
    resp = client.get(f"/v1/profiles/{gid[0]}", headers={"X-API-Key": "dev-key"})
    assert resp.status_code == 200
    assert resp.json()["golden_profile_id"] == gid[0]


def test_health():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["ok"] is True
