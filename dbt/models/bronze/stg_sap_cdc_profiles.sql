select
    cdc_id,
    lower(trim(email)) as email,
    first_name,
    last_name,
    phone,
    date_of_birth,
    city,
    zip_code,
    cast(is_professional as boolean) as is_professional,
    nullif(trim(speciality), '') as speciality,
    cast(marketing_consent as boolean) as marketing_consent,
    cast(profiling_consent as boolean) as profiling_consent,
    cast(third_party_sharing as boolean) as third_party_sharing,
    try_cast(registered_at as date) as registered_at,
    _loaded_at,
    _source_file
from {{ source('bronze_raw', 'bronze_sap_cdc_profiles') }}
