{{ config(alias='gold_audience_summary', materialized='table') }}

{% set audiences = [
    ('aud_whitening_intenders', ref('aud_whitening_intenders')),
    ('aud_lapsed_buyers', ref('aud_lapsed_buyers')),
    ('aud_engaged_professionals', ref('aud_engaged_professionals')),
    ('aud_new_nurturable', ref('aud_new_nurturable')),
] %}

with counts as (
    {% for aid, model in audiences %}
    select '{{ aid }}' as audience_id, count(*)::bigint as members from {{ model }}
    {% if not loop.last %}union all{% endif %}
    {% endfor %}
),
exported as (
    select audience_id, max(row_count)::bigint as exported
    from activation_log
    group by 1
)
select
    c.audience_id,
    c.members,
    coalesce(e.exported, 0)::bigint as exported
from counts c
left join exported e using (audience_id)
