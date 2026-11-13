select * from {{ source('silver_python', 'int_identity_matches') }}
