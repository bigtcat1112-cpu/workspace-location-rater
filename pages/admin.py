import streamlit as st
from supabase import create_client

# Secure admin barrier connected directly to your application workflow config
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        return True

    st.title("🔒 TA Workspaces - Security Gateway")
    password = st.text_input("Enter Admin Password Verification", type="password")
    
    if st.button("Verify Identity"):
        # Custom secure secret validator check
        correct_pwd = st.secrets.get("admin_password", "admin123")
        if password == correct_pwd:
            st.session_state.password_correct = True
            st.rerun()
        else:
            st.error("❌ Access Denied. Admin verification string failed.")
            
    return False

if not check_password():
    st.stop()

st.title("📊 Platform Analytics Portal")

# Active shared analytical dataset queries
try:
    url = "https://supabase.co"
    key = st.secrets.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ3dHw...")
    supabase = create_client(url, key)
except Exception as e:
    st.error("Analytics client connection failed.")
    st.stop()

# --- ADMINISTRATIVE INSIGHT METRICS ---
col1, col2, col3 = st.columns(3)

try:
    # Aggregates raw row analytics totals directly from your live database
    reviews_count = len(supabase.table("reviews").select("id").execute().data)
except:
    reviews_count = 0

col1.metric("Logged Workspace Locations", f"{reviews_count}")
col2.metric("Weekly Target Active Goals", "142 / 200")
col3.metric("Live Platform Subscription MRR", "$20/mo per Sub")

# --- LIVE REVIEWS MODERATION DASHBOARD ---
st.header("System Database Monitor")
try:
    all_reviews = supabase.table("reviews").select("*").order("created_at", descending=True).execute().data
    if all_reviews:
        for rev in all_reviews:
            st.markdown(
                f"**[{rev.get('company_name')}]** ({rev.get('location_address')}) — **{rev.get('rating')} Stars**  \n*{rev.get('comment')}*"
            )
            st.markdown("---")
    else:
        st.info("No logs present in the dynamic record tables yet.")
except Exception as e:
    st.error(f"Analytics table scan halted: {e}")
