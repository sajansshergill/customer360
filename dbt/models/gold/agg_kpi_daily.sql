with as_of as (
    select coalesce(max(event_at), current_timestamp) as ts from {{ ref('fact_engagement') }}
)
select
    cast((select ts from as_of) as date) as metric_date,
    (select count(*) from {{ ref('int_profiles_cleaned') }}) as golden_profiles,
    (select count(*) from {{ ref('int_identity_matches') }}) as identity_edges,
    (select avg(case when marketing_consent then 1.0 else 0.0 end) from {{ ref('int_consent_latest') }}) as consent_rate,
    (select count(*) from {{ ref('fact_engagement') }}) as engagement_events
