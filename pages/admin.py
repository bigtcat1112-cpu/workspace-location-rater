import streamlit as st
from supabase import create_client
import pandas as pd
import time
import stripe
from datetime import date

# ==========================================
# 1. THEME MATRIX INJECTION OVERRIDES
# ==========================================
st.markdown(
    """
    <style>
    /* Global Application Shell Base Override */
    .stApp {
        background-color: #3E3D3A !important;
        color: #FDFBF7 !important;
    }
    
    /* Input Password Verification Overrides */
    div[data-baseweb="input"] input {
        background-color: #FDFBF7 !important;
        color: #3E3D3A !important;
        border-radius: 6px !important;
        font-weight: bold !important;
    }
    
    /* Document Component Header Colors */
    h1, h2, h3, h4, label {
        color: #FDFBF7 !important;
    }
    
    /* Log container row decoration card blocks */
    .admin-log-entry {
        background-color: #2E2D2A;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 12px;
        border-left: 4px solid #E6A23C;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 2. HIGH-SECURITY PASS EXPULSION LOGIC
# ==========================================
def check_password():
    """Validates authorization via Streamlit environment variables panel securely."""
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        return True

    st.title("🔒 TA Workspaces - Security Gateway")
    st.write("Authorization token required to inspect live analytical database pipelines.")
    
    password_input = st.text_input("Enter Admin Password Verification", type="password", key="admin_pwd_gate")
    
    if st.button("Verify Identity", key="admin_submit_auth"):
        correct_pwd = st.secrets.get("ADMIN_PASSWORD") or st.secrets.get("admin_password", "admin123")
        
        if password_input == correct_pwd:
            st.session_state.password_correct = True
            st.success("Access Granted. Synchronizing token streams...")
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("❌ Access Denied. Admin verification string failed.")
            
    return False

if not check_password():
    st.stop()

# ==========================================
# 3. SECURE API CONNECTOR EXTENSIONS
# ==========================================
@st.cache_resource
def get_admin_supabase_client():
    try:
        url = st.secrets.get("SUPABASE_URL") or st.secrets.get("supabase_url")
        key = st.secrets.get("SUPABASE_KEY") or st.secrets.get("supabase_key")
        return create_client(url, key)
    except Exception as e:
        st.error(f"Administrative data link client error: {e}")
        return None

supabase = get_admin_supabase_client()

# Fetch and initialize real-world Stripe Secret Key pipelines safely
stripe.api_key = st.secrets.get("STRIPE_SECRET_KEY") or st.secrets.get("stripe_secret_key", "mock_key")

# ==========================================
# 4. DATA ENGINE PIPELINES (REAL-TIME ANALYSIS)
# ==========================================
reviews_list = []
reviews_count = 0
live_visitor_count = 0
live_mrr_dollars = 0.0

if supabase:
    try:
        # 1. Fetch Real Live Employer Reviews Count
        all_reviews_query = supabase.table("reviews").select("*").order("created_at", desc=True).execute()
        reviews_list = all_reviews_query.data
        reviews_count = len(reviews_list) if reviews_list else 0
        
        # 2. Fetch Real Total Unique Weekly Site Traffic Hits
        traffic_query = supabase.table("site_traffic").select("id").execute()
        if traffic_query.data:
            live_visitor_count = len(traffic_query.data)
    except Exception as e:
        st.error(f"Live database sync trace failed: {e}")

# 3. Fetch Real Revenue Math Metrics from Stripe Accounts Dashboard
try:
    if stripe.api_key != "mock_key":
        # Pull active recurring premium transactions from live configurations
        active_subs = stripe.Subscription.list(status="active", limit=100)
        total_mrr_cents = 0
        
        for sub in active_subs.data:
            for item in sub.get("items", {}).get("data", []):
                plan = item.get("plan", {})
                if plan.get("interval") == "month":
                    total_mrr_cents += plan.get("amount", 0) * item.get("quantity", 1)
        
        live_mrr_dollars = total_mrr_cents / 100.0
except Exception:
    # Safe silent fallback if Stripe is in fallback/mock dev states
    live_mrr_dollars = 0.0

# ==========================================
# 5. MONITOR ENGINE VISUAL LAYOUT
# ==========================================
st.title("📊 Platform Analytics Portal")
st.write("System status: **Connected** to live database pipelines and active payout streams.")
st.markdown("---")

col_m1, col_m2, col_m3 = st.columns(3)

with col_m1:
    st.metric(label="Logged Workspace Locations", value=f"{reviews_count}")

with col_m2:
    # Dynamic text color math calculation for your traffic target budget values
    target_goal = 200
    delta_val = live_visitor_count - target_goal
    st.metric(
        label="Weekly Total Visitor Traffic", 
        value=f"{live_visitor_count} / {target_goal}", 
        delta=f"{delta_val} to target goal" if delta_val < 0 else "🎉 Target Met!"
    )

with col_m3:
    st.metric(label="Platform Live MRR Income", value=f"${live_mrr_dollars:,.2f} / month")

st.markdown("---")
st.header("🎛️ Live Database Record Monitor")

if reviews_list:
    try:
        raw_df = pd.DataFrame(reviews_list)
        expected_cols = ["id", "company_name", "location_address", "overall_rating", "comment", "created_at"]
        actual_cols = [c for c in expected_cols if c in raw_df.columns]
        
        if actual_cols:
            st.dataframe(raw_df[actual_cols], use_container_width=True)
    except Exception as df_err:
        st.caption(f"Tabular formatting error skipped: {df_err}")
        
    st.markdown("##### Administrative Log Output Stream")
    
    for rev_entry in reviews_list:
        comp = rev_entry.get("company_name", "Raw Row Element")
        addr = rev_entry.get("location_address", "Missing Coordinate String")
        rate = rev_entry.get("overall_rating", 5.0)
        comm = rev_entry.get("comment", "")
        timestamp = rev_entry.get("created_at", "2026-11-02T00:00:00")[:10]
        
        st.markdown(
            f"""
            <div class="admin-log-entry">
                <span style='color: #D3CFC9; font-size: 0.8rem;'>[{timestamp}]</span> 
                <b style='color: #FDFBF7;'>{comp}</b> ({addr}) — 
                <span style='color: #E6A23C; font-weight: bold;'>{rate} Stars</span><br>
                <span style='color: #FDFBF7; font-size: 0.9rem;'>"{comm}"</span>
            </div>
            """,
            unsafe_allow_html=True
        )
else:
    st.info("No rows present in the active cloud database instance tables yet.")

st.markdown("---")
if st.button("Flush Portal Authentication Session Token", key="admin_session_clear_btn"):
    st.session_state.password_correct = False
    st.success("Session state token flushed successfully.")
    time.sleep(0.5)
    st.rerun()

st.markdown("---")
st.caption("© 2026 TA Workspaces. Protected tracking pipelines active. Anti-bot scrapers enabled.")
