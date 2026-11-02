import streamlit as st
from supabase import create_client, Client

# Initialize Supabase client using secrets
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_supabase()

st.title("Admin Portal - Live Data Control")

# 1. Fetch live records from the database
try:
    response = supabase.table("workspace_reviews").select("*").order("created_at", desc=True).execute()
    reviews = response.data
except Exception as e:
    st.error(f"Failed to connect to database: {e}")
    reviews = []

# 2. Display live database metrics
st.subheader("System Metrics")
col1, col2 = st.columns(2)
col1.metric("Total Reviews Logged", len(reviews))
col2.metric("Database Status", "Connected" if supabase else "Disconnected")

# 3. View Data Table
st.subheader("Live Review Database Log")
if reviews:
    # This will now display all your new columns (treatment, concerns, address) in a clean spreadsheet view
    st.dataframe(reviews, use_container_width=True)
else:
    st.info("No reviews found in the live database table yet.")

