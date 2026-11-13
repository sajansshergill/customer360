select
    event_id,
    device_id,
    user_pseudo_id,
    lower(trim(email)) as email,
    session_id,
    event_name,
    item_name,
    try_cast(event_at as timestamp) as event_at,
    _loaded_at,
    _source_file
from {{ source('bronze_raw', 'bronze_ga4_events') }}
