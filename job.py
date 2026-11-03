import streamlit as st
import pandas as pd

st.set_page_config(page_title="TA Workspaces - Jobs", page_icon="💼", layout="wide")

st.markdown("<h1 style='color: #F5F5DC;'>💼 Workspace Positions Registry</h1>", unsafe_allow_html=True)
st.divider()

jobs = [
    {"title": "Workspace Assistant Coordinator", "loc": "Hurst, TX", "pay": "$15 - $18 / hr"},
    {"title": "Community Operations Host", "loc": "Bedford, TX", "pay": "$42,000 / yr"},
    {"title": "IT Lab System Technical Support", "loc": "Euless, TX", "pay": "$20 - $24 / hr"}
]

for job in jobs:
    with st.container(border=True):
        # FIXED: Added the number 2 inside st.columns() so it knows to make exactly 2 columns!
        col_j1, col_j2 = st.columns(2)
        with col_j1:
            st.markdown(f"<h4 style='color: #F5F5DC; margin:0;'>{job['title']}</h4>", unsafe_allow_html=True)
            st.caption(f"📍 Location: {job['loc']}")
        with col_j2:
            st.markdown(f"<p style='color: #D3D3D3; text-align:right; margin:0;'><b>{job['pay']}</b></p>", unsafe_allow_html=True)
            if st.button("Apply", key=job['title']):
                st.toast(f"Application manifest opened for {job['title']}!")
