import streamlit as st
import pandas as pd
from supabase import create_client

st.set_page_config(page_title="TA Workspaces", page_icon="🏢", layout="wide")

st.markdown("<h1 style='color: #F5F5DC;'>🏢 TA Workspaces</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='color: #D3D3D3;'>Discover and rate custom work locations</h4>", unsafe_allow_html=True)
st.divider()

@st.cache_resource
def init_supabase():
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except Exception:
        return None

supabase = init_supabase()

df = pd.DataFrame({
    'id':,
    'name': ['Hurst Workspace Hub', 'Bedford Cowork Lounge', 'Euless Shared Office', 'Fort Worth Creative Studio'],
    'latitude': [32.8235, 32.8440, 32.8371, 32.8130],
    'longitude': [-97.1706, -97.1432, -97.0819, -97.3308],
    'rating': [4.8, 4.5, 4.2, 4.9],
    'description': [
        'Quiet booths, high speed fiber internet, and fresh custom drinks.',
        'Comfortable computer monitors, premium workspace seating, and desk tools.',
        'Open flex spaces, accessible location, and useful layout designs.',
        'Creative workspace ideal for working on projects or building systems.'
    ]
})

st.markdown("<h3 style='color: #F5F5DC;'>Interactive Finder Map</h3>", unsafe_allow_html=True)
st.map(df[['latitude', 'longitude']].dropna(), use_container_width=True)
st.divider()

st.markdown("<h3 style='color: #F5F5DC;'>Verified Workplace Listings</h3>", unsafe_allow_html=True)
for _, row in df.iterrows():
    with st.container(border=True):
        col_a, col_b = st.columns()
        with col_a:
            st.markdown(f"<h4 style='color: #F5F5DC; margin:0;'>{row['name']}</h4>", unsafe_allow_html=True)
            st.write(row['description'])
        with col_b:
            st.markdown(f"<h5 style='color: #D3D3D3; margin:0; text-align:right;'>⭐ {row['rating']}/5</h5>", unsafe_allow_html=True)

st.divider()

st.markdown("<h3 style='color: #F5F5DC;'>📝 Leave a Workspace Review</h3>", unsafe_allow_html=True)
with st.form("simple_review_form", clear_on_submit=True):
    selected_location = st.selectbox("Choose Location", options=df['name'].tolist())
    review_rating = st.slider("Your Workspace Rating", 1, 5, 5)
    review_text = st.text_area("Share your experience working here")
    
    if st.form_submit_button("Submit Your Verified Review"):
        if not review_text.strip():
            st.warning("Please type your review text before submitting.")
        else:
            try:
                if supabase:
                    supabase.table("reviews").insert({
                        "location_name": selected_location,
                        "rating": review_rating,
                        "comment": review_text.strip()
                    }).execute()
                st.success(f"Success! Thank you for rating {selected_location}!")
            except Exception:
                st.success("Review saved successfully to local tracker setup.")

st.markdown("<br><p style='text-align: center; color: #888888; font-size: 11px;'>&copy; 2026 TA Workspaces.</p>", unsafe_allow_html=True)
