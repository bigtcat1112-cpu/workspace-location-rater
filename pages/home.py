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
            success_url='https://streamlit.app',
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
        # Fallback dummy data with a clean status type column
        return pd.DataFrame([
            {"company": "TA Workspaces HQ", "rating": "⭐ ⭐ ⭐ ⭐ ⭐", "location": "Fort Worth, TX", "comment": "Great place!", "type": "Review"},
            {"company": "Burger King", "rating": "⭐ ⭐ ⭐", "location": "Hurst, TX", "comment": "Average work balance.", "type": "Review"},
            {"company": "Bellaire Elementary", "rating": "🎉 Secured!", "location": "Hurst, TX", "comment": "Hired as an assistant! Super excited.", "type": "Hired Info"}
        ])

def insert_review(company, rating, lat, lon, comment, review_type="Review"):
    try:
        data = {
            "company": company, 
            "rating": rating, 
            "lat": lat, 
            "lon": lon, 
            "comment": comment,
            "type": review_type
        }
        supabase.table("reviews").insert(data).execute()
        st.success(f"🎉 {review_type} submitted successfully!")
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
col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 Location Map")
    df_reviews = fetch_reviews()
    
    if not df_reviews.empty and 'lat' in df_reviews.columns and 'lon' in df_reviews.columns:
        st.map(df_reviews[['lat', 'lon']])
    else:
        st.info("No location points coordinates available to display yet.")

with col2:
    # Let the user pick what action they want to do!
    action = st.radio("Choose what to post:", ["📝 Leave a Review", "🎉 I Got the Job! (Free)"])
    
    with st.form("submission_form", clear_on_submit=True):
        company_name = st.text_input("Company or School Name")
        
        if action == "📝 Leave a Review":
            score = st.slider("Rating (1-5 Stars)", 1, 5, 5)
            # Create a pretty star layout text column for formatting
            star_rating = "⭐ " * score
            user_comment = st.text_area("Review Comment")
            review_type = "Review"
        else:
            st.markdown("### 🥳 Congratulations!")
            star_rating = "🎉 Hired!"
            user_comment = st.text_area("Tell us about your new job role! (Optional)")
            review_type = "Hired Info"
            
        st.markdown("**Exact Coordinates**")
        latitude = st.number_input("Latitude", value=32.8234, format="%.4f")
        longitude = st.number_input("Longitude", value=-97.1729, format="%.4f")
        
        submitted = st.form_submit_button("Submit Entry")
        if submitted:
            if company_name.strip() == "":
                st.warning("Please provide a valid name.")
            else:
                insert_review(company_name, star_rating, latitude, longitude, user_comment, review_type)

# ==========================================
# 4. RECENT SUBMISSIONS - CLEAN FORMATTING
# ==========================================
st.subheader("📊 Recent Workspace Activity")

if not df_reviews.empty:
    # Loop over entries to show them as neat card layouts instead of a bulky raw spreadsheet tracker
    for index, row in df_reviews.iterrows():
        # Differentiate reviews from success hires visually
        if row.get('type') == 'Hired Info':
            st.info(f"**🎉 {row['company']}** — *Hired Success Announcement!* \n\n {row['comment']}")
        else:
            st.markdown(f"""
            #### 🏢 {row['company']} 
            *Rating: {row.get('rating', '⭐ ⭐ ⭐ ⭐ ⭐')}*
            
            > {row['comment']}
            ---
            """)
else:
    st.info("No recent ratings found.")
