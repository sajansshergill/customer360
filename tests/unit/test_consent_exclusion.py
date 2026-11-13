from consumer360.activation.consent import filter_audience_by_consent


def test_opted_out_excluded():
    members = ["g1", "g2", "g3"]
    consent = {"g1": True, "g2": False, "g3": True}
    assert filter_audience_by_consent(members, consent) == ["g1", "g3"]
