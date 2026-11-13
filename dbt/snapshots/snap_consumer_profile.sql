{% snapshot snap_consumer_profile %}

{{
    config(
        target_schema='snapshots',
        unique_key='golden_profile_id',
        strategy='check',
        check_cols=['first_name', 'last_name', 'email', 'marketing_consent'],
    )
}}

select
    golden_profile_id,
    email,
    first_name,
    last_name,
    is_professional,
    marketing_consent,
    profiling_consent,
    speciality,
    registered_at
from {{ ref('int_profiles_cleaned') }}

{% endsnapshot %}
