{{ config(materialized='table') }}

with as_of as (
    select coalesce(max(viewed_at), current_timestamp) as ts from {{ ref('stg_aem_content') }}
),
profiles as (
    select p.*
    from {{ ref('int_profiles_cleaned') }} p
    where {{ consent_filter('p') }}
),
whitening_views as (
    select distinct v.email
    from {{ ref('stg_aem_content') }} v, as_of
    where (
            lower(v.category) like '%whitening%'
         or lower(v.page_title) like '%whitening%'
        )
      and v.viewed_at >= as_of.ts - interval 30 day
),
email_clicks as (
    select distinct s.email
    from {{ ref('stg_sfmc_engagement') }} s, as_of
    where lower(s.event_type) in ('click', 'clicked')
      and s.event_at >= as_of.ts - interval 30 day
),
recent_oral_purchase as (
    select distinct o.email
    from {{ ref('stg_commerce_orders') }} o, as_of
    where lower(o.category) in ('oral care', 'whitening')
      and o.ordered_at >= cast(as_of.ts as date) - interval 90 day
)
select
    pr.golden_profile_id,
    pr.email
from profiles pr
inner join whitening_views w on pr.email = w.email
inner join email_clicks c on pr.email = c.email
left join recent_oral_purchase r on pr.email = r.email
where r.email is null
