"""Streamlit page - identity graph from Silver."""
import streamlit as st
import duckdb

from config.settings import get_settings

st.title("Identity Graph")
st.write(
    "CDC id + email + phone ↔ subscriber_key (SFMC, via email) ↔ device_id "
    "(GA4/AEM, via logged-in email). Transitive merges use Union-Find."
)

path = get_settings().warehouse_path
if not path.exists():
    st.warning("Warehouse not found. Run the pipeline first.")
    st.stop()

gid = st.text_input("Golden profile ID", "gold_p00000")
con = duckdb.connect(str(path), read_only=True)
try:
    graph = con.execute(
        "select * from int_identity_graph where golden_profile_id = ? order by confidence desc",
        [gid],
    ).df()
    st.dataframe(graph, use_container_width=True)
    matches = con.execute(
        """
        select m.*
        from int_identity_matches m
        join node_golden_map a on a.node_id = m.node_a
        where a.golden_profile_id = ?
        limit 50
        """,
        [gid],
    ).df()
    st.subheader("Match edges")
    st.dataframe(matches, use_container_width=True)
finally:
    con.close()
