CONTRACTS: dict[str, list[str]] = {
    "sap_cdc": [
        "cdc_id",
        "email",
        "first_name",
        "last_name",
        "phone",
        "date_of_birth",
        "marketing_consent",
        "registered_at",
    ],
    "sfmc": ["event_id", "subscriber_key", "email", "event_type", "event_at"],
    "ga4": ["event_id", "device_id", "event_name", "event_at"],
    "aem": ["content_view_id", "email", "category", "viewed_at"],
    "commerce": ["order_id", "email", "category", "ordered_at"],
}


def validate_contract(source: str, rows: list[dict]) -> None:
    required = CONTRACTS.get(source)
    if not required:
        raise ValueError(f"Unknown source: {source}")
    if not rows:
        return
    keys = set(rows[0].keys())
    missing = [c for c in required if c not in keys]
    if missing:
        raise ValueError(f"Contract violation for {source}: missing {missing}")
