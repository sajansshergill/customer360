{{ config(materialized='table') }}

with as_of as (
    select coalesce(max(event_at), current_timestamp) as ts from {{ ref('stg_sfmc_engagement') }}
),
profiles as (
    select p.*
    from {{ ref('int_profiles_cleaned') }} p
    where {{ consent_filter('p') }}
      and coalesce(p.is_professional, false) = true
      and lower(coalesce(p.speciality, '')) = 'orthodontics'
),
opens as (
    select
        s.email,
        count(*) as open_count
    from {{ ref('stg_sfmc_engagement') }} s, as_of
    where lower(s.event_type) in ('open', 'opened')
      and s.event_at >= as_of.ts - interval 45 day
    group by 1
    having count(*) >= 2
)
select
    pr.golden_profile_id,
    pr.email
from profiles pr
inner join opens o on pr.email = o.email
