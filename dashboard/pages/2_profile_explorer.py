"""Streamlit page - reads only Gold tables from the warehouse."""
import streamlit as st
import duckdb

from config.settings import get_settings

st.title("Profile Explorer")
path = get_settings().warehouse_path
if not path.exists():
    st.warning("Warehouse not found. Run the pipeline first.")
    st.stop()

gid = st.text_input("Golden profile ID", "gold_p00000")
con = duckdb.connect(str(path), read_only=True)
try:
    profile = con.execute(
        """
        select * from (
          select * from gold_consumer_360
          union all
          select * from gold_professional_360
        ) where golden_profile_id = ?
        """,
        [gid],
    ).df()
    st.dataframe(profile, use_container_width=True)
    if not profile.empty:
        st.subheader("Engagement timeline")
        st.dataframe(
            con.execute(
                "select * from fact_engagement where golden_profile_id = ? order by event_at desc limit 100",
                [gid],
            ).df(),
            use_container_width=True,
        )
        st.subheader("Orders")
        st.dataframe(
            con.execute(
                "select * from fact_orders where golden_profile_id = ? order by ordered_at desc",
                [gid],
            ).df(),
            use_container_width=True,
        )
finally:
    con.close()
