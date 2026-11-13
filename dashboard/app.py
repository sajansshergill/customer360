"""Part of the Consumer360 CDP - see README for where this file fits."""
import streamlit as st
st.set_page_config(page_title="Consumer360", layout="wide")
st.title("Consumer360 - Customer Data Platform")
st.write("Use the pages in the sidebar: Overview, Profile Explorer, Identity Graph, Audience Builder, Data Quality.")
st.info("Run the pipeline first: bash scripts/run_pipeline.sh")
