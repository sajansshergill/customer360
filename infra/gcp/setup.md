# GCP setup (optional)

Local development uses DuckDB at `data/consumer360.duckdb`. To run the same project against BigQuery:

1. Create a GCP project and enable BigQuery + Cloud Storage APIs.
2. `cd infra/terraform && terraform init && terraform apply -var="project_id=YOUR_PROJECT"`.
3. Create a service account with BigQuery Data Editor and Storage Object Admin; download JSON key.
4. Export:
   - `TARGET=gcp`
   - `GCP_PROJECT=YOUR_PROJECT`
   - `GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json`
5. Point `dbt/profiles.yml` output `gcp` at your datasets (`consumer360_bronze`, `_silver`, `_gold` from Terraform).

Airflow on GCP is out of scope for the minimal portfolio repo; use Cloud Composer or run `scripts/run_pipeline.sh` on a scheduler VM.
