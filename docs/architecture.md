# Architecture

Consumer360 implements a medallion lakehouse pattern. Source extracts land in **Bronze** (Python loaders preserving `_loaded_at` and `_source_file`). **Silver** identity and consent logic runs in Python (`int_*` tables) because graph-style resolution is awkward in pure SQL. **Gold** dimensions, facts, audiences, and KPIs are built with **dbt** on DuckDB locally (BigQuery in GCP mode).

## Runtime components

| Layer | Technology | Responsibility |
|-------|------------|----------------|
| Ingestion | Python connectors + optional Airflow | CSV → DuckDB bronze tables |
| Identity | Python (`consumer360.identity`) | Union-find on email/device → `golden_profile_id` |
| Transform | dbt 1.9 + dbt-duckdb | Staging views, gold tables, audiences |
| Quality | dbt tests + `data_quality/run_checks.py` | Uniqueness, consent, row counts |
| Serving | FastAPI + Streamlit | Query `gold_consumer_360`, audiences, activation |

Warehouse file: `data/consumer360.duckdb`. Gold physical tables are aliased to names the API expects (`gold_consumer_360`, `gold_professional_360`, `gold_audience_summary`).

## Data flow

```
sources (CSV) → bronze_* → Python silver int_* → dbt gold/audiences → API/dashboard
```

Consent is enforced in audience SQL via the `consent_filter` macro (`marketing_consent = true`), not at export time.
