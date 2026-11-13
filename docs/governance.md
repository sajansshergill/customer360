# Governance

## Consent

SAP CDC fields `marketing_consent`, `profiling_consent`, and `third_party_sharing` are authoritative. Silver copies them verbatim; dbt audiences apply `consent_filter` so opted-out profiles never appear in audience tables.

Snapshots `snap_consent` and `snap_consumer_profile` record historical changes when dbt snapshot jobs run.

## PII

- Raw PII stays in Bronze staging views sourced from bronze tables.
- `hash_pii` macro (and Python `hash_pii`) support tokenisation for non-display use cases.
- API returns display fields from Gold only; activation exports require consent-clean audience membership.

## Markets

Seed `country_market.csv` documents consent regimes per market for future row-level policies. Terraform provisions separate BigQuery datasets (`_bronze`, `_silver`, `_gold`) so IAM can restrict raw access.

## Activations

`activation_log` stores export metadata. dbt test `assert_activation_matches_audience` ensures export row counts never exceed audience sizes.
