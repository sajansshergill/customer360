def filter_audience_by_consent(
    golden_profile_ids: list[str], consent_by_golden: dict[str, bool]
) -> list[str]:
    """Hard-exclude opted-out profiles from activation audiences."""
    return [gid for gid in golden_profile_ids if consent_by_golden.get(gid, False)]
