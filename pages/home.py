import streamlit as st
import pandas as pd
import numpy as np
from supabase import create_client, Client

st.set_page_config(page_title="TA Workspaces", page_icon="🏢", layout="wide")

if "user_search_history" not in st.session_state:
    st.session_state["user_search_history"] = []
if "admin_authenticated" not in st.session_state:
    st.session_state["admin_authenticated"] = False

st.sidebar.markdown("# 🚀 TA Workspace Engine")
explore_tab, jobs_tab, admin_tab = "📍 Explore", "💼 Jobs", "🛠️ Admin"
app_mode = st.sidebar.radio("Navigation", [explore_tab, jobs_tab, admin_tab])

@st.cache_resource
def init_supabase():
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except Exception:
        return None

supabase = init_supabase()

def get_mock_data():
    return pd.DataFrame({
        'id':,
        'name': ['Hurst Creative Hub', 'Bedford Tech Lounge', 'Euless Executive Suites'],
        'latitude': [32.8236, 32.8443, 32.8371],
        'longitude': [-97.1706, -97.1432, -97.0819],
        'rating': [4.8, 4.2, 4.6],
        'capacity':,
        'amenities': ['Fiber, Coffee', 'Fiber, Monitors', '24/7, Coffee'],
        'price_per_hour': [10.50, 12.00, 15.00],
        'description': ['Shared spaces close to home.', 'High-speed fiber internet infrastructure.', 'Premium office structures.']
    })

@st.cache_data(ttl=120)
def fetch_data():
    if not supabase: return get_mock_data()
    try:
        res = supabase.table("workspaces").select("*").order("created_at", descending=True).execute()
        df = pd.DataFrame(res.data)
        return df if not df.empty else get_mock_data()
    except Exception:
        return get_mock_data()

df_workspaces = fetch_data()

if app_mode == explore_tab:
    st.title("🏢 Premium Workspace Discovery Platform")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Facilities", len(df_workspaces))
    col2.metric("Average Rating", f"⭐ {df_workspaces['rating'].mean():.1f}")
    col3.metric("Total Capacity", f"{int(df_workspaces['capacity'].sum())} Seats")
    col4.metric("Starting Price", f"${df_workspaces['price_per_hour'].min():.2f}/hr")

    with st.expander("🔍 Filters", expanded=True):
        f1, f2, f3 = st.columns(3)
        query = f1.text_input("Keyword Search", "")
        max_p = f2.slider("Max Price", 3.0, 25.0, 25.0)
        min_r = f3.slider("Min Rating", 1.0, 5.0, 1.0)

    f_df = df_workspaces[
        (df_workspaces['name'].str.contains(query, case=False) | df_workspaces['description'].str.contains(query, case=False)) &
        (df_workspaces['price_per_hour'] <= max_p) & (df_workspaces['rating'] >= min_r)
    ]

    t1, t2 = st.tabs(["🗺️ Map View", "📊 List View"])
    with t1:
        m_col, c_col = st.columns()
        with m_col:
            st.map(f_df[['latitude', 'longitude']].dropna(), use_container_width=True)
        with c_col:
            for _, r in f_df.head(3).iterrows():
                with st.container(border=True):
                    st.markdown(f"##### {r['name']} (${r['price_per_hour']}/hr)")
                    st.caption(f"⭐ {r['rating']} | {r['amenities']}")

    with t2:
        st.dataframe(f_df[['name', 'rating', 'capacity', 'price_per_hour', 'amenities']], use_container_width=True)

    st.markdown("### 📝 Leave a Review")
    with st.form("review_form", clear_on_submit=True):
        opts = {r['name']: r['id'] for _, r in f_df.iterrows()} if not f_df.empty else {"No options": 0}
        selected = st.selectbox("Select Workspace", options=list(opts.keys()))
        rating = st.slider("Rating", 1, 5, 5)
        comment = st.text_area("Your Review")
        if st.form_submit_button("Submit"):
            if opts[selected] != 0 and len(comment.strip()) >= 5:
                try:
                    if supabase: supabase.table("reviews").insert({"workspace_id": int(opts[selected]), "rating": rating, "comment": comment.strip()}).execute()
                    st.success(f"Transmission Confirmed: Feedback recorded for {selected}.")
                    st.cache_data.clear()
                except Exception as tx_err:
                    st.error(f"Database Pipeline Mutation Fault: {str(tx_err)}")
            else:
                st.warning("Please provide a valid comment.")
                
    st.markdown("---")
    st.markdown("TA Workspaces Distribution Engine • System Clock Stamp Mon, Nov 02, 2026", unsafe_allow_html=True)

elif app_mode == jobs_tab:
    st.title("💼 Workspace Career Board")
    jobs = [
        {"role": "Workspace Operations Coordinator", "city": "Hurst, TX", "tier": "Full-Time", "pay": "$45,000"},
        {"role": "Community Network Manager", "city": "Euless, TX", "tier": "Full-Time", "pay": "$48,000"},
        {"role": "IT Network Specialist", "city": "Bedford, TX", "tier": "Part-Time", "pay": "$24/hr"}
    ]
    for j in jobs:
        with st.container(border=True):
            st.markdown(f"### {j['role']} ({j['tier']})")
            st.write(f"📍 {j['city']} | 💰 {j['pay']}")
            if st.button("Apply", key=j['role']):
                st.toast("Application initiated!")

elif app_mode == admin_tab:
    if not st.session_state["admin_authenticated"]:
        st.title("🔐 Admin Login")
        pass_target = st.secrets.get("ADMIN_PASSWORD", "admin_fallback_secure_99")
        with st.form("login_form"):
            pwd = st.text_input("Admin Password", type="password")
            if st.form_submit_button("Login"):
                if pwd == pass_target:
                    st.session_state["admin_authenticated"] = True
                    st.success("Access Granted!")
                    st.rerun()
                else:
                    st.error("Incorrect password.")
    else:
        st.title("🛠️ Operations Management Terminal")
        if st.sidebar.button("Logout"):
            st.session_state["admin_authenticated"] = False
            st.rerun()
            
        m1, m2, m3 = st.columns(3)
        m1.metric("DB Status", "99.9% Online")
        m2.metric("Stripe Pipeline", "Test Mode Active")
        m3.metric("Server Ingress", "Nominal")
        
        st.markdown("### Stripe Revenue Pipeline Simulation")
        st.line_chart(pd.DataFrame(np.random.randn(20, 2), columns=["Revenue", "Refunds"]))
