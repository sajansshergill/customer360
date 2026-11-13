"""End-to-end DuckDB medallion pipeline (bronze -> silver -> gold -> audiences)."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import duckdb

from config.settings import Settings, get_settings
from consumer360.activation.activation_log import log_activation
from consumer360.activation.exporter import export_audience
from consumer360.identity.graph import build_identity_graph
from consumer360.identity.resolver import build_edges, resolve_golden_ids_with_profiles
from consumer360.identity.survivorship import apply_survivorship
from consumer360.ingestion.loader import load_all_bronze
from consumer360.utils.hashing import normalise_email
from consumer360.utils.logging import get_logger

log = get_logger(__name__)
AS_OF = date(2025, 11, 1)

AUDIENCES = [
    "aud_whitening_intenders",
    "aud_lapsed_buyers",
    "aud_engaged_professionals",
    "aud_new_nurturable",
]


def _bool_sql(col: str) -> str:
    return f"lower(cast({col} as varchar)) IN ('true', '1', 'yes')"


def build_silver_profiles(con: duckdb.DuckDBPyConnection) -> list[dict]:
    con.execute(
        """
        CREATE OR REPLACE TABLE int_profiles_cleaned AS
        SELECT
          'cdc_' || cdc_id AS node_id,
          cdc_id,
          trim(email) AS email,
          phone,
          '' AS subscriber_key,
          '' AS device_id,
          trim(first_name) || ' ' || trim(last_name) AS full_name,
          date_of_birth,
          zip_code,
          'sap_cdc' AS source_system,
          first_name,
          last_name,
          city,
          is_professional,
          speciality,
          marketing_consent,
          profiling_consent,
          third_party_sharing,
          registered_at
        FROM bronze_sap_cdc_profiles
        UNION ALL
        SELECT
          'sfmc_' || subscriber_key,
          NULL, email, '', subscriber_key, '',
          '', NULL, '', 'sfmc',
          NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL
        FROM (
          SELECT subscriber_key, email,
            row_number() OVER (PARTITION BY subscriber_key ORDER BY event_at DESC) AS rn
          FROM bronze_sfmc_engagement
        ) s WHERE rn = 1
        UNION ALL
        SELECT
          'ga4_' || device_id,
          NULL, email, '', '', device_id,
          '', NULL, '', 'ga4',
          NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL
        FROM (
          SELECT device_id,
            coalesce(max(email), '') AS email,
            row_number() OVER (PARTITION BY device_id ORDER BY max(event_at) DESC) AS rn
          FROM bronze_ga4_events
          GROUP BY device_id
        ) g WHERE rn = 1
        UNION ALL
        SELECT
          'aem_' || coalesce(nullif(trim(email), ''), device_id),
          NULL, email, '', '', device_id,
          '', NULL, '', 'aem',
          NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL
        FROM (
          SELECT email, device_id,
            row_number() OVER (
              PARTITION BY coalesce(nullif(trim(email), ''), device_id)
              ORDER BY viewed_at DESC
            ) AS rn
          FROM bronze_aem_content
        ) a WHERE rn = 1 AND coalesce(nullif(trim(email), ''), device_id) IS NOT NULL
        """
    )
    desc = con.execute("SELECT * FROM int_profiles_cleaned LIMIT 0").description
    cols = [d[0] for d in desc]
    rows = con.execute("SELECT * FROM int_profiles_cleaned").fetchall()
    return [dict(zip(cols, r)) for r in rows]


def build_identity_tables(con: duckdb.DuckDBPyConnection, profiles: list[dict]) -> None:
    edges = build_edges(profiles)
    golden_map = resolve_golden_ids_with_profiles(edges, profiles)
    graph = build_identity_graph(profiles, golden_map)

    con.execute(
        """
        CREATE OR REPLACE TABLE int_identity_matches (
          node_a VARCHAR, node_b VARCHAR, match_type VARCHAR, confidence DOUBLE
        )
        """
    )
    if edges:
        con.executemany(
            "INSERT INTO int_identity_matches VALUES (?, ?, ?, ?)",
            [(e["node_a"], e["node_b"], e["match_type"], e["confidence"]) for e in edges],
        )

    con.execute(
        """
        CREATE OR REPLACE TABLE int_identity_graph (
          golden_profile_id VARCHAR,
          identifier_type VARCHAR,
          identifier_value VARCHAR,
          source_system VARCHAR,
          confidence DOUBLE
        )
        """
    )
    if graph:
        con.executemany(
            "INSERT INTO int_identity_graph VALUES (?, ?, ?, ?, ?)",
            [
                (
                    g["golden_profile_id"],
                    g["identifier_type"],
                    g["identifier_value"],
                    g["source_system"],
                    g["confidence"],
                )
                for g in graph
            ],
        )

    by_golden: dict[str, list[dict]] = defaultdict(list)
    for p in profiles:
        gid = golden_map.get(p["node_id"])
        if gid:
            by_golden[gid].append(p)

    consent_rows = []
    for gid, cluster in by_golden.items():
        surv = apply_survivorship(cluster)
        consent_rows.append(
            (
                gid,
                surv["marketing_consent"],
                surv["profiling_consent"],
                surv["third_party_sharing"],
                surv["registered_at"],
            )
        )

    con.execute(
        """
        CREATE OR REPLACE TABLE int_consent_latest (
          golden_profile_id VARCHAR PRIMARY KEY,
          marketing_consent BOOLEAN,
          profiling_consent BOOLEAN,
          third_party_sharing BOOLEAN,
          registered_at VARCHAR
        )
        """
    )
    if consent_rows:
        con.executemany(
            "INSERT INTO int_consent_latest VALUES (?, ?, ?, ?, ?)",
            consent_rows,
        )

    con.execute(
        """
        CREATE OR REPLACE TABLE node_golden_map (node_id VARCHAR, golden_profile_id VARCHAR)
        """
    )
    if golden_map:
        con.executemany(
            "INSERT INTO node_golden_map VALUES (?, ?)",
            list(golden_map.items()),
        )


def build_engagement_unified(con: duckdb.DuckDBPyConnection) -> None:
    con.execute(
        """
        CREATE OR REPLACE TABLE int_engagement_unified AS
        SELECT
          coalesce(m.golden_profile_id, 'gold_unknown') AS golden_profile_id,
          'sfmc' AS channel,
          event_type,
          event_at,
          journey_name,
          link_category,
          email
        FROM bronze_sfmc_engagement e
        LEFT JOIN node_golden_map m ON m.node_id = 'sfmc_' || e.subscriber_key
        UNION ALL
        SELECT
          coalesce(m.golden_profile_id, 'gold_unknown'),
          'ga4',
          event_name,
          event_at,
          session_id,
          item_name,
          email
        FROM bronze_ga4_events g
        LEFT JOIN node_golden_map m ON m.node_id = 'ga4_' || g.device_id
        UNION ALL
        SELECT
          coalesce(m.golden_profile_id, 'gold_unknown'),
          'aem',
          'content_view',
          viewed_at,
          page_title,
          category,
          email
        FROM bronze_aem_content a
        LEFT JOIN node_golden_map m
          ON m.node_id = 'aem_' || coalesce(nullif(trim(a.email), ''), a.device_id)
        """
    )


def build_gold(con: duckdb.DuckDBPyConnection) -> None:
    con.execute(
        """
        CREATE OR REPLACE TABLE gold_dims AS
        WITH cdc AS (
          SELECT c.*, m.golden_profile_id
          FROM bronze_sap_cdc_profiles c
          JOIN node_golden_map m ON m.node_id = 'cdc_' || c.cdc_id
        ),
        subs AS (
          SELECT m.golden_profile_id, max(e.subscriber_key) AS subscriber_key
          FROM bronze_sfmc_engagement e
          JOIN node_golden_map m ON m.node_id = 'sfmc_' || e.subscriber_key
          GROUP BY 1
        ),
        orders AS (
          SELECT
            m.golden_profile_id,
            count(*) AS order_count,
            sum(try_cast(o.order_total AS DOUBLE)) AS total_spend
          FROM bronze_commerce_orders o
          JOIN node_golden_map m ON m.node_id = 'aem_' || trim(o.email)
          GROUP BY 1
        )
        SELECT
          c.golden_profile_id,
          cl.marketing_consent,
          cl.registered_at,
          trim(c.first_name) AS first_name,
          trim(c.last_name) AS last_name,
          trim(c.email) AS email,
          CASE WHEN """ + _bool_sql("c.is_professional") + """ THEN true ELSE false END AS is_professional,
          coalesce(c.speciality, '') AS speciality,
          coalesce(s.subscriber_key, '') AS subscriber_key,
          coalesce(o.order_count, 0) AS order_count,
          coalesce(o.total_spend, 0) AS total_spend
        FROM cdc c
        JOIN int_consent_latest cl ON cl.golden_profile_id = c.golden_profile_id
        LEFT JOIN subs s ON s.golden_profile_id = c.golden_profile_id
        LEFT JOIN orders o ON o.golden_profile_id = c.golden_profile_id
        """
    )

    con.execute(
        """
        CREATE OR REPLACE TABLE gold_consumer_360 AS
        SELECT * FROM gold_dims WHERE coalesce(is_professional, false) = false
        """
    )
    con.execute(
        """
        CREATE OR REPLACE TABLE gold_professional_360 AS
        SELECT * FROM gold_dims WHERE coalesce(is_professional, false) = true
        """
    )

    con.execute(
        """
        CREATE OR REPLACE TABLE fact_engagement AS
        SELECT * FROM int_engagement_unified
        WHERE golden_profile_id != 'gold_unknown'
        """
    )
    con.execute(
        """
        CREATE OR REPLACE TABLE fact_orders AS
        SELECT
          coalesce(g.golden_profile_id, 'gold_unknown') AS golden_profile_id,
          o.*
        FROM bronze_commerce_orders o
        LEFT JOIN gold_dims g ON lower(trim(o.email)) = lower(trim(g.email))
        """
    )
    con.execute(
        """
        CREATE OR REPLACE TABLE agg_kpi_daily AS
        SELECT
          cast(event_at AS date) AS kpi_date,
          channel,
          count(*) AS events
        FROM fact_engagement
        GROUP BY 1, 2
        """
    )


def build_audiences(con: duckdb.DuckDBPyConnection) -> None:
    as_of = AS_OF.isoformat()
    con.execute(
        f"""
        CREATE OR REPLACE TABLE aud_whitening_intenders AS
        SELECT DISTINCT g.golden_profile_id
        FROM gold_dims g
        JOIN int_consent_latest c ON c.golden_profile_id = g.golden_profile_id
        WHERE c.marketing_consent = true
          AND EXISTS (
            SELECT 1 FROM bronze_aem_content a
            JOIN node_golden_map m ON m.node_id = 'aem_' || coalesce(nullif(trim(a.email), ''), a.device_id)
            WHERE m.golden_profile_id = g.golden_profile_id
              AND a.category = 'Whitening'
              AND cast(a.viewed_at AS timestamp) >= timestamp '{as_of}' - interval '30 days'
          )
          AND EXISTS (
            SELECT 1 FROM bronze_sfmc_engagement s
            JOIN node_golden_map m ON m.node_id = 'sfmc_' || s.subscriber_key
            WHERE m.golden_profile_id = g.golden_profile_id
              AND s.event_type = 'click'
              AND cast(s.event_at AS timestamp) >= timestamp '{as_of}' - interval '30 days'
          )
          AND NOT EXISTS (
            SELECT 1 FROM bronze_commerce_orders o
            WHERE lower(trim(o.email)) = lower(trim(g.email))
              AND (
                o.category = 'Oral Care'
                OR lower(o.product_name) LIKE '%whitening%'
              )
              AND cast(o.ordered_at AS timestamp) >= timestamp '{as_of}' - interval '90 days'
          )
        """
    )

    con.execute(
        f"""
        CREATE OR REPLACE TABLE aud_lapsed_buyers AS
        SELECT DISTINCT g.golden_profile_id
        FROM gold_dims g
        JOIN int_consent_latest c ON c.golden_profile_id = g.golden_profile_id
        WHERE c.marketing_consent = true
          AND EXISTS (
            SELECT 1 FROM bronze_commerce_orders o
            WHERE lower(trim(o.email)) = lower(trim(g.email))
              AND o.category = 'Oral Care'
              AND cast(o.ordered_at AS timestamp)
                BETWEEN timestamp '{as_of}' - interval '120 days'
                AND timestamp '{as_of}' - interval '60 days'
          )
          AND NOT EXISTS (
            SELECT 1 FROM bronze_commerce_orders o2
            WHERE lower(trim(o2.email)) = lower(trim(g.email))
              AND cast(o2.ordered_at AS timestamp) > timestamp '{as_of}' - interval '60 days'
          )
        """
    )

    con.execute(
        f"""
        CREATE OR REPLACE TABLE aud_engaged_professionals AS
        SELECT g.golden_profile_id
        FROM gold_professional_360 g
        JOIN int_consent_latest c ON c.golden_profile_id = g.golden_profile_id
        WHERE c.marketing_consent = true
          AND g.speciality = 'Orthodontics'
        GROUP BY g.golden_profile_id
        HAVING (
          SELECT count(*)
          FROM bronze_sfmc_engagement s
          JOIN node_golden_map m ON m.node_id = 'sfmc_' || s.subscriber_key
          WHERE m.golden_profile_id = g.golden_profile_id
            AND s.event_type = 'open'
            AND cast(s.event_at AS timestamp) >= timestamp '{as_of}' - interval '45 days'
        ) >= 2
        """
    )

    con.execute(
        f"""
        CREATE OR REPLACE TABLE aud_new_nurturable AS
        SELECT DISTINCT g.golden_profile_id
        FROM gold_dims g
        JOIN int_consent_latest c ON c.golden_profile_id = g.golden_profile_id
        WHERE c.marketing_consent = true
          AND cast(c.registered_at AS date) >= date '{as_of}' - interval '14 days'
          AND coalesce(g.order_count, 0) = 0
          AND EXISTS (
            SELECT 1 FROM bronze_ga4_events e
            JOIN node_golden_map m ON m.node_id = 'ga4_' || e.device_id
            WHERE m.golden_profile_id = g.golden_profile_id
              AND cast(e.event_at AS timestamp) >= timestamp '{as_of}' - interval '7 days'
          )
        """
    )

    summary = []
    for aud in AUDIENCES:
        members = con.execute(f"SELECT count(*) FROM {aud}").fetchone()[0]
        summary.append((aud, members, members))
    con.execute(
        """
        CREATE OR REPLACE TABLE gold_audience_summary (
          audience_id VARCHAR,
          members INTEGER,
          exported INTEGER
        )
        """
    )
    con.executemany("INSERT INTO gold_audience_summary VALUES (?, ?, ?)", summary)


def fix_order_golden_join(con: duckdb.DuckDBPyConnection) -> None:
    """Rebuild gold_dims orders join using CDC email mapping."""
    con.execute(
        """
        CREATE OR REPLACE TABLE gold_dims AS
        WITH cdc AS (
          SELECT c.*, m.golden_profile_id
          FROM bronze_sap_cdc_profiles c
          JOIN node_golden_map m ON m.node_id = 'cdc_' || c.cdc_id
        ),
        email_map AS (
          SELECT DISTINCT golden_profile_id, trim(email) AS email FROM cdc
        ),
        subs AS (
          SELECT m.golden_profile_id, max(e.subscriber_key) AS subscriber_key
          FROM bronze_sfmc_engagement e
          JOIN node_golden_map m ON m.node_id = 'sfmc_' || e.subscriber_key
          GROUP BY 1
        ),
        orders AS (
          SELECT
            em.golden_profile_id,
            count(*) AS order_count,
            sum(try_cast(o.order_total AS DOUBLE)) AS total_spend
          FROM bronze_commerce_orders o
          JOIN email_map em ON lower(trim(o.email)) = lower(em.email)
          GROUP BY 1
        )
        SELECT
          c.golden_profile_id,
          cl.marketing_consent,
          cl.registered_at,
          trim(c.first_name) AS first_name,
          trim(c.last_name) AS last_name,
          trim(c.email) AS email,
          CASE WHEN """ + _bool_sql("c.is_professional") + """ THEN true ELSE false END AS is_professional,
          coalesce(c.speciality, '') AS speciality,
          coalesce(s.subscriber_key, '') AS subscriber_key,
          coalesce(o.order_count, 0) AS order_count,
          coalesce(o.total_spend, 0) AS total_spend
        FROM cdc c
        JOIN int_consent_latest cl ON cl.golden_profile_id = c.golden_profile_id
        LEFT JOIN subs s ON s.golden_profile_id = c.golden_profile_id
        LEFT JOIN orders o ON o.golden_profile_id = c.golden_profile_id
        """
    )
    con.execute(
        "CREATE OR REPLACE TABLE gold_consumer_360 AS "
        "SELECT * FROM gold_dims WHERE coalesce(is_professional, false) = false"
    )
    con.execute(
        "CREATE OR REPLACE TABLE gold_professional_360 AS "
        "SELECT * FROM gold_dims WHERE coalesce(is_professional, false) = true"
    )


def run_pipeline(settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    settings.activation_dir.mkdir(parents=True, exist_ok=True)
    load_all_bronze(settings)
    con = duckdb.connect(str(settings.warehouse_path))
    try:
        profiles = build_silver_profiles(con)
        build_identity_tables(con, profiles)
        con.execute(
            """
            CREATE OR REPLACE TABLE int_profiles_cleaned AS
            SELECT
              m.golden_profile_id,
              c.cdc_id,
              trim(c.email) AS email,
              trim(c.first_name) AS first_name,
              trim(c.last_name) AS last_name,
              c.phone,
              c.date_of_birth,
              c.city,
              c.zip_code,
              CASE WHEN """ + _bool_sql("c.is_professional") + """ THEN true ELSE false END AS is_professional,
              nullif(trim(c.speciality), '') AS speciality,
              CASE WHEN """ + _bool_sql("c.marketing_consent") + """ THEN true ELSE false END AS marketing_consent,
              CASE WHEN """ + _bool_sql("c.profiling_consent") + """ THEN true ELSE false END AS profiling_consent,
              CASE WHEN """ + _bool_sql("c.third_party_sharing") + """ THEN true ELSE false END AS third_party_sharing,
              c.registered_at
            FROM bronze_sap_cdc_profiles c
            JOIN node_golden_map m ON m.node_id = 'cdc_' || c.cdc_id
            """
        )
        build_engagement_unified(con)
        build_gold(con)
        fix_order_golden_join(con)
        build_audiences(con)
        for aud in AUDIENCES:
            path = export_audience(con, aud, settings.activation_dir)
            with path.open() as f:
                n = max(sum(1 for _ in f) - 1, 0)
            log_activation(con, aud, n, path)
        log.info("Pipeline complete: %s golden profiles", con.execute("SELECT count(*) FROM node_golden_map").fetchone()[0])
    finally:
        con.close()


def main() -> None:
    run_pipeline()


if __name__ == "__main__":
    main()
