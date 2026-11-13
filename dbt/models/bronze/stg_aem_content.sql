select
    content_view_id,
    lower(trim(email)) as email,
    device_id,
    page_title,
    category,
    try_cast(viewed_at as timestamp) as viewed_at,
    _loaded_at,
    _source_file
from {{ source('bronze_raw', 'bronze_aem_content') }}
