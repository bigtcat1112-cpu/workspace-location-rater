import streamlit as st
import pandas as pd
import datetime

# 1. Page Configuration & Security Password
st.set_page_config(page_title="TA Workspaces - Private Admin", page_icon="🔐", layout="centered")

# Custom CSS to make it look like a premium executive control center
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    h1 { color: #1E3A8A; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; }
    </style>
""", unsafe_allow_html=True)

# Simple, secure login form
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 Admin Access Required")
    st.write("This dashboard is strictly restricted to the platform owners.")
    
    password = st.text_input("Enter Admin Password:", type="password")
    login_button = st.button("Access Dashboard")
    
    if login_button:
        if password == "TA_owners_2026":
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect password. Access denied.")
    st.stop()

# --- EVERYTHING BELOW THIS LINE ONLY SHOWS IF LOGIN IS SUCCESSFUL ---

# 2. Header
st.title("📊 TA Workspaces - Executive Admin Panel")
st.write(f"Welcome back! Current Date: **{datetime.date.today().strftime('%B %d, %Y')}**")
st.markdown("---")

# 3. Visitor Analytics Section
st.markdown("### 📈 Live Traffic Overview")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Today's Visitors", value="42 users", delta="+12% vs yesterday")
with col2:
    st.metric(label="Weekly Average", value="185 users", delta="Approaching 200 goal!")
with col3:
    st.metric(label="Total Lifetime Signups", value="612", delta=None)

# Simple traffic chart simulating weekly growth
st.markdown("#### Weekly Traffic Trend")
visitors_list = [110, 130, 145, 120, 160, 195, 185]
chart_data = pd.DataFrame(
    visitors_list,
    index=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    columns=["Visitors"]
)
st.line_chart(chart_data)

st.markdown("---")

# 4. Monetization Pipeline (Target Buyers)
st.markdown("### 💼 Commercial Lead Pipeline")
st.write("Companies matching highly active review locations that might buy a featured spot:")

reviews_list = [14, 28, 42, 9]
leads_data = {
    "Company Name": ["Apex Textile Logistics", "Target Corp", "Amazon Logistics", "Home Depot"],
    "Target Location": ["Regional Hubs", "Hurst Branch", "DFW Fulfillment", "Fort Worth Central"],
    "Review Count": reviews_list,
    "Avg Rating at Site": ["⭐ 2.1 / 5", "⭐ 4.2 / 5", "⭐ 3.0 / 5", "⭐ 2.8 / 5"],
    "Pitch Status": ["High Interest - Reviewing", "Contacted HR", "Monitoring Traffic", "Lead Generated"]
}

df_leads = pd.DataFrame(leads_data)
st.dataframe(df_leads, use_container_width=True)

st.markdown("#### ➕ Add New Sales Lead")
with st.form("add_lead_form", clear_on_submit=True):
    new_company = st.text_input("Company Name:")
    new_loc = st.text_input("Specific Location/Branch Area:")
    new_status = st.selectbox("Current Status:", ["Lead Generated", "Monitoring Traffic", "Ready to Pitch", "In Negotiations"])
    submit_lead = st.form_submit_button("Save Lead to Dashboard")
    
    if submit_lead and new_company:
        st.success(f"Added {new_company} ({new_loc}) to your tracking pipeline!")

# 5. Sticky Owner Footer
st.markdown("---")
st.caption("🔒 Confidential Data | TA Workspaces Proprietary Owner Dashboard")
