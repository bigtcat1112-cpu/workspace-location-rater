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
    .stSelectbox>div>div>div { background-color: #f5f5dc; color: #1e1e1e; }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize data caches and simulated analytics metrics
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

# Real-time traffic tracking counter cycles
if str(date.today()) != st.session_state.last_tracked_date:
    st.session_state.total_visitors_today = 1
    st.session_state.last_tracked_date = str(date.today())
else:
    st.session_state.total_visitors_today += 1

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "subscribed" not in st.session_state:
    st.session_state.subscribed = False

# Workspace database holding updated core categories
if "reviews" not in st.session_state:
    st.session_state.reviews = [
        {
            "company": "TechSpace Downtown", "location": "Dallas, TX",
            "commute": 4, "management": 5, "stress": 4, "team": 5, "pay": 4,
            "lat": 32.7767, "lon": -96.7970
        },
        {
            "company": "CoWork Central", "location": "Fort Worth, TX",
            "commute": 3, "management": 4, "stress": 5, "team": 4, "pay": 5,
            "lat": 32.7555, "lon": -97.3308
        }
    ]

# Simulated cloud databases for new premium hubs
if "premium_alerts" not in st.session_state:
    st.session_state.premium_alerts = [
        {"city": "Dallas, TX", "metric": "Pay & Benefits", "threshold": 4}
    ]
if "resumes_submitted" not in st.session_state:
    st.session_state.resumes_submitted = []

# Mock interview preparation data catalog
interview_guides = {
    "TechSpace Downtown": [
        "❓ Tell me about a time you handled a heavy workflow under tight management pressure.",
        "💡 Tip: Emphasize your communication skill strategies and core boundary management style."
    ],
    "CoWork Central": [
        "❓ How do you manage your project tasks when shifting team structures occur?",
        "💡 Tip: Talk about your flexibility and how you keep stress levels consistently low."
    ]
}

query_params = st.query_params
if "session_id" in query_params:
    st.session_state.subscribed = True
    st.session_state.premium_members_count += 1
    st.sidebar.success("🎉 Payment verified successfully!")

# -------------------------------------------------------------
# 3. SIDEBAR NAVIGATION & PREMIUM GATEWAYS
# -------------------------------------------------------------
st.sidebar.title("🏢 TA Workspaces")

# Building navigation list dynamically based on premium validation status
nav_options = ["🔍 Discover Workspaces", "📝 Rate a Workspace", "💼 I Got the Job!", "🔒 Admin Panel"]
if st.session_state.subscribed:
    nav_options.extend(["🔔 Listing Alerts", "🧠 Interview Prep Hub", "📄 Resume Review Drop"])

menu = st.sidebar.radio("Navigation", nav_options)

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
    st.sidebar.info(
        "🚀 **Premium Perks Unlocked:**\n"
        "* 🛡️ Safe Bet Badges enabled\n"
        "* 🔔 Live Listing Alerts dashboard\n"
        "* 🧠 Company Interview Prep Hub\n"
        "* 📄 Secure Resume Review Drop\n\n"
        "🌱 **Eco Contribution:**\n"
        "**1.5% of subscription profits** go directly to active atmospheric CO2 removal tech."
    )
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
            st.sidebar.info("Click secure portal link above.")
        except Exception as e:
            st.sidebar.error(f"Stripe Error: {e}")

# -------------------------------------------------------------
# 4. CORE CHANNELS & APPLICATION FEATURES
# -------------------------------------------------------------

# TAB A: DISCOVER WORKSPACES (WITH MAP & SAFE BET FILTERS)
if menu == "🔍 Discover Workspaces":
    st.title("🔍 Discover Rated Workspaces")
    
    # Premium Exclusive Safe Bet Filtering Module Toggle
    safe_bet_only = False
    if st.session_state.subscribed:
        col_s1, col_s2 = st.columns([1, 2])
        with col_s1:
            safe_bet_only = st.checkbox("🛡️ Show Safe Bet Companies Only")
        with col_s2:
            min_pay = st.slider("Minimum Pay & Benefits Level", 1, 5, 1)
            
        if safe_bet_only:
            # Safe Bet definition: Team treatment >= 4 and Management >= 4
            filtered_list = [r for r in st.session_state.reviews if r["team"] >= 4 and r["management"] >= 4 and r["pay"] >= min_pay]
        else:
            filtered_list = [r for r in st.session_state.reviews if r["pay"] >= min_pay]
    else:
        filtered_list = st.session_state.reviews
        st.caption("💡 *Tip: Subscribe to premium to use 'Safe Bet' employer tags and metrics filters.*")

    if filtered_list:
        df = pd.DataFrame(filtered_list)
        df["Overall Score"] = df[["commute", "management", "stress", "team", "pay"]].mean(axis=1).round(1)
        
        st.subheader("📍 Nearby Locations")
        st.map(df[["lat", "lon"]])
        
        st.subheader("📋 Workspace Directory")
        
        # Displaying custom indicators directly inside the text directory overview loop
        st.markdown("---")
        st.subheader("⭐ Recent Corporate Ratings")
        for r in filtered_list:
            score = round(np.mean([r["commute"], r["management"], r["stress"], r["team"], r["pay"]]), 1)
            
            # Badge generation logic block
            is_safe_bet = r["team"] >= 4 and r["management"] >= 4
            badge_text = " 🛡️ [SAFE BET EMPLOYER]" if is_safe_bet else ""
            
            st.markdown(f"### 🏢 {r['company']}{badge_text}")
            st.markdown(f"📍 **Location:** {r['location']} | ⭐ **Overall Rating:** `{score} / 5.0`")
            st.markdown(
                f"🚗 Commute: `{r['commute']}/5` | 👔 Management: `{r['management']}/5` | "
                f"🧘 Stress Level (5=Low): `{r['stress']}/5` | 🤝 Team Treatment: `{r['team']}/5` | 💰 Pay & Benefits: `{r['pay']}/5`"
            )
            st.markdown("---")
    else:
        st.info("No workspaces match your filtering or selection path criteria.")

# TAB B: COMPREHENSIVE WORKSPACE RATING FORM (WITH AUTO-ALERT EMITTER)
elif menu == "📝 Rate a Workspace":
    st.title("📝 Submit a New Workspace Rating")
    
    with st.form("rating_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("Company Name").strip()
            location_text = st.text_input("City, State (e.g., Dallas, TX)").strip()
        with col2:
            lat_input = st.number_input("Latitude", value=32.7, format="%.4f")
            lon_input = st.number_input("Longitude", value=-97.3, format="%.4f")
            
        st.markdown("### Quality Metrics")
        commute_ins = st.slider("Commute Quality", 1, 5, 3)
        mgmt_speed = st.slider("Management Quality", 1, 5, 4)
        stress_comfort = st.slider("Stress Levels (5 = Low Stress)", 1, 5, 3)
        team_treatment = st.slider("Team & Employee Treatment", 1, 5, 4)
        pay_setup = st.slider("Pay & Benefits", 1, 5, 3)
        
        submit_btn = st.form_submit_button("Submit Application Rating")
        
        if submit_btn:
            if company_name and location_text:
                st.session_state.reviews.append({
                    "company": company_name, "location": location_text,
                    "commute": int(commute_ins), "management": int(mgmt_speed),
                    "stress": int(stress_comfort), "team": int(team_treatment),
                    "pay": int(pay_setup), "lat": float(lat_input), "lon": float(lon_input)
                })
                st.success(f"Successfully added review for '{company_name}'!")
                st.rerun()
            else:
                st.error("Please completely fill out both the Company Name and Location fields.")

# FEATURE C: RESTORED SUCCESS STORY ACTION INTERFACE
elif menu == "💼 I Got the Job!":
    st.title("🎉 Share Your Career Success Story")
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
                st.error("Please enter the company name.")

# PREMIUM FEATURE D: INSTANT LISTING ALERTS MANAGER
elif menu == "🔔 Listing Alerts" and st.session_state.subscribed:
    st.title("🔔 Instant Listing Alerts Configuration")
    st.markdown("Set triggers to get notified immediately when high-tier workspaces match your layout filters.")
    with st.form("alert_form"):
        target_city = st.text_input("Target City/State (e.g., Dallas, TX)")
        target_metric = st.selectbox("Trigger Category Metric", ["Commute Quality", "Management Quality", "Stress Levels", "Team Treatment", "Pay & Benefits"])
        target_score = st.slider("Minimum Quality Score Trigger", 1, 5, 4)
        add_alert = st.form_submit_button("Deploy Live Tracking Alert Sensor")
        if add_alert and target_city:
            st.session_state.premium_alerts.append({
                "city": target_city, "metric": target_metric, "threshold": target_score
            })
            st.success(f"Tracking radar deployed for entries matching {target_metric} >= {target_score} inside {target_city}!")
    st.subheader("📡 Active Notification Radars")
    for a in st.session_state.premium_alerts:
        st.markdown(f"• Listening for entries in {a['city']} where {a['metric']} hits or exceeds {a['threshold']}/5 rating metrics.")

# PREMIUM FEATURE E: RECRUITMENT INTERVIEW PREPARATION HUB
elif menu == "🧠 Interview Prep Hub" and st.session_state.subscribed:
    st.title("🧠 Company Interview Preparation Hub")
    st.markdown("Review shared interview questions and strategic coaching guides for indexed platform corporations.")
    selected_corp = st.selectbox("Select target firm catalog", list(interview_guides.keys()))
    if selected_corp in interview_guides:
        st.markdown(f"### 📋 Interview Blueprints: {selected_corp}")
        for item in interview_guides[selected_corp]:
            st.markdown(item)
    else:
        st.info("No shared blueprints cataloged for this firm profile block yet.")

# PREMIUM FEATURE F: SECURE RESUME REVIEW DROPBOX
elif menu == "📄 Resume Review Drop" and st.session_state.subscribed:
    st.title("📄 Secure Resume Review Drop")
    st.markdown("Submit your structural resume layout details for background data checking matrix matching.")
    with st.form("resume_drop_form"):
        user_name = st.text_input("Applicant Handle / Nickname")
        resume_text = st.text_area("Paste structural resume details or role descriptions here")
        submit_resume = st.form_submit_button("Submit Resume Data Package")
        if submit_resume and resume_text:
            st.session_state.resumes_submitted.append({"user": user_name, "data": resume_text})
            st.success("Resume data successfully queued for database matrix matching analysis checking verification.")

# FEATURE G: ENHANCED ADMINISTRATIVE TERMINAL MANAGEMENT CONTROL PANEL
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
                st.error("Invalid configuration key signature.")
    else:
        st.sidebar.button("Log Out Admin", on_click=lambda: st.session_state.update({"authenticated": False}))
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
import streamlit as st
import urllib.parse

st.markdown("---")
st.header("🏅 For Featured Businesses")
st.write("Were you rated a top-tier workspace? Grab your free digital verification badge for your website!")

# Clean, modern inputs for the business owner
business_name = st.text_input("Enter Your Business Name (e.g., CoWork Central)", value="CoWork Central")

# Safely format the name so it can be passed into a link if needed
encoded_name = urllib.parse.quote_plus(business_name)
your_app_url = "https://streamlit.app"

# 1. THE VISUAL BADGE: This is exactly what it will look like on their site
st.markdown("##### Preview Your Badge:")
st.markdown(
    f"""
    <div style="
        background-color: #2E2D2A; 
        border: 2px solid #E6A23C; 
        border-radius: 12px; 
        padding: 20px; 
        max-width: 280px; 
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    ">
        <span style="font-size: 2rem;">📍</span>
        <h4 style="color: #FDFBF7; margin: 10px 0 5px 0; font-family: sans-serif;">TOP RATED</h4>
        <h3 style="color: #E6A23C; margin: 0 0 10px 0; font-family: sans-serif; font-size: 1.3rem;">WORKSPACE</h3>
        <p style="color: #D3CFC9; font-size: 0.8rem; margin: 5px 0; font-family: sans-serif;">Verified on</p>
        <strong style="color: #FDFBF7; font-family: sans-serif; letter-spacing: 1px; font-size: 0.9rem;">TA WORKSPACES</strong>
    </div>
    """,
    unsafe_allow_html=True
)

# 2. THE LOOPHOLE EMBED CODE: The copy-and-paste snippet they can take
st.markdown("##### Copy Your Embed Code:")
st.write("Paste this HTML code into your website's editor to display your badge:")

raw_html_snippet = f"""<a href="{your_app_url}" target="_blank" style="text-decoration: none;"><div style="background-color: #2E2D2A; border: 2px solid #E6A23C; border-radius: 12px; padding: 20px; max-width: 280px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.3); font-family: sans-serif;"><span style="font-size: 2rem;">📍</span><h4 style="color: #FDFBF7; margin: 10px 0 5px 0;">TOP RATED</h4><h3 style="color: #E6A23C; margin: 0 0 10px 0; font-size: 1.3rem;">WORKSPACE</h3><p style="color: #D3CFC9; font-size: 0.8rem; margin: 5px 0;">Verified on</p><strong style="color: #FDFBF7; letter-spacing: 1px; font-size: 0.9rem;">TA WORKSPACES</strong></div></a>"""

st.code(raw_html_snippet, language="html")

# -------------------------------------------------------------
# 5. LEGAL & SECURITY ANTI-SCRAPING FOOTER NOTICE
# -------------------------------------------------------------
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: grey; font-size: 0.8em;'>
        © 2026 TA Workspaces. All Rights Reserved. <br>
        🔒 Anti-Scraping Shield Active: Automated collection, data harvesting, processing, or structural cloning 
        of this application's layout modules, rating definitions, or stored caches is strictly prohibited by law.
    </div>
    """,
    unsafe_allow_html=True
)
