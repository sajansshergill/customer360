{{ config(alias='gold_consumer_360', materialized='table') }}

with order_aggs as (
    select
        golden_profile_id,
        count(distinct order_id) as order_count,
        coalesce(sum(unit_price * quantity), 0) as total_spend
    from {{ ref('fact_orders') }}
    group by 1
)
select
    p.golden_profile_id,
    p.first_name,
    p.last_name,
    p.email,
    false as is_professional,
    c.marketing_consent,
    coalesce(o.order_count, 0)::integer as order_count,
    coalesce(o.total_spend, 0)::double as total_spend
from {{ ref('int_profiles_cleaned') }} p
inner join {{ ref('int_consent_latest') }} c using (golden_profile_id)
left join order_aggs o using (golden_profile_id)
where coalesce(p.is_professional, false) = false
