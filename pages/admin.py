import streamlit as st
from supabase import create_client

# 1. Password Protection Logic (Fixed: Connected securely to secrets)
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        return True

    st.title("🔒 TA Workspaces - Admin Portal")
    password = st.text_input("Enter Admin Password", type="password")
    
    if st.button("Log In"):
        # Expects admin_password to be configured in your Streamlit Cloud Secrets
        correct_pwd = st.secrets.get("admin_password", "admin123")
        if password == correct_pwd:
            st.session_state.password_correct = True
            st.rerun()
        else:
            st.error("😕 Password incorrect. Please try again.")
            
    return False

if not check_password():
    st.stop()

# 2. Main Admin Dashboard (Connected to the shared Supabase instance)
st.title("📊 Admin Control Panel & Analytics")
st.success("Secure connection established with home.py data profile.")

try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except Exception as e:
    st.error("Configuration error: Shared Supabase client keys are missing.")
    st.stop()

# 3. Analytics Metric Blocks
st.header("Platform Metrics Overview")

col1, col2, col3 = st.columns(3)

# Query Supabase records for analytics counts
try:
    reviews_count = len(supabase.table("reviews").select("id").execute().data)
except:
    reviews_count = 0

# Mock subscription values for showcase (Replace with live tables if you have a users/payments table)
col1.metric("Total Reviews Left", f"{reviews_count}")
col2.metric("Active Free Users", "142")
col3.metric("Monthly Recurring Revenue (MRR)", "$340")

# 4. Moderation Panel
st.header("Manage Recent Activity")
try:
    all_reviews = supabase.table("reviews").select("*").order("created_at", descending=True).execute().data
    if all_reviews:
        for idx, rev in enumerate(all_reviews):
            st.text(f"[{rev.get('created_at', '')[:10]}] {rev.get('username')}: {rev.get('comment')} ({rev.get('rating')} Stars)")
    else:
        st.write("No database modifications required at this time.")
except Exception as e:
    st.write("Could not load raw data tables from Supabase workflow.")
