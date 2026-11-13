"""Streamlit page - reads only Gold tables from the warehouse."""
import streamlit as st
import duckdb

from config.settings import get_settings

st.title("Overview")
path = get_settings().warehouse_path
if not path.exists():
    st.warning("Warehouse not found. Run: bash scripts/run_pipeline.sh")
    st.stop()

con = duckdb.connect(str(path), read_only=True)
try:
    c = con.execute("select count(*) from gold_consumer_360").fetchone()[0]
    p = con.execute("select count(*) from gold_professional_360").fetchone()[0]
    rate = con.execute(
        "select avg(case when marketing_consent then 1.0 else 0 end) from gold_consumer_360"
    ).fetchone()[0]
    a, b, d = st.columns(3)
    a.metric("Consumer profiles", c)
    b.metric("Professional profiles", p)
    d.metric("Consent rate", f"{(rate or 0):.0%}")
    st.subheader("Audiences")
    st.dataframe(con.execute("select * from gold_audience_summary").df(), use_container_width=True)
finally:
    con.close()
