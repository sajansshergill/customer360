from consumer360.identity.survivorship import apply_survivorship


def test_consent_from_cdc_only():
    rows = [
        {
            "source_system": "sap_cdc",
            "email": "a@example.com",
            "first_name": "Ann",
            "last_name": "Bee",
            "marketing_consent": "true",
            "registered_at": "2025-01-01",
            "is_professional": "false",
        },
        {
            "source_system": "sfmc",
            "email": "a@example.com",
            "marketing_consent": "false",
        },
    ]
    surv = apply_survivorship(rows)
    assert surv["marketing_consent"] is True
    assert surv["first_name"] == "Ann"
