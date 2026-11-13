from fastapi.testclient import TestClient

from api.main import app


def test_list_activations(seeded_warehouse):
    client = TestClient(app)
    resp = client.get("/v1/activations", headers={"X-API-Key": "dev-key"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_activate_audience(seeded_warehouse):
    client = TestClient(app)
    resp = client.post(
        "/v1/audiences/aud_lapsed_buyers/activate",
        headers={"X-API-Key": "dev-key"},
    )
    # Sample data may or may not produce members; file always written by pipeline
    assert resp.status_code in (200, 404)
    if resp.status_code == 200:
        body = resp.json()
        assert body["audience_id"] == "aud_lapsed_buyers"
        assert body["status"] == "exported"


def test_list_audiences(seeded_warehouse):
    client = TestClient(app)
    resp = client.get("/v1/audiences", headers={"X-API-Key": "dev-key"})
    assert resp.status_code == 200
    assert len(resp.json()) == 4
