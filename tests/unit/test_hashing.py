from consumer360.utils.hashing import hash_pii, normalise_email, normalise_phone


def test_normalise_email():
    assert normalise_email("  Test@Example.COM ") == "test@example.com"


def test_normalise_phone():
    assert normalise_phone("+1 (201) 555-0001") == "2015550001"


def test_hash_pii_stable():
    a = hash_pii("test@example.com", "salt")
    b = hash_pii("test@example.com", "salt")
    assert a == b
    assert hash_pii(None, "salt") is None
