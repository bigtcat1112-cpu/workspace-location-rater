import streamlit as st
import folium
from streamlit_folium import st_folium
from supabase import create_client, Client

# 1. Initialize Supabase Connection
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_supabase()

st.title("TA Workspaces - DFW Job Rater")
st.write("Explore exact job locations across DFW and rate how they treat employees!")

# 2. Interactive Map Component
st.subheader("Workspace Location Map")

# Center the map around the DFW area
m = folium.Map(location=[32.7767, -96.7970], zoom_start=10)

# Add our existing workspace marker tags
folium.Marker(
    [32.8232, -97.1739], 
    popup="Target - Hurst (Example)", 
    tooltip="Click for Info"
).add_to(m)

# Display the map on the page
st_folium(m, width=700, height=450)

st.markdown("---")

# 3. Live User Submission Form
st.subheader("Rate Your Exact Workplace Location")
st.write("Help others by posting an honest review about your specific job location.")

with st.form("review_form", clear_on_submit=True):
    workspace_name = st.text_input("Exact Location Name (e.g., Target - Hurst, TX)")
    rating = st.slider("Rating (1 = Awful, 5 = Amazing!)", 1, 5, 3)
    comment = st.text_area("Tell us about how they treat employees, hours, managers, etc.")
    
    submit_button = st.form_submit_button("Submit Rating")

# Handle database submission
if submit_button:
    if workspace_name.strip() == "":
        st.warning("Please type in a location name before submitting!")
    else:
        new_row = {
            "workspace_name": workspace_name,
            "rating": rating,
            "comment": comment
        }
        try:
            supabase.table("workspace_reviews").insert(new_row).execute()
            st.success(f"Review for '{workspace_name}' successfully added to the live database!")
        except Exception as e:
            st.error(f"Could not connect to database: {e}")
