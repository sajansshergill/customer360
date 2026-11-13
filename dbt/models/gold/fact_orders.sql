select
    p.golden_profile_id,
    o.order_id,
    o.order_line_id,
    o.email,
    o.sku,
    o.product_name,
    o.category,
    o.quantity,
    o.unit_price,
    o.order_total,
    o.ordered_at
from {{ ref('stg_commerce_orders') }} o
inner join {{ ref('int_profiles_cleaned') }} p on o.email = p.email
