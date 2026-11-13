select a.golden_profile_id
from aud_whitening_intenders a
left join {{ ref('int_profiles_cleaned') }} p using (golden_profile_id)
where coalesce(p.marketing_consent, false) = false
union all
select a.golden_profile_id from aud_lapsed_buyers a
left join {{ ref('int_profiles_cleaned') }} p using (golden_profile_id)
where coalesce(p.marketing_consent, false) = false
