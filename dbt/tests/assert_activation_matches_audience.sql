select l.audience_id, l.row_count, c.members
from activation_log l
inner join gold_audience_summary c using (audience_id)
where l.row_count > c.members
