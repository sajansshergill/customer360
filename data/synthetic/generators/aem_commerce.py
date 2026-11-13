import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

from .people import Person

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "seeds" / "product_catalog.csv"

CONTENT_CATEGORIES = ["Whitening", "Oral Care", "Sensitivity", "Professional"]
TITLES = {
    "Whitening": ["How Whitening Works", "Whitening Tips", "Bright Smile Guide"],
    "Oral Care": ["Daily Oral Care", "Brush Better", "Healthy Gums"],
    "Sensitivity": ["Sensitivity Relief", "Gentle Care"],
    "Professional": ["Clinical Resources", "Practice Growth"],
}


def _load_catalog() -> list[dict]:
    with CATALOG.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def generate_aem_content(people: list[Person], seed: int = 17) -> list[dict]:
    rng = random.Random(seed)
    rows = []
    n = 0
    base = datetime(2025, 6, 1, 11, 0, 0)
    for p in people:
        if rng.random() > 0.55:
            continue
        for _ in range(rng.randint(1, 3)):
            n += 1
            cat = rng.choice(CONTENT_CATEGORIES)
            rows.append(
                {
                    "content_view_id": f"aem_{n:06d}",
                    "email": p.email if rng.random() < 0.75 else "",
                    "device_id": p.device_id if rng.random() < 0.4 else "",
                    "page_title": rng.choice(TITLES[cat]),
                    "category": cat,
                    "viewed_at": (base + timedelta(days=rng.randint(0, 150))).isoformat(),
                }
            )
    return rows


def generate_orders(people: list[Person], seed: int = 19) -> list[dict]:
    rng = random.Random(seed)
    catalog = _load_catalog()
    rows = []
    n = 0
    base = datetime(2025, 6, 15, 12, 0, 0)
    for p in people:
        if rng.random() > 0.4:
            continue
        for _ in range(rng.randint(1, 3)):
            n += 1
            product = rng.choice(catalog)
            qty = rng.randint(1, 2)
            price = float(product["price"])
            # Mix recent and lapsed (60–120d before 2025-11-01) purchases
            if rng.random() < 0.35:
                when = datetime(2025, 7, 5, 12, 0, 0) + timedelta(days=rng.randint(0, 55))
            else:
                when = base + timedelta(days=rng.randint(0, 150))
            rows.append(
                {
                    "order_id": f"ord_{n:06d}",
                    "order_line_id": f"line_{n:06d}",
                    "email": p.email,
                    "sku": product["sku"],
                    "product_name": product["product_name"],
                    "category": product["category"],
                    "quantity": qty,
                    "unit_price": price,
                    "order_total": round(price * qty, 2),
                    "ordered_at": when.isoformat(),
                }
            )
    return rows
