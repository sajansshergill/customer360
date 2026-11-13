{{ config(materialized='table') }}

with as_of as (
    select coalesce(max(ordered_at), current_date) as d from {{ ref('stg_commerce_orders') }}
),
profiles as (
    select p.*
    from {{ ref('int_profiles_cleaned') }} p
    where {{ consent_filter('p') }}
),
last_orders as (
    select
        o.email,
        max(o.ordered_at) as last_order_at
    from {{ ref('stg_commerce_orders') }} o
    where lower(o.category) = 'oral care'
    group by 1
),
lapsed as (
    select l.email
    from last_orders l, as_of
    where l.last_order_at <= as_of.d - interval 60 day
      and l.last_order_at >= as_of.d - interval 120 day
)
select
    pr.golden_profile_id,
    pr.email
from profiles pr
inner join lapsed la on pr.email = la.email
