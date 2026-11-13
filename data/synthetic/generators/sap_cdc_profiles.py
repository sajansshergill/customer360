import random
from datetime import date, timedelta
from .people import Person

def generate_cdc_profiles(people: list[Person], seed: int = 7) -> list[dict]:
    """SAP CDC / Gigya = source of truth for identity + consent."""
    rng = random.Random(seed)
    rows = []
    for p in people:
        # ~12% register in the last 14 days relative to pipeline as-of (2025-11-01)
        if rng.random() < 0.12:
            registered = date(2025, 10, 18) + timedelta(days=rng.randint(0, 13))
        else:
            registered = date(2025, 1, 1) + timedelta(days=rng.randint(0, 280))
        rows.append({
            "cdc_id": f"cdc_{p.true_id}",
            "email": p.email,
            "first_name": p.first_name,
            "last_name": p.last_name,
            "phone": p.phone,
            "date_of_birth": p.date_of_birth,
            "city": p.city,
            "zip_code": p.zip_code,
            "is_professional": p.is_professional,
            "speciality": p.speciality or "",
            "marketing_consent": p.marketing_consent,
            "profiling_consent": p.profiling_consent,
            "third_party_sharing": False,
            "registered_at": registered.isoformat(),
        })
    return rows
