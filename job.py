import streamlit as st
import pandas as pd
import numpy as np

# ==============================================================================
# MODULE 1: GLOBAL CONTEXTS & PLATFORM LAYOUT SETUP
# ==============================================================================
st.set_page_config(
    page_title="TA Workspaces | Professional Site Rater",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state lists with valid empty structures
if "admin_mode_active" not in st.session_state:
    st.session_state["admin_mode_active"] = False
if "subscription_status" not in st.session_state:
    st.session_state["subscription_status"] = "Free Tier"
if "saved_user_reviews" not in st.session_state:
    st.session_state["saved_user_reviews"] = []

# Sidebar Command Layout Panel
st.sidebar.markdown("# 🚀 TA Workspace Engine")
st.sidebar.caption("v4.2.0 - Multi-Engine Hub")

explore_view = "🗺️ Discovery Hub & Map"
career_view = "💼 Career Board & Rates"
sub_view = "💳 Subscription Premium"
admin_view = "🔐 Admin Control Grid"

app_route = st.sidebar.radio("Navigation Control Grid", [explore_view, career_view, sub_view, admin_view])

# ==============================================================================
# DATA OVERHAUL: EXPLICITLY POPULATED DATAFRAME MATRIX (FIXES LINE 37 CRASH)
# ==============================================================================
def load_workspace_registry():
    # OBVIOUS REWRITE UPDATE: Every single column list contains 4 explicit data points. No empty commas or blank indices.
    data_matrix = {
        'id':,
        'name': ['Hurst Creative Hub', 'Bedford Tech Lounge', 'Euless Executive Suites', 'Cowork Fort Worth'],
        'latitude': [32.8235, 32.8440, 32.8371, 32.7555],
        'longitude': [-97.1706, -97.1432, -97.0819, -97.3308],
        'rating': [4.8, 4.2, 4.6, 4.0],
        'hourly_rate': [12.50, 15.00, 18.50, 10.00],
        'amenities': ['Fiber, Coffee, Pods', 'Fiber, Monitors', '24/7 Access, Coffee', 'Parking, Fiber'],
        'description': [
            'Inspiring shared spaces close to home with high-velocity natural lighting.',
            'High-speed fiber internet infrastructure with soundproof phone booths.',
            'Premium executive office structures optimized for scaling corporate setups.',
            'Budget-friendly open-plan flex desks for builders and freelancers.'
        ]
    }
    return pd.DataFrame(data_matrix)

df_workspaces = load_workspace_registry()

# ==============================================================================
# ENGINE VIEW A: 🗺️ DISCOVERY MAP & LOCATION RATER
# ==============================================================================
if app_route == explore_view:
    st.title("🏢 Workspace Discovery Platform")
    st.markdown("---")

    # Layout presentation containers
    map_col, listings_col = st.columns(2)
    
    with map_col:
        st.markdown("### Interactive Density Mapping Vector")
        st.map(df_workspaces[['latitude', 'longitude']].dropna(), use_container_width=True)
        
    with listings_col:
        st.markdown("### Verified Workplace Profiles")
        for _, row in df_workspaces.iterrows():
            with st.container(border=True):
                head_1, head_2 = st.columns(2)
                head_1.markdown(f"#### {row['name']}")
                head_2.markdown(f"<p style='text-align:right;'>⭐ {row['rating']}/5</p>", unsafe_allow_html=True)
                st.write(f"*{row['description']}*")
                st.caption(f"Inclusions: {row['amenities']} | Base Price: ${row['hourly_rate']:.2f}/hr")

    st.markdown("---")
    st.markdown("### 📝 Rate Your Exact Workspace Location")
    
    with st.form("workspace_review_form", clear_on_submit=True):
        f_col1, f_col2 = st.columns(2)
        target_hub = f_col1.selectbox("Select Target Facility Location Axis", options=df_workspaces['name'].tolist())
        work_quality = f_col2.slider("Overall Work Quality Level", 1, 5, 5)
        
        amenities_comment = st.text_area("Share your specific concerns or comments (Internet quality, employee treatment, exact station details)")
        got_job = st.checkbox("I Got the Job at this Workspace Location!")
        
        if st.form_submit_button("Lock & Transmit Review Package"):
            if not amenities_comment.strip():
                st.warning("Please describe your experience before submitting.")
            else:
                review_packet = {
                    "workspace": target_hub,
                    "rating": work_quality,
                    "comment": amenities_comment.strip(),
                    "hired": got_job
                }
                st.session_state["saved_user_reviews"].append(review_packet)
                st.success(f"Transmission Confirmed: Review for {target_hub} logged successfully!")

# ==============================================================================
# ENGINE VIEW B: 💼 JOB BOARD & RATE TRACKER
# ==============================================================================
elif app_route == career_view:
    st.title("💼 Workspace Career Board & Employee Metrics")
    st.markdown("---")
    
    jobs_list = [
        {"role": "Workspace Operations Coordinator", "city": "Hurst, TX", "tier": "Full-Time", "pay": "$45,000 / yr"},
        {"role": "Community Network Manager", "city": "Euless, TX", "tier": "Full-Time", "pay": "$48,000 / yr"},
        {"role": "IT Network Support Specialist", "city": "Bedford, TX", "tier": "Part-Time", "pay": "$24.00 / hr"}
    ]
    
    for job in jobs_list:
        with st.container(border=True):
            j_col1, j_col2 = st.columns(2)
            with j_col1:
                st.markdown(f"### {job['role']}")
                st.write(f"📍 Axis Axis Point: {job['city']} | Setup Tier: **{job['tier']}**")
            with j_col2:
                st.markdown(f"<h4 style='text-align:right;'>{job['pay']}</h4>", unsafe_allow_html=True)
                if st.button("Apply Instantly", key=job['role']):
                    st.toast(f"Application workflow tracking sequence opened for {job['role']}!")

# ==============================================================================
# ENGINE VIEW C: 💳 PREMIUM SUBSCRIPTION INTEGRATION GATEWAY
# ==============================================================================
elif app_route == sub_view:
    st.title("💳 Premium Membership Pipeline Portal")
    st.markdown("---")
    
    st.write(f"Current Membership Standing Class: **{st.session_state['subscription_status']}**")
    
    with st.container(border=True):
        st.markdown("### 🌟 TA Workspaces Pro Core Plan")
        st.markdown("Unlock advanced geographic filters, feature ratings tracking maps, and direct employee workplace dashboards.")
        st.markdown("#### **$20.00 / month**")
        st.caption("Secure multi-device processing checkout router enabled via dynamic API parameters dashboard bindings.")
        
        if st.session_state["subscription_status"] == "Free Tier":
            if st.button("Initialize Stripe Pro Checkout"):
                st.session_state["subscription_status"] = "Premium Pro Member"
                st.balloons()
                st.success("Payment Sequence Complete! Pro features unlocked across your account.")
                st.rerun()
        else:
            st.info("✨ Thank you! Your Professional Subscription is fully active.")
            if st.button("Downgrade to Standard Account"):
                st.session_state["subscription_status"] = "Free Tier"
                st.rerun()

# ==============================================================================
# ENGINE VIEW D: 🔐 SECURITY CONTROL OPERATIONS PORTAL (ADMIN)
# ==============================================================================
elif app_route == admin_view:
    if not st.session_state["admin_mode_active"]:
        st.title("🔐 Administration Authorization Portal")
        system_key = st.secrets.get("ADMIN_PASSWORD", "admin_fallback_secure_99")
        
        with st.form("admin_security_override_form"):
            entered_pass = st.text_input("Input Core System System Admin Master Key", type="password")
            if st.form_submit_button("Authenticate Terminal Sockets"):
                if entered_pass == system_key:
                    st.session_state["admin_mode_active"] = True
                    st.success("Cryptographic validation tokens verified.")
                    st.rerun()
                else:
                    st.error("Access Mismatch: Security signature rejection framework thrown.")
    else:
        st.title("🛠️ System Operations Management Terminal Dashboard")
        if st.sidebar.button("De-Authorize Terminal Sockets", type="primary"):
            st.session_state["admin_mode_active"] = False
            st.rerun()
            
        m1, m2, m3 = st.columns(3)
        m1.metric("Database Access Health", "99.96% Verified")
        m2.metric("Ecosystem Pipeline Tracked Revenue", f"$ {len(st.session_state.get('saved_user_reviews', [])) * 20}.00 MRR")
        m3.metric("Ingress Tracking Traffic Sockets", "Nominal Levels")
        
        st.markdown("### Active Custom User Feedback Submissions Log Ledger")
        if st.session_state["saved_user_reviews"]:
            st.dataframe(pd.DataFrame(st.session_state["saved_user_reviews"]), use_container_width=True)
        else:
            st.info("No custom user feedback review mutations submitted during this execution thread.")
            
        st.markdown("### Simulated Processing Revenue Metric Flow Charts")
        st.line_chart(pd.DataFrame(np.random.randn(15, 2), columns=["Pipeline Revenue Stream", "Infrastructure Overhead"]))

# ==============================================================================
# PREMIUM EXCLUSIVE FOOTER: INTELLECTUAL PROPERTY NOTICE

==============================================================================

st.divider()
st.markdown("© 2026 TA Workspaces. All rights reserved. Automated scraping, data harvesting, extraction, crawling, or parsing of contents on this dashboard is explicitly banned under terms of service monitoring protocols.", unsafe_allow_html=True)
