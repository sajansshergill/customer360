from __future__ import annotations

from collections import Counter

from consumer360.utils.dates import parse_datetime
from consumer360.utils.hashing import normalise_email


def _as_bool(val) -> bool:
    if isinstance(val, bool):
        return val
    if val is None:
        return False
    return str(val).strip().lower() in {"true", "1", "yes", "y"}


def apply_survivorship(rows: list[dict]) -> dict:
    """Merge a cluster of profile rows into one survivorship dict."""
    cdc_rows = [r for r in rows if r.get("source_system") == "sap_cdc"]
    consent_src = cdc_rows[0] if cdc_rows else {}

    name_rows = sorted(
        rows,
        key=lambda r: parse_datetime(r.get("registered_at")) or parse_datetime("1900-01-01"),
        reverse=True,
    )
    name_row = name_rows[0] if name_rows else {}

    emails = [
        normalise_email(r.get("email") or "")
        for r in rows
        if normalise_email(r.get("email") or "")
    ]
    email = Counter(emails).most_common(1)[0][0] if emails else ""

    first_name = name_row.get("first_name") or ""
    last_name = name_row.get("last_name") or ""

    return {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "marketing_consent": _as_bool(consent_src.get("marketing_consent")),
        "profiling_consent": _as_bool(consent_src.get("profiling_consent")),
        "third_party_sharing": _as_bool(consent_src.get("third_party_sharing")),
        "is_professional": _as_bool(consent_src.get("is_professional") or name_row.get("is_professional")),
        "speciality": (consent_src.get("speciality") or name_row.get("speciality") or "").strip(),
        "registered_at": consent_src.get("registered_at") or name_row.get("registered_at"),
        "phone": consent_src.get("phone") or name_row.get("phone") or "",
        "date_of_birth": consent_src.get("date_of_birth") or name_row.get("date_of_birth") or "",
        "zip_code": consent_src.get("zip_code") or name_row.get("zip_code") or "",
        "city": consent_src.get("city") or name_row.get("city") or "",
    }
