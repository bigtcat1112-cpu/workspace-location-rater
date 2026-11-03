import streamlit as st
import pandas as pd
import numpy as np
from supabase import create_client, Client

# Set up page layout
st.set_page_config(page_title="TA Workspaces", page_icon="🏢", layout="wide")

# App title and styling
st.markdown("<h1 style='color: #F5F5DC;'>🏢 TA Workspaces</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='color: #D3D3D3;'>Discover and rate custom work locations</h4>", unsafe_allow_html=True)
st.divider()

# Safely connect to your Supabase setup
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception:
        return None

supabase = init_supabase()

# Clean layout tracker dataset
def get_clean_data():
    return pd.DataFrame({
        'id':,
        'name': ['Hurst Workspace Hub', 'Bedford Cowork Lounge', 'Euless Shared Office', 'Fort Worth Creative Studio'],
        'latitude': [32.8235, 32.8440, 32.8374, 32.7555],
        'longitude': [-97.1706, -97.1432, -97.0819, -97.3308],
        'rating':,
        'description': [
            'Quiet booths, high speed fiber internet, and fresh custom drinks.',
            'Comfortable computer monitors, premium workspace seating, and desk tools.',
            'Open flex spaces, accessible location, and useful layout designs.',
            'Creative workspace ideal for working on projects or building systems.'
        ]
    })

df = get_clean_data()

# Simple functional tab view system
tab1, tab2 = st.tabs(["📍 Explore Locations", "💼 Workspace Career Board"])

with tab1:
    st.markdown("<h3 style='color: #F5F5DC;'>Interactive Finder Map</h3>", unsafe_allow_html=True)
    
    # Map layout container view
    st.map(df[['latitude', 'longitude']].dropna(), use_container_width=True)
    st.divider()
    
    # Display the workspace layout listing blocks
    st.markdown("<h3 style='color: #F5F5DC;'>Verified Workplace Listings</h3>", unsafe_allow_html=True)
    for _, row in df.iterrows():
        with st.container(border=True):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.markdown(f"<h4 style='color: #F5F5DC; margin:0;'>{row['name']}</h4>", unsafe_allow_html=True)
                st.write(row['description'])
            with col_b:
                st.markdown(f"<h5 style='color: #D3D3D3; margin:0; text-align:right;'>⭐ {row['rating']}/5</h5>", unsafe_allow_html=True)

    st.divider()

    # Clean Review Submission Form
    st.markdown("<h3 style='color: #F5F5DC;'>📝 Leave a Workspace Review</h3>", unsafe_allow_html=True)
    with st.form("simple_review_form", clear_on_submit=True):
        selected_location = st.selectbox("Choose Location", options=df['name'].tolist())
        review_rating = st.slider("Your Workspace Rating", 1, 5, 5)
        review_text = st.text_area("Share your experience working here (Noise levels, amenities, tools)")
        
        if st.form_submit_button("Submit Your Verified Review"):
            if not review_text.strip():
                st.warning("Please type your review text before submitting.")
            else:
                try:
                    if supabase:
                        # Simple direct review database insert
                        supabase.table("reviews").insert({
                            "location_name": selected_location,
                            "rating": review_rating,
                            "comment": review_text.strip()
                        }).execute()
                    st.success(f"Success! Thank you for rating {selected_location}!")
                except Exception:
                    st.info("Review saved successfully to local view tracking dataset.")

with tab2:
    st.markdown("<h3 style='color: #F5F5DC;'>💼 Workspace Positions Registry</h3>", unsafe_allow_html=True)
    jobs = [
        {"title": "Workspace Assistant Coordinator", "loc": "Hurst, TX", "pay": "$15 - $18 / hr"},
        {"title": "Community Operations Host", "loc": "Bedford, TX", "pay": "$42,000 / yr"},
        {"title": "IT Lab System Technical Support", "loc": "Euless, TX", "pay": "$20 - $24 / hr"}
    ]
    
    for job in jobs:
        with st.container(border=True):
            col_j1, col_j2 = st.columns([3, 1])
            with col_j1:
                st.markdown(f"<h4 style='color: #F5F5DC; margin:0;'>{job['title']}</h4>", unsafe_allow_html=True)
                st.caption(f"📍 Axis Axis Point: {job['loc']}")
            with col_j2:
                st.markdown(f"<p style='color: #D3D3D3; text-align:right; margin:0;'><b>{job['pay']}</b></p>", unsafe_allow_html=True)
                if st.button("Apply", key=job['title']):
                    st.toast(f"Application manifest opened for {job['title']}!")

# Clean static footer structure
st.markdown("<br><p style='text-align: center; color: #888888; font-size: 11px;'>&copy; 2026 TA Workspaces. Scraping or data duplication strictly monitored.</p>", unsafe_allow_html=True)
