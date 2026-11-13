"""Synthetic data orchestrator: generates ONE population of people, then renders
them into all 5 source-system files - so the same person appears differently
in every system, exactly like real life.

Run:
  python -m data.synthetic.generate --profiles 1000 --seed 42
  python data/synthetic/generate.py 1000
"""
import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from generators.people import generate_people
from generators.sap_cdc_profiles import generate_cdc_profiles
from generators.sfmc_engagement import generate_sfmc_engagement
from generators.ga4_events import generate_ga4_events
from generators.aem_commerce import generate_aem_content, generate_orders


def write_csv(path, rows):
    if not rows:
        print(f"{path.name}: 0 rows")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        wtr = csv.DictWriter(f, fieldnames=rows[0].keys())
        wtr.writeheader()
        wtr.writerows(rows)
    print(f"{path.name}: {len(rows)} rows")


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic Consumer360 source files")
    parser.add_argument("--profiles", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("count", nargs="?", type=int, help="positional profile count (back-compat)")
    args = parser.parse_args()
    count = args.count if args.count is not None else args.profiles

    people = generate_people(count, seed=args.seed)
    out = Path(__file__).parent / "output"
    write_csv(out / "sap_cdc_profiles.csv", generate_cdc_profiles(people, seed=args.seed + 1))
    write_csv(out / "sfmc_engagement.csv", generate_sfmc_engagement(people, seed=args.seed + 2))
    write_csv(out / "ga4_events.csv", generate_ga4_events(people, seed=args.seed + 3))
    write_csv(out / "aem_content.csv", generate_aem_content(people, seed=args.seed + 4))
    write_csv(out / "commerce_orders.csv", generate_orders(people, seed=args.seed + 5))


if __name__ == "__main__":
    main()
