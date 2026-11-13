import random
from dataclasses import dataclass

FIRST = ["Aarav","Priya","Marcus","Elena","James","Fatima","Chen","Sofia","David","Anita",
         "Michael","Kavita","Omar","Julia","Ryan","Meera","Lucas","Nina","Arjun","Grace"]
LAST = ["Sharma","Patel","Johnson","Garcia","Kim","Nguyen","Singh","Brown","Kaur","Ali",
        "Murphy","Shah","Torres","Lee","Wilson","Gupta","Chen","Davis","Khan","Mehta"]
CITIES = [("Jersey City","07302"),("New York","10001"),("Piscataway","08854"),
          ("Chicago","60601"),("Austin","73301"),("Seattle","98101")]
SPECIALITIES = ["General Dentistry","Orthodontics","Orthodontics","Periodontics","Paediatrics"]

@dataclass
class Person:
    true_id: str            # ground truth — NEVER exported to a source file, only used to create realistic duplicates
    first_name: str
    last_name: str
    email: str
    phone: str
    device_id: str
    date_of_birth: str
    city: str
    zip_code: str
    is_professional: bool
    speciality: str | None
    marketing_consent: bool
    profiling_consent: bool

    @property
    def full_name(self): return f"{self.first_name} {self.last_name}"
    @property
    def alt_email(self):  # same person, second email — this is WHY identity resolution exists
        return f"{self.first_name.lower()}.{self.last_name.lower()}@gmail.com"

def generate_people(count: int, seed: int = 42) -> list[Person]:
    rng = random.Random(seed)
    people = []
    for i in range(count):
        first, last = rng.choice(FIRST), rng.choice(LAST)
        city, zip_code = rng.choice(CITIES)
        is_pro = i < count // 10                      # 10% are dental professionals
        marketing = rng.random() < 0.78               # 78% consent rate — realistic, not 100%
        people.append(Person(
            true_id=f"p{i:05d}",
            first_name=first, last_name=last,
            email=f"{first.lower()}.{last.lower()}{i}@example.com",
            phone=f"201555{i:04d}",
            device_id=f"dev-{rng.randint(100000, 999999)}",
            date_of_birth=f"{rng.randint(1965, 2005)}-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}",
            city=city, zip_code=zip_code,
            is_professional=is_pro,
            speciality=rng.choice(SPECIALITIES) if is_pro else None,
            marketing_consent=marketing,
            profiling_consent=marketing and rng.random() < 0.85,
        ))
    return people
