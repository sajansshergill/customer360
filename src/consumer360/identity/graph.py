from consumer360.utils.hashing import normalise_email, normalise_phone


def build_identity_graph(
    profiles: list[dict], golden_map: dict[str, str]
) -> list[dict]:
    rows: list[dict] = []
    seen: set[tuple] = set()

    def add(gid: str, itype: str, value: str | None, source: str, confidence: float) -> None:
        if not value:
            return
        key = (gid, itype, value, source)
        if key in seen:
            return
        seen.add(key)
        rows.append(
            {
                "golden_profile_id": gid,
                "identifier_type": itype,
                "identifier_value": value,
                "source_system": source,
                "confidence": confidence,
            }
        )

    for p in profiles:
        gid = golden_map.get(p["node_id"])
        if not gid:
            continue
        src = p.get("source_system") or ""
        if p.get("cdc_id"):
            add(gid, "cdc_id", p["cdc_id"], src, 1.0)
        email = normalise_email(p.get("email") or "")
        if email:
            add(gid, "email", email, src, 1.0)
        phone = normalise_phone(p.get("phone") or "")
        if phone:
            add(gid, "phone", phone, src, 0.98)
        if p.get("subscriber_key"):
            add(gid, "subscriber_key", p["subscriber_key"], src, 0.95)
        if p.get("device_id"):
            add(gid, "device_id", p["device_id"], src, 0.90)
    return rows
