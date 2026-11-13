select * from {{ source('silver_python', 'int_profiles_cleaned') }}
