# Identity resolution

## Problem

The same person appears with different emails (`example.com` vs `gmail.com` alt), unrelated SFMC `subscriber_key`, and shared `device_id` across GA4 and AEM. CDC remains the consent and profile source of truth.

## Algorithm (Python)

1. Collect edges from Bronze: verified CDC emails, SFMC emails, GA4+AEM device links, commerce emails.
2. **Union-find** on normalised email strings (`consumer360.identity.graph.IdentityGraph`).
3. `golden_profile_id = SHA-256(salt:canonical_email)` for each component root.
4. Survivorship (`survivorship.merge_profile`) copies attributes from SAP CDC only; consent never downgraded in Silver helpers.

## Match types (`int_identity_matches`)

| `match_type` | Typical confidence |
|--------------|-------------------|
| `cdc_id` | 1.00 |
| `verified_email` | 1.00 |
| `device` | 0.90 |
| `sfmc_standalone` | 0.95 |

dbt Silver models are passthrough `select *` from these Python tables so Gold can `ref()` them with tests and documentation.

## Worked example

If SFMC sends to `jane.doe@gmail.com` but CDC holds `jane.doe42@example.com`, they remain separate golden profiles unless a future probabilistic rule links them. Device overlap between GA4 and AEM links sessions to the CDC email when both events carry the same verified email.
