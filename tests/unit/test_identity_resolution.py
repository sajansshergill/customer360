from consumer360.identity.resolver import (
    UnionFind,
    build_edges,
    resolve_golden_ids_with_profiles,
)


def test_union_find_links_nodes():
    uf = UnionFind()
    uf.union("a", "b")
    uf.union("b", "c")
    assert uf.find("a") == uf.find("c")


def test_email_match_merges_cdc_and_sfmc():
    profiles = [
        {
            "node_id": "cdc_1",
            "cdc_id": "cdc_p00001",
            "email": "Ada.Lovelace@Example.com",
            "phone": "2015550001",
            "subscriber_key": "",
            "device_id": "",
            "full_name": "Ada Lovelace",
            "date_of_birth": "1990-01-01",
            "zip_code": "07302",
            "source_system": "sap_cdc",
        },
        {
            "node_id": "sfmc_1",
            "cdc_id": None,
            "email": "ada.lovelace@example.com",
            "phone": "",
            "subscriber_key": "sub_p00001",
            "device_id": "",
            "full_name": "",
            "date_of_birth": None,
            "zip_code": "",
            "source_system": "sfmc",
        },
    ]
    edges = build_edges(profiles)
    assert any(e["match_type"] == "verified_email" for e in edges)
    golden = resolve_golden_ids_with_profiles(edges, profiles)
    assert golden["cdc_1"] == golden["sfmc_1"]
    assert golden["cdc_1"] == "gold_p00001"


def test_unrelated_profiles_stay_separate():
    profiles = [
        {
            "node_id": "cdc_a",
            "cdc_id": "cdc_a",
            "email": "a@example.com",
            "phone": "1111111111",
            "subscriber_key": "",
            "device_id": "",
            "full_name": "Ann Alpha",
            "date_of_birth": "1991-01-01",
            "zip_code": "10001",
            "source_system": "sap_cdc",
        },
        {
            "node_id": "cdc_b",
            "cdc_id": "cdc_b",
            "email": "b@example.com",
            "phone": "2222222222",
            "subscriber_key": "",
            "device_id": "",
            "full_name": "Bob Beta",
            "date_of_birth": "1992-02-02",
            "zip_code": "10002",
            "source_system": "sap_cdc",
        },
    ]
    edges = build_edges(profiles)
    golden = resolve_golden_ids_with_profiles(edges, profiles)
    assert golden["cdc_a"] != golden["cdc_b"]
