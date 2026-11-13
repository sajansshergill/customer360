"""Streamlit page - audience sizes and rules."""
import streamlit as st
import duckdb
import yaml
from pathlib import Path

from config.settings import get_settings

st.title("Audience Builder")
path = get_settings().warehouse_path
if not path.exists():
    st.warning("Warehouse not found. Run the pipeline first.")
    st.stop()

cfg = yaml.safe_load((Path(__file__).resolve().parents[2] / "config" / "audiences.yaml").read_text())
st.caption(cfg.get("rule", "Consent-filtered in Gold."))

con = duckdb.connect(str(path), read_only=True)
try:
    st.dataframe(con.execute("select * from gold_audience_summary").df(), use_container_width=True)
    aud = st.selectbox("Audience", [a["id"] for a in cfg["audiences"]])
    if aud:
        st.dataframe(
            con.execute(f"select * from {aud} limit 100").df(),
            use_container_width=True,
        )
finally:
    con.close()
