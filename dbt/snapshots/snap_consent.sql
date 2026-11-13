{% snapshot snap_consent %}

{{
    config(
        target_schema='snapshots',
        unique_key='golden_profile_id',
        strategy='check',
        check_cols=['marketing_consent', 'profiling_consent', 'third_party_sharing'],
    )
}}

select * from {{ ref('int_consent_latest') }}

{% endsnapshot %}
