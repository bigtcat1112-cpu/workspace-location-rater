import streamlit as st
import stripe
from supabase import create_client, Client
import pandas as pd

# ==========================================
# 1. INITIALIZE APIS & CONFIGURATION
# ==========================================
st.set_page_config(page_title="TA Workspaces", page_icon="🏢", layout="wide")

# Custom injection to brighten background layouts using soft greys and warm beiges
st.markdown("""
    <style>
        .stApp {
            background-color: #F7F5F0;  /* Soft Warm Bright Beige */
        }
        .sidebar .sidebar-content {
            background-color: #EDEDED;  /* Clean Minimal Light Grey */
        }
        div[data-testid="stForm"] {
            background-color: #FFFFFF;
            border: 1px solid #E0DCD3;
            border-radius: 10px;
            padding: 25px;
        }
        div.stMetric {
            background-color: #FAFAFA;
            padding: 10px;
            border-radius: 5px;
        }
    </style>
""", unsafe_allow_html=True)

try:
    # Stripe Flat Layout
    stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]
    STRIPE_PRICE_ID = st.secrets["STRIPE_PRICE_ID"]
    
    # Supabase Connection
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except KeyError as e:
    st.error(f"❌ Configuration error. Missing key inside Streamlit settings: {e}")
    st.stop()

# ==========================================
# 2. HELPER FUNCTIONS (STRIPE & SUPABASE)
# ==========================================
def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': STRIPE_PRICE_ID,
                'quantity': 1,
            }],
            mode='subscription',
            success_url='https://streamlit.app',
            cancel_url='https://streamlit.app',
        )
        return session.url
    except Exception as e:
        st.error(f"Stripe Session Creation Failed: {e}")
        return None

def fetch_reviews():
    try:
        # Pull live records from your Supabase table
        response = supabase.table("reviews").select("*").order("id", desc=True).execute()
        if response.data:
            return pd.DataFrame(response.data)
        return pd.DataFrame()
    except Exception as e:
        # Local mock structural fallback if database connection drops
        return pd.DataFrame([
            {
                "id": 1,
                "company": "TA Workspaces HQ", 
                "rating": "⭐ ⭐ ⭐ ⭐ ⭐", 
                "latitude": 32.7555, 
                "longitude": -97.3308, 
                "comment": "Incredible management team!", 
                "type": "Review", 
                "address": "123 Main St, Fort Worth",
                "details": "Management: 5/5 | Pay: 5/5 | Environment: 5/5 | Safety: 5/5 | Breaks: 5/5"
            }
        ])

def insert_review(company, rating, lat, lon, comment, address, review_type="Review", details=""):
    try:
        # Ensure column map variables align with data rows completely
        data = {
            "company": company, 
            "rating": str(rating), 
            "latitude": float(lat), 
            "longitude": float(lon), 
            "comment": comment,
            "address": address,
            "type": review_type,
            "details": details
        }
        # Step 1: Write to table
        supabase.table("reviews").insert(data).execute()
        st.success(f"🎉 {review_type} submitted successfully!")
        
        # Step 2: Force clean cache session update states before view render loops
        st.cache_data.clear()
        st.rerun()
    except Exception as e:
        st.error(f"Failed to save to database: {e}")

# ==========================================
# 3. STREAMLIT APPLICATION INTERFACE
# ==========================================
st.title("🏢 TA Workspaces")
st.markdown("##### *Transparent Workspace Metrics & Exact Location Ratings*")
st.write("---")

# Combined Sidebar Tier Layout Tracker
with st.sidebar:
    st.header("⚡ Membership Options")
    tier = st.radio("Choose Account Action:", ["Free User Options", "Go Premium ($20/mo)"])
    
    if tier == "Go Premium ($20/mo)":
        st.write("Unlock absolute unrestricted database access, custom map views, and live metric tracking portals.")
        if st.button("Launch Stripe Checkout"):
            with st.spinner("Opening secure checkout..."):
                url = create_checkout_session()
                if url:
                    st.markdown(f"[👉 Click Here to Complete Payment]({url})")
    else:
        st.info("You're using the standard free dashboard tiers. Share your hiring status toggle on the right anytime!")

# Load fresh matching datasets
df_reviews = fetch_reviews()

col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 DFW Workspace Location Map")
    if not df_reviews.empty and 'latitude' in df_reviews.columns and 'longitude' in df_reviews.columns:
        map_df = df_reviews.dropna(subset=['latitude', 'longitude'])
        st.map(map_df[['latitude', 'longitude']])
    else:
        st.info("No location points available to display yet.")

with col2:
    st.subheader("📝 Post Activity Interface")
    action = st.radio("Select submission format type:", ["📝 Leave a Detailed Review", "🎉 I Got the Job! (Free)"])
    
    with st.form("submission_form", clear_on_submit=True):
        company_name = st.text_input("Company or School Name")
        target_address = st.text_input("Exact Street Address / Location Specifics")
        
        if action == "📝 Leave a Detailed Review":
            st.markdown("##### 📊 Location Specific Metrics")
            slider_mgmt = st.slider("Management & Leadership", 1, 5, 5)
            slider_pay = st.slider("Pay Rate & Compensation", 1, 5, 5)
            slider_env = st.slider("Workplace Culture & Environment", 1, 5, 5)
            slider_safe = st.slider("Job Safety & Equipment Condition", 1, 5, 5)
            slider_breaks = st.slider("Break Times & Schedule Flexibility", 1, 5, 5)
            
            avg_score = round((slider_mgmt + slider_pay + slider_env + slider_safe + slider_breaks) / 5)
            star_rating = "⭐ " * avg_score
            
            metrics_summary = f"Management: {slider_mgmt}/5 | Pay: {slider_pay}/5 | Environment: {slider_env}/5 | Safety: {slider_safe}/5 | Breaks: {slider_breaks}/5"
            user_comment = st.text_area("What are your exact concerns or positives about this location?")
            review_type = "Review"
        else:
            st.markdown("### 🥳 Congratulations on getting hired!")
            star_rating = "🎉 Hired!"
            metrics_summary = "Celebration Milestone Posted"
            user_comment = st.text_area("Tell us about your new job role! (Optional)")
            review_type = "Hired Info"
            
        st.markdown("**Exact Coordinates (For Live Map Drop)**")
        latitude = st.number_input("Latitude", value=32.8234, format="%.4f")
        longitude = st.number_input("Longitude", value=-97.1729, format="%.4f")
        
        submitted = st.form_submit_button("Submit Entry")
        if submitted:
            if company_name.strip() == "" or target_address.strip() == "":
                st.warning("Please provide a valid name and specific address location.")
            else:
                insert_review(company_name, star_rating, latitude, longitude, user_comment, target_address, review_type, metrics_summary)

# ==========================================
# 4. RECENT SUBMISSIONS - SPECIFICS LAYOUT
# ==========================================
st.write("---")
st.subheader("📊 Recent Workspace Activity & Location Specifics")

if not df_reviews.empty:
    for index, row in df_reviews.iterrows():
        comp = row.get('company', 'Unknown Work')
        addr = row.get('address', 'No specific address listed')
        comm = row.get('comment', '')
        rate = row.get('rating', '⭐ ⭐ ⭐ ⭐ ⭐')
        specs = row.get('details', '')
        
        # Visually clean custom panels utilizing background color structures
        if row.get('type') == 'Hired Info':
            st.info(f"**🎉 {comp}** — *{addr}* \n\n**Status:** {rate} \n\n{comm}")
        else:
            st.markdown(f"""
            <div style="background-color: #FFFFFF; padding: 15px; border-radius: 8px; border-left: 5px solid #D1C7BD; margin-bottom: 15px;">
                <h4 style="margin: 0; color: #333333;">🏢 {comp}</h4>
                <p style="margin: 5px 0; color: #666666;">📍 <b>Specific Location:</b> <code>{addr}</code></p>
                <p style="margin: 5px 0; color: #FFB400;"><b>Average Rating:</b> {rate}</p>
                <div style="background-color: #F5F5F5; padding: 8px; border-radius: 4px; font-family: monospace; font-size: 0.9em; color: #555555; margin: 10px 0;">
                    {specs}
                </div>
                <p style="margin: 10px 0 0 0; font-style: italic; color: #444444;">> {comm}</p>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("No recent ratings found.")
