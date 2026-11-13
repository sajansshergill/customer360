import csv, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from generators.people import generate_people
from generators.sap_cdc_profiles import generate_cdc_profiles

def write_csv(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"{path.name}: {len(rows)} rows")

if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    people = generate_people(count)
    out = Path(__file__).parent / "output"
    write_csv(out / "sap_cdc_profiles.csv", generate_cdc_profiles(people))
    pros = sum(p.is_professional for p in people)
    consent = sum(p.marketing_consent for p in people)
    print(f"people={count} professionals={pros} marketing_consent={consent} ({consent/count:.0%})")
