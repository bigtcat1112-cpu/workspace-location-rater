import streamlit as st
from supabase import create_client, Client

# Initialize Supabase client
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_supabase()

st.title("Admin Portal - Live Data Control")

# Fetch live records from the database
try:
    response = supabase.table("workspace_reviews").select("*").eq("is_deleted", False).order("created_at", desc=True).execute()
    reviews = response.data
except Exception as e:
    st.error(f"Failed to connect to database: {e}")
    reviews = []

# Display live database metrics
st.subheader("System Metrics")
col1, col2 = st.columns(2)
col1.metric("Total Active Reviews", len(reviews))
col2.metric("Database Status", "Connected" if supabase else "Disconnected")

st.markdown("---")

# Content Moderation Tool Panel
st.subheader("Review Moderation & Clearing Desk")

if reviews:
    st.write("Click 'Delete' on any item below to immediately hide it from the public app feed.")
    for rev in reviews:
        # Lay out item details next to its moderation button
        col_text, col_btn = st.columns([4, 1])
        
        with col_text:
            st.markdown(f"**{rev['workspace_name']}** — {'⭐' * rev['rating']}")
            st.caption(f"Address: {rev.get('exact_street_address', 'None')} | ID: {rev['id']}")
        
        with col_btn:
            # Unique key assigned to each database record row button
            if st.button("🗑️ Delete", key=f"del_{rev['id']}"):
                try:
                    supabase.table("workspace_reviews").update({"is_deleted": True}).eq("id", rev['id']).execute()
                    st.success(f"Item #{rev['id']} successfully removed!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        st.markdown("---")
else:
    st.info("No active logs or reviews found in the live database table room.")
