import streamlit as st
from supabase import create_client

# --- CUSTOM DARK THEME MATCH ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #3E3D3A; 
        color: #FDFBF7; 
    }
    div[data-baseweb="input"] input {
        background-color: #FDFBF7 !important; 
        color: #3E3D3A !important;
    }
    h1, h2, h3, h4, label {
        color: #FDFBF7 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Secure admin barrier connected directly to your application workflow config
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        return True

    st.title("🔒 TA Workspaces - Security Gateway")
    password = st.text_input("Enter Admin Password Verification", type="password")
    
    if st.button("Verify Identity"):
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
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except Exception as e:
    st.error("Analytics client connection failed.")
    st.stop()

# --- ADMINISTRATIVE INSIGHT METRICS ---
col1, col2, col3 = st.columns(3)

try:
    reviews_count = len(supabase.table("reviews").select("id").execute().data)
except:
    reviews_count = 0

col1.metric("Logged Workspace Locations", f"{reviews_count}")
col2.metric("Weekly Target Active Goals", "142 / 200")
col3.metric("Live Platform Subscription MRR", "$20/mo per Sub")

# --- LIVE REVIEWS MODERATION DASHBOARD ---
st.header("System Database Monitor")
try:
    # FIXED: Changed descending=True to desc=True
    all_reviews = supabase.table("reviews").select("*").order("created_at", desc=True).execute().data
    if all_reviews:
        for rev in all_reviews:
            st.markdown(
                f"""
                <div style='background-color: #2E2D2A; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 5px solid #D3CFC9;'>
                    <strong style='color: #FDFBF7;'>🏢 {rev.get('company_name')}</strong> ({rev.get('location_address')}) — <span style='color: #E6A23C;'>{rev.get('overall_rating')} Stars</span><br>
                    <p style='margin-top: 5px; color: #FDFBF7;'>"{rev.get('comment')}"</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
    else:
        st.info("No logs present in the dynamic record tables yet.")
except Exception as e:
    st.error(f"Analytics table scan halted: {e}")
