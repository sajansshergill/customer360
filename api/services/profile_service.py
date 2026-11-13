"""Service layer: warehouse queries and business logic behind the API routers."""
def fetch_profile(con, golden_id):
    row=con.execute("select golden_profile_id, first_name, last_name, email, is_professional, marketing_consent, order_count, total_spend from (select * from gold_consumer_360 union all select * from gold_professional_360) where golden_profile_id=?",[golden_id]).fetchone()
    if not row: return None
    keys=["golden_profile_id","first_name","last_name","email","is_professional","marketing_consent","order_count","total_spend"]
    return dict(zip(keys,row))
