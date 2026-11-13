# Interview notes

## JD mapping

| Requirement | Implementation |
|-------------|----------------|
| Multi-source ingestion | Connectors + Bronze loader, Airflow DAG stubs |
| Identity / 360 | Python graph + `gold_consumer_360` / `gold_professional_360` |
| Consent-aware activation | dbt `consent_filter`, audience tests, activation log |
| Data quality | dbt tests + JSON suites in `data_quality/` |
| Cloud-ready | DuckDB local + Terraform BQ datasets, dbt `gcp` target |

## Trade-offs

- **Python Silver vs SQL Silver:** Identity graph is easier to test and iterate in Python; dbt owns business-facing Gold.
- **CSV synthetic sources:** Real SFMC/SAP credentials are unavailable; schemas match vendor documentation.
- **DuckDB local:** Fast portfolio demos; swap `profiles.yml` target for BigQuery without changing model SQL.

## Talking points

- Why consent is modelled in Gold audiences, not the Streamlit export button.
- How `golden_profile_id` stability depends on salt + anchor email (document rotation if salt changes).
- Extension path: Pub/Sub GA4 streaming, Marketing Cloud REST activation, propensity model as Gold feature.
