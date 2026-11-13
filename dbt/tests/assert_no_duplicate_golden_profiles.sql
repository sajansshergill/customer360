select golden_profile_id, count(*) as n
from {{ ref('int_profiles_cleaned') }}
group by 1
having count(*) > 1
