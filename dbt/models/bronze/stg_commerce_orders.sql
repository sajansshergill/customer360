select
    order_id,
    order_line_id,
    lower(trim(email)) as email,
    sku,
    product_name,
    category,
    cast(quantity as integer) as quantity,
    cast(unit_price as double) as unit_price,
    cast(order_total as double) as order_total,
    try_cast(ordered_at as date) as ordered_at,
    _loaded_at,
    _source_file
from {{ source('bronze_raw', 'bronze_commerce_orders') }}
