"""Consumer360 Streamlit entrypoint — works locally and on Streamlit Community Cloud."""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(_ROOT), str(_ROOT / "src")]

import streamlit as st

from dashboard.bootstrap import ensure_warehouse

st.set_page_config(page_title="Consumer360", layout="wide", page_icon="◉")

st.title("Consumer360")
st.caption("Customer Data Platform — profiles, identity, audiences, and activation.")


@st.cache_resource(show_spinner="Building warehouse (first run only)…")
def _boot():
    return str(ensure_warehouse(profiles=300))


warehouse = _boot()
st.success(f"Warehouse ready: `{warehouse}`")
st.write(
    "Use the sidebar pages: **Overview**, **Profile Explorer**, **Identity Graph**, "
    "**Audience Builder**, **Data Quality**."
)
