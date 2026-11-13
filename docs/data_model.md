# Data model

## Bronze (raw)

| Table | Grain | Key columns |
|-------|-------|-------------|
| `bronze_sap_cdc_profiles` | 1 row / CDC profile | `cdc_id`, consent flags |
| `bronze_sfmc_engagement` | 1 row / email event | `event_id`, `event_type` |
| `bronze_ga4_events` | 1 row / hit | `event_id`, `session_id` |
| `bronze_aem_content` | 1 row / content view | `content_view_id` |
| `bronze_commerce_orders` | 1 row / order line | `order_line_id` |

## Silver (Python)

- `int_profiles_cleaned` — survivorship winners keyed by `golden_profile_id`
- `int_identity_matches` — pairwise identifier edges + confidence
- `int_identity_graph` — flattened identifiers → golden profile
- `int_consent_latest` — CDC consent snapshot per profile
- `int_engagement_unified` — SFMC + GA4 + AEM timeline

## Gold (dbt, API-facing aliases)

**`gold_consumer_360` / `gold_professional_360`**

| Column | Description |
|--------|-------------|
| `golden_profile_id` | Surrogate key (hashed anchor email) |
| `first_name`, `last_name`, `email` | Display attributes |
| `is_professional` | Segment flag |
| `marketing_consent` | Latest CDC marketing consent |
| `order_count`, `total_spend` | Commerce rollups |

**`gold_audience_summary`**: `audience_id`, `members`, `exported` (from `activation_log`).

Supporting facts: `fact_orders`, `fact_engagement`, `agg_kpi_daily`.

## Audiences

All members must satisfy `marketing_consent = true`. Models: `aud_whitening_intenders`, `aud_lapsed_buyers`, `aud_engaged_professionals`, `aud_new_nurturable`.
