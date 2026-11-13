select
    golden_profile_id,
    channel,
    event_type,
    journey_name,
    link_category,
    event_at,
    source_event_id
from {{ ref('int_engagement_unified') }}
