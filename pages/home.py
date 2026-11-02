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
            success_url='https://workspace-location-rater-jnegy9jvnqwzeuvxfifqtv.streamlit.app/',
            cancel_url='https://workspace-location-rater-jnegy9jvnqwzeuvxfifqtv.streamlit.app/',
        )
        return session.url
    except Exception as e:
        st.error(f"Stripe Session Creation Failed: {e}")
        return None

def fetch_reviews():
    try:
        # Pull everything live from Supabase
        response = supabase.table("reviews").select("*").execute()
        if response.data:
            return pd.DataFrame(response.data)
        return pd.DataFrame()
    except Exception as e:
        # Fallback dummy data if connection drops
        return pd.DataFrame([
            {"company": "TA Workspaces HQ", "rating": "⭐ ⭐ ⭐ ⭐ ⭐", "latitude": 32.7555, "longitude": -97.3308, "comment": "Great place!", "type": "Review", "address": "123 Main St, Fort Worth"},
            {"company": "Burger King", "rating": "⭐ ⭐ ⭐", "latitude": 32.8140, "longitude": -97.1729, "comment": "Average work balance.", "type": "Review", "address": "789 Highway 121, Hurst"}
        ])

def insert_review(company, rating, lat, lon, comment, address, review_type="Review"):
    try:
        # Ensure these column names perfectly match your Supabase table columns!
        data = {
            "company": company, 
            "rating": str(rating), 
            "latitude": float(lat), 
            "longitude": float(lon), 
            "comment": comment,
            "address": address,
            "type": review_type
        }
        supabase.table("reviews").insert(data).execute()
        st.success(f"🎉 {review_type} submitted successfully!")
        # Force rerun so it updates instantly on the screen
        st.rerun()
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

# Load data first so map and list stay aligned
df_reviews = fetch_reviews()

# Fixed column initialization (passing 2 splits it properly)
col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 DFW Workspace Location Map")
    
    # Check for latitude/longitude columns to make sure map doesn't crash
    if not df_reviews.empty and 'latitude' in df_reviews.columns and 'longitude' in df_reviews.columns:
        # Map needs a dataframe containing 'latitude' and 'longitude' columns
        map_df = df_reviews.dropna(subset=['latitude', 'longitude'])
        st.map(map_df[['latitude', 'longitude']])
    else:
        st.info("No location points available to display yet.")

with col2:
    # Let the user pick what action they want to do!
    action = st.radio("Choose what to post:", ["📝 Leave a Review", "🎉 I Got the Job! (Free)"])
    
    with st.form("submission_form", clear_on_submit=True):
        company_name = st.text_input("Company or School Name")
        target_address = st.text_input("Exact Street Address / Location Specifics")
        
        if action == "📝 Leave a Review":
            score = st.slider("Rating (1-5 Stars)", 1, 5, 5)
            star_rating = "⭐ " * score
            user_comment = st.text_area("What are your exact concerns or positives about this location?")
            review_type = "Review"
        else:
            st.markdown("### 🥳 Congratulations!")
            star_rating = "🎉 Hired!"
            user_comment = st.text_area("Tell us about your new job role! (Optional)")
            review_type = "Hired Info"
            
        st.markdown("**Exact Coordinates (For Live Map Drop)**")
        # Defaulting center near Hurst area coordinates
        latitude = st.number_input("Latitude", value=32.8234, format="%.4f")
        longitude = st.number_input("Longitude", value=-97.1729, format="%.4f")
        
        submitted = st.form_submit_button("Submit Entry")
        if submitted:
            if company_name.strip() == "" or target_address.strip() == "":
                st.warning("Please provide a valid name and specific address location.")
            else:
                insert_review(company_name, star_rating, latitude, longitude, user_comment, target_address, review_type)

# ==========================================
# 4. RECENT SUBMISSIONS - SPECIFICS LAYOUT
# ==========================================
st.subheader("📊 Recent Workspace Activity & Location Specifics")

if not df_reviews.empty:
    for index, row in df_reviews.iterrows():
        # Clean defaults if missing
        comp = row.get('company', 'Unknown Work')
        addr = row.get('address', 'No specific address listed')
        comm = row.get('comment', '')
        rate = row.get('rating', '⭐ ⭐ ⭐ ⭐ ⭐')
        
        if row.get('type') == 'Hired Info':
            st.info(f"**🎉 {comp}** — *{addr}* \n\n**Status:** {rate} \n\n{comm}")
        else:
            st.markdown(f"""
            #### 🏢 {comp} 
            📍 **Specific Location:** `{addr}`
            *Rating:* {rate}
            
            > {comm}
            ---
            """)
else:
    st.info("No recent ratings found.")
