"""Part of the Consumer360 CDP - see README for where this file fits."""
import random
from datetime import datetime, timedelta
from .people import Person

JOURNEYS_CONSUMER = ["Welcome Series", "Whitening Education", "Reorder Reminder", "Sensitivity Care"]
JOURNEYS_PRO = ["Clinical Updates", "Professional Samples", "New Product Launch"]

def generate_sfmc_engagement(people: list[Person], seed: int = 11) -> list[dict]:
    """Salesforce Marketing Cloud. Key problem: subscriber_key has NOTHING to do with cdc_id,
    and ~25% of people engage on their alt email."""
    rng = random.Random(seed)
    rows, n = [], 0
    base = datetime(2025, 6, 1, 9, 0, 0)

    def add(p, sub_key, email_used, journey, event, when, category=""):
        nonlocal n; n += 1
        rows.append({"event_id": f"sfmc_{n:06d}", "subscriber_key": sub_key,
                     "email": email_used, "journey_name": journey, "event_type": event,
                     "event_at": when.isoformat(), "link_category": category})

    for p in people:
        if rng.random() > 0.62:            # 62% have any email engagement
            continue
        sub_key = f"sub_{p.true_id}"       # SFMC's own ID - no relation to cdc_id
        email_used = p.alt_email if rng.random() < 0.25 else p.email
        journeys = JOURNEYS_PRO if p.is_professional else JOURNEYS_CONSUMER
        for _ in range(rng.randint(1, 5)):
            journey = rng.choice(journeys)
            sent_at = base + timedelta(days=rng.randint(0, 150), hours=rng.randint(0, 12))
            add(p, sub_key, email_used, journey, "send", sent_at)
            if rng.random() < 0.55:
                add(p, sub_key, email_used, journey, "open", sent_at + timedelta(hours=rng.randint(1, 48)))
                if rng.random() < 0.45:
                    cat = rng.choice(["Oral Care", "Whitening", "Sensitivity", "Professional"])
                    add(p, sub_key, email_used, journey, "click", sent_at + timedelta(hours=rng.randint(2, 72)), cat)
            if rng.random() < 0.03:
                add(p, sub_key, email_used, journey, "bounce", sent_at)
    return rows
