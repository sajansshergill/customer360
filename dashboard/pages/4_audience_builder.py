"""Audience sizes and member preview."""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(_ROOT), str(_ROOT / "src")]

import streamlit as st
import duckdb
import yaml

from dashboard.bootstrap import ensure_warehouse
from config.settings import get_settings

st.title("Audience Builder")


@st.cache_resource
def _boot():
    return str(ensure_warehouse())


_boot()
cfg = yaml.safe_load((_ROOT / "config" / "audiences.yaml").read_text())
st.caption(cfg.get("rule", "Consent-filtered in Gold."))

path = get_settings().warehouse_path
con = duckdb.connect(str(path), read_only=True)
try:
    st.dataframe(con.execute("select * from gold_audience_summary").df(), use_container_width=True)
    aud = st.selectbox("Audience", [a["id"] for a in cfg["audiences"]])
    if aud:
        st.dataframe(con.execute(f"select * from {aud} limit 100").df(), use_container_width=True)
finally:
    con.close()
