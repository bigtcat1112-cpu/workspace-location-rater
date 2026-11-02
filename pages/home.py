import streamlit as st
import stripe
from supabase import create_client, Client
import pandas as pd

# ==========================================
# 1. INITIALIZE APIS & CONFIGURATION
# ==========================================
st.set_page_config(page_title="TA Workspaces", page_icon="🏢", layout="wide")

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
            # Redirects back to your app seamlessly
            success_url='https://streamlit.app{CHECKOUT_SESSION_ID}',
            cancel_url='https://streamlit.app',
        )
        return session.url
    except Exception as e:
        st.error(f"Stripe Session Creation Failed: {e}")
        return None

def fetch_reviews():
    try:
        response = supabase.table("reviews").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception:
        # Fallback dummy data if table isn't built yet
        return pd.DataFrame([
            {"company": "TA Workspaces HQ", "rating": 5, "lat": 32.7555, "lon": -97.3308, "comment": "Great place!"},
            {"company": "Tech Corp", "rating": 3, "lat": 32.8140, "lon": -96.7970, "comment": "Average work balance."}
        ])

def insert_review(company, rating, lat, lon, comment):
    try:
        data = {"company": company, "rating": rating, "lat": lat, "lon": lon, "comment": comment}
        supabase.table("reviews").insert(data).execute()
        st.success("🎉 Review submitted successfully!")
    except Exception as e:
        st.error(f"Failed to save to database: {e}")

# ==========================================
# 3. STREAMLIT APPLICATION INTERFACE
# ==========================================
st.title("🏢 TA Workspaces")
st.markdown("### Transparent Workspace Metrics & Exact Location Ratings")

# Sidebar - Premium Upgrades
with st.sidebar:
    st.header("👑 Premium Access")
    st.write("Unlock fully detailed metrics, advanced filters, and maps.")
    if st.button("Subscribe for $20/mo"):
        with st.spinner("Opening secure checkout..."):
            url = create_checkout_session()
            if url:
                st.markdown(f"[👉 Click Here to Complete Payment]({url})")

# Main Content Layout Split
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📍 DFW Workspace Location Map")
    df_reviews = fetch_reviews()
    
    if not df_reviews.empty and 'lat' in df_reviews.columns and 'lon' in df_reviews.columns:
        st.map(df_reviews[['lat', 'lon']])
    else:
        st.info("No location points coordinates available to display yet.")

with col2:
    st.subheader("📝 Submit a Location Review")
    with st.form("review_form", clear_on_submit=True):
        company_name = st.text_input("Company Name")
        score = st.slider("Rating (1-5 Stars)", 1, 5, 5)
        
        st.markdown("**Exact Coordinates (DFW Area Example)**")
        latitude = st.number_input("Latitude", value=32.7555, format="%.4f")
        longitude = st.number_input("Longitude", value=-97.3308, format="%.4f")
        
        user_comment = st.text_area("Review Comment")
        
        submitted = st.form_submit_button("Submit Rating")
        if submitted:
            if company_name.strip() == "":
                st.warning("Please provide a valid company name.")
            else:
                insert_review(company_name, score, latitude, longitude, user_comment)

# Data Table view below the map
st.subheader("📊 Recent Workspace Submissions")
if not df_reviews.empty:
    st.dataframe(df_reviews[['company', 'rating', 'comment']], use_container_width=True)
