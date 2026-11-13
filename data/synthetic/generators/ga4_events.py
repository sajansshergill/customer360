import random
from datetime import datetime, timedelta

from .people import Person

EVENTS = ["page_view", "session_start", "view_item"]
PAGES = ["Home", "Whitening", "Oral Care", "Professional", "Checkout"]


def generate_ga4_events(people: list[Person], seed: int = 13) -> list[dict]:
    rng = random.Random(seed)
    rows = []
    n = 0
    base = datetime(2025, 6, 1, 10, 0, 0)
    for p in people:
        if rng.random() > 0.7:
            continue
        for _ in range(rng.randint(1, 4)):
            n += 1
            email = "" if rng.random() < 0.4 else p.email  # more logged-in for identity links
            # Bias ~25% of events into the last 7 days before as-of 2025-11-01
            if rng.random() < 0.25:
                when = datetime(2025, 10, 25, 10, 0, 0) + timedelta(
                    days=rng.randint(0, 6), hours=rng.randint(0, 10)
                )
            else:
                when = base + timedelta(days=rng.randint(0, 150), hours=rng.randint(0, 10))
            rows.append(
                {
                    "event_id": f"ga4_{n:06d}",
                    "device_id": p.device_id,
                    "user_pseudo_id": f"pseudo_{p.device_id}",
                    "email": email,
                    "session_id": f"sess_{p.true_id}_{rng.randint(0, 3)}",
                    "event_name": rng.choice(EVENTS),
                    "item_name": rng.choice(PAGES),
                    "event_at": when.isoformat(),
                }
            )
    return rows
