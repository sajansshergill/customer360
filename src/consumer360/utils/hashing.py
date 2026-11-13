import hashlib

def hash_pii(value: str | None, salt: str) -> str | None:
    """One-way token for PII. Raw PII lives only in Bronze; Silver/Gold use this."""
    if not value:
        return None
    return hashlib.sha256(f"{salt}:{value.strip().lower()}".encode()).hexdigest()

def normalise_email(value: str) -> str:
    return value.strip().lower()

def normalise_phone(value: str) -> str:
    return "".join(ch for ch in value if ch.isdigit())[-10:]
