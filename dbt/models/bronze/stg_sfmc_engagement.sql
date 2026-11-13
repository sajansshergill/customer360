select
    event_id,
    subscriber_key,
    lower(trim(email)) as email,
    journey_name,
    lower(event_type) as event_type,
    try_cast(event_at as timestamp) as event_at,
    link_category,
    _loaded_at,
    _source_file
from {{ source('bronze_raw', 'bronze_sfmc_engagement') }}
