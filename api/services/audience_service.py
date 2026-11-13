"""Service layer: warehouse queries and business logic behind the API routers."""
def fetch_audiences(con):
    rows=con.execute("select audience_id, members, exported from gold_audience_summary order by 1").fetchall()
    return [{"audience_id":a,"members":m,"exported":e} for a,m,e in rows]
