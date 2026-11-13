"""Identity graph explorer."""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(_ROOT), str(_ROOT / "src")]

import streamlit as st
import duckdb

from dashboard.bootstrap import ensure_warehouse
from config.settings import get_settings

st.title("Identity Graph")
st.write(
    "CDC id + email + phone ↔ subscriber_key (SFMC) ↔ device_id (GA4/AEM). "
    "Merges use Union-Find in `src/consumer360/identity/resolver.py`."
)


@st.cache_resource
def _boot():
    return str(ensure_warehouse())


_boot()
path = get_settings().warehouse_path
gid = st.text_input("Golden profile ID", "gold_p00000")
con = duckdb.connect(str(path), read_only=True)
try:
    st.dataframe(
        con.execute(
            "select * from int_identity_graph where golden_profile_id = ? order by confidence desc",
            [gid],
        ).df(),
        use_container_width=True,
    )
    st.subheader("Match edges")
    st.dataframe(
        con.execute(
            """
            select m.*
            from int_identity_matches m
            join node_golden_map a on a.node_id = m.node_a
            where a.golden_profile_id = ?
            limit 50
            """,
            [gid],
        ).df(),
        use_container_width=True,
    )
finally:
    con.close()
