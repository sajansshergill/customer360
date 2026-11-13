{{ config(materialized='table') }}

with as_of as (
    select coalesce(max(event_at), current_timestamp) as ts from {{ ref('stg_ga4_events') }}
),
profiles as (
    select p.*
    from {{ ref('int_profiles_cleaned') }} p
    where {{ consent_filter('p') }}
      and try_cast(p.registered_at as date) >= current_date - interval 14 day
),
purchasers as (
    select distinct email from {{ ref('stg_commerce_orders') }}
),
sessions as (
    select distinct g.email
    from {{ ref('stg_ga4_events') }} g, as_of
    where g.event_name = 'session_start'
      and g.event_at >= as_of.ts - interval 7 day
      and g.email is not null
      and g.email != ''
)
select
    pr.golden_profile_id,
    pr.email
from profiles pr
inner join sessions s on pr.email = s.email
left join purchasers pu on pr.email = pu.email
where pu.email is null
