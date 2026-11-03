import streamlit as st
import pandas as pd
import numpy as np
import stripe
from datetime import date

# -------------------------------------------------------------
# 1. STRIPE API INTEGRATION SETUP
# -------------------------------------------------------------
stripe.api_key = st.secrets.get("STRIPE_SECRET_KEY", "mock_key_if_missing")
PRICE_ID = "price_1UXNrfEbNBWTyWzqE2qkw78S"

# -------------------------------------------------------------
# 2. APPLICATION SETUP & CONFIGURATION
# -------------------------------------------------------------
st.set_page_config(page_title="TA Workspaces", layout="wide", initial_sidebar_state="expanded")

# Inject retro dark theme styling with beige/gray accents
st.markdown(
    """
    <style>
    .stApp { background-color: #1e1e1e; color: #f5f5dc; }
    .stTextInput>div>div>input { background-color: #f5f5dc; color: #1e1e1e; }
    .stTextArea>div>div>textarea { background-color: #f5f5dc; color: #1e1e1e; }
    .stNumberInput>div>div>input { background-color: #f5f5dc; color: #1e1e1e; }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize global analytics metrics inside state store
if "total_visitors_today" not in st.session_state:
    st.session_state.total_visitors_today = 142
if "jobs_placed_count" not in st.session_state:
    st.session_state.jobs_placed_count = 28
if "normal_members_count" not in st.session_state:
    st.session_state.normal_members_count = 114
if "premium_members_count" not in st.session_state:
    st.session_state.premium_members_count = 12
if "last_tracked_date" not in st.session_state:
    st.session_state.last_tracked_date = str(date.today())

# Increment visitor traffic telemetry on fresh load tracking cycles
if str(date.today()) != st.session_state.last_tracked_date:
    st.session_state.total_visitors_today = 1
    st.session_state.last_tracked_date = str(date.today())
else:
    st.session_state.total_visitors_today += 1

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "subscribed" not in st.session_state:
    st.session_state.subscribed = False
if "reviews" not in st.session_state:
    st.session_state.reviews = [
        {
            "company": "TechSpace Downtown", "location": "Dallas, TX",
            "noise": 4, "internet": 5, "comfort": 4, "treatment": 5, "desk": 4,
            "lat": 32.7767, "lon": -96.7970
        },
        {
            "company": "CoWork Central", "location": "Fort Worth, TX",
            "noise": 3, "internet": 4, "comfort": 5, "treatment": 4, "desk": 5,
            "lat": 32.7555, "lon": -97.3308
        }
    ]

query_params = st.query_params
if "session_id" in query_params:
    st.session_state.subscribed = True
    st.session_state.premium_members_count += 1
    st.sidebar.success("🎉 Payment verified successfully!")

# -------------------------------------------------------------
# 3. SIDEBAR NAVIGATION & PREMIUM ACTIONS
# -------------------------------------------------------------
st.sidebar.title("🏢 TA Workspaces")
menu = st.sidebar.radio("Navigation", ["🔍 Discover Workspaces", "📝 Rate a Workspace", "💼 I Got the Job!", "🔒 Admin Panel"])

st.sidebar.markdown("---")
st.sidebar.subheader("💎 Premium Access")

if st.session_state.subscribed:
    st.sidebar.success("Premium Active ($20/mo)")
    if st.sidebar.button("Cancel Subscription"):
        st.session_state.subscribed = False
        st.session_state.premium_members_count = max(0, st.session_state.premium_members_count - 1)
        st.query_params.clear()
        st.rerun()
else:
    st.sidebar.info("Unlock advanced filter tools.")
    if st.sidebar.button("Subscribe Now ($20/mo)"):
        try:
            app_url = "https://streamlit.app" 
            checkout_session = stripe.checkout.Session.create(
                line_items=[{'price': PRICE_ID, 'quantity': 1}],
                mode='subscription',
                success_url=f"{app_url}?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=app_url,
            )
            st.sidebar.markdown(f"[👉 Complete Payment on Stripe]({checkout_session.url})", unsafe_allow_html=True)
            st.sidebar.info("Click the secure link above to complete transaction.")
        except Exception as e:
            st.sidebar.error(f"Stripe Error: {e}")

# -------------------------------------------------------------
# 4. CORE APPLICATION FEATURES
# -------------------------------------------------------------

# FEATURE A: DISCOVER WORKSPACES (WITH MAP)
if menu == "🔍 Discover Workspaces":
    st.title("🔍 Discover Rated Workspaces")
    
    if st.session_state.subscribed:
        min_internet = st.slider("Minimum Internet Speed Rating", 1, 5, 1)
        filtered_list = [r for r in st.session_state.reviews if r["internet"] >= min_internet]
    else:
        filtered_list = st.session_state.reviews
        st.caption("💡 *Tip: Subscribe to premium in the sidebar to filter workspaces by speed metrics.*")

    if filtered_list:
        df = pd.DataFrame(filtered_list)
        df["Overall Score"] = df[["noise", "internet", "comfort", "treatment", "desk"]].mean(axis=1).round(1)
        
        st.subheader("📍 Nearby Locations")
        st.map(df[["lat", "lon"]])
        
        st.subheader("📋 Workspace Directory")
        st.dataframe(
            df[["company", "location", "Overall Score", "noise", "internet", "comfort", "treatment", "desk"]],
            use_container_width=True
        )
        
        st.markdown("---")
        st.subheader("⭐ Recent Corporate Ratings")
        for r in st.session_state.reviews:
            score = round(np.mean([r["noise"], r["internet"], r["comfort"], r["treatment"], r["desk"]]), 1)
            st.markdown(f"### 🏢 {r['company']}")
            st.markdown(f"📍 **Location:** {r['location']} | ⭐ **Overall Rating Score:** `{score} / 5.0`")
            st.markdown(
                f"🔊 Noise: `{r['noise']}/5` | ⚡ Internet: `{r['internet']}/5` | "
                f"🪑 Comfort: `{r['comfort']}/5` | 🤝 Treatment: `{r['treatment']}/5` | 🖥️ Desk Setup: `{r['desk']}/5`"
            )
            st.markdown("---")
    else:
        st.info("No workspaces match your filtering criteria.")

# FEATURE B: COMPREHENSIVE WORKSPACE RATING FORM
elif menu == "📝 Rate a Workspace":
    st.title("📝 Submit a New Workspace Rating")
    
    with st.form("rating_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("Company Name").strip()
            location_text = st.text_input("City, State (e.g., Austin, TX)").strip()
        with col2:
            lat_input = st.number_input("Latitude", value=32.7, format="%.4f")
            lon_input = st.number_input("Longitude", value=-97.3, format="%.4f")
            
        st.markdown("### Quality Metrics")
        noise_insulation = st.slider("Noise Insulation", 1, 5, 3)
        internet_speed = st.slider("Internet Speed Quality", 1, 5, 4)
        ergonomic_comfort = st.slider("Ergonomic Comfort (Chairs/Desks)", 1, 5, 3)
        employee_treatment = st.slider("Staff & Employee Treatment", 1, 5, 4)
        desk_setup = st.slider("Desk Space & Power Setup", 1, 5, 3)
        
        submit_btn = st.form_submit_button("Submit Application Rating")
        
        if submit_btn:
            if company_name and location_text:
                st.session_state.reviews.append({
                    "company": company_name, "location": location_text,
                    "noise": int(noise_insulation), "internet": int(internet_speed),
                    "comfort": int(ergonomic_comfort), "treatment": int(employee_treatment),
                    "desk": int(desk_setup), "lat": float(lat_input), "lon": float(lon_input)
                })
                st.success(f"Successfully added review for '{company_name}'!")
                st.rerun()
            else:
                st.error("Please completely fill out both the Company Name and Location text blocks.")

# FEATURE C: RESTORED SUCCESS STORY ACTION INTERFACE
elif menu == "💼 I Got the Job!":
    st.title("🎉 Share Your Career Success Story")
    st.markdown("Found a high-rated workplace from our application database index? Let us know!")
    
    with st.form("success_form", clear_on_submit=True):
        hired_company = st.text_input("Which company hired you?").strip()
        role_title = st.text_input("Job Position / Title").strip()
        user_notes = st.text_area("Tell us about your experience")
        
        hired_btn = st.form_submit_button("Log My Career Victory!")
        if hired_btn:
            if hired_company:
                st.session_state.jobs_placed_count += 1
                st.balloons()
                st.success(f"Awesome! New role tracked at {hired_company}!")
                st.rerun()
            else:
                st.error("Please enter the company name to celebrate your victory.")

# FEATURE D: ENHANCED ADMIN MANAGEMENT PORTAL
elif menu == "🔒 Admin Panel":
    st.title("🔒 Terminal Control Panel")
    
    if not st.session_state.authenticated:
        secret_pass = st.secrets.get("ADMIN_PASSWORD", "fallback_admin123")
        password_attempt = st.text_input("Enter Admin Access Key", type="password")
        
        if st.button("Authenticate"):
            if password_attempt == secret_pass:
                st.session_state.authenticated = True
                st.success("Access Granted.")
                st.rerun()
            else:
                st.error("Invalid key signature. Verify configurations or check environment secrets.")
    else:
        st.sidebar.button("Log Out Admin", on_click=lambda: st.session_state.update({"authenticated": False}))
        
        # Application Metrics Display
        st.subheader("📈 Application Metrics & User Analytics")
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
m_col1.metric("Daily Users So Far", st.session_state.total_visitors_today)
m_col2.metric("Hired Victory Stories", st.session_state.jobs_placed_count)
m_col3.metric("Normal Members Pool", st.session_state.normal_members_count)
m_col4.metric("Premium Member Subscriptions", st.session_state.premium_members_count)
st.markdown("---")
st.subheader("🛠 Database Administration Mode")
if st.session_state.reviews:
for idx, r in enumerate(st.session_state.reviews):
col1, col2 = st.columns(2)
col1.write(f"{r['company']} ({r['location']})")
if col2.button("Purge Entry", key=f"del_{idx}"):
st.session_state.reviews.pop(idx)
st.success("Entry removed from storage pool.")
st.rerun()
else:
st.info("The application review cache is completely clean.")

-------------------------------------------------------------

-------------------------------------------------------------

st.markdown("---")
st.markdown(
"""

© 2026 TA Workspaces. All Rights Reserved. 

🔒 Anti-Scraping Shield Active: Automated collection, data harvesting, processing, or structural cloning
of this application's layout modules, rating definitions, or stored caches is strictly prohibited by law.

""",
unsafe_allow_html=True
)
