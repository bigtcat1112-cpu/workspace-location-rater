import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from supabase import create_client
import stripe
import time

# ==========================================
# 1. ADVANCED DARK THEME INJECTION
# ==========================================
st.set_page_config(
    page_title="TA Workspaces - Fort Worth / DFW Area",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    /* Global Application Shell Base Override */
    .stApp {
        background-color: #3E3D3A !important;
        color: #FDFBF7 !important;
    }
    
    /* Input Fields / Text Areas Structural Overrides */
    div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea {
        background-color: #FDFBF7 !important;
        color: #3E3D3A !important;
        border-radius: 6px !important;
        border: 1px solid #D3CFC9 !important;
        font-weight: 500 !important;
    }
    
    /* Block Headers, Target Slider Elements and Labels styling */
    h1, h2, h3, h4, h5, h6, label, .stSlider {
        color: #FDFBF7 !important;
    }
    
    /* Streamlit Form Container Theming Overrides */
    div[data-testid="stForm"] {
        background-color: #2E2D2A !important;
        border: 1px solid #4E4D4A !important;
        border-radius: 12px !important;
        padding: 25px !important;
    }
    
    /* Left Structural Sidebar Column Overrides */
    section[data-testid="stSidebar"] {
        background-color: #2E2D2A !important;
        border-right: 1px solid #4E4D4A !important;
    }
    
    /* Custom Notification Alert Block Rules */
    .review-card {
        background-color: #2E2D2A; 
        padding: 20px; 
        border-radius: 10px; 
        margin-bottom: 15px; 
        border-left: 6px solid #D3CFC9;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 2. SECURE API CLIENT RECOVERY INITIALIZATION
# ==========================================
@st.cache_resource
def initialize_supabase():
    """Initializes and returns a secure cache client instance for Supabase."""
    try:
        supabase_url = st.secrets["SUPABASE_URL"]
        supabase_key = st.secrets["SUPABASE_KEY"]
        return create_client(supabase_url, supabase_key)
    except KeyError:
        st.error("🔒 Supabase Credentials Missing in Streamlit Secret Variables Panel.")
        return None
    except Exception as e:
        st.error(f"Initialization Halted: {e}")
        return None

@st.cache_resource
def initialize_stripe():
    """Initializes production settings for the Stripe gateway API securely."""
    try:
        stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]
        return True
    except KeyError:
        st.sidebar.error("🔒 Stripe API Secret String Token is Missing.")
        return False

supabase = initialize_supabase()
stripe_active = initialize_stripe()

# ==========================================
# 3. APP HEADER LOGO WRAPPER
# ==========================================
st.title("📍 TA Workspaces")
st.subheader("DFW Workplace Location & Job Rating Matrix")
st.markdown("---")

# ==========================================
# 4. STRIPE DYNAMIC PORTAL FRAMEWORK
# ==========================================
st.sidebar.header("Premium Subscription")
st.sidebar.write("Unlock full DFW historical analytics, trends, and platform verification filters.")

if st.sidebar.button("Subscribe for $20/month", key="stripe_btn_checkout"):
    if stripe_active:
        try:
            session = stripe.checkout.Session.create(
                line_items=[{
                    'price': 'price_1UXNrfEbNBWTyWzqE2qkw78S',
                    'quantity': 1,
                }],
                mode='subscription',
                success_url='https://streamlit.app',
                cancel_url='https://streamlit.app',
            )
            st.sidebar.success("Payment Checkout Token Generated!")
            st.sidebar.markdown(f"[👉 Click here to complete subscription session]({session.url})")
        except Exception as e:
            st.sidebar.error(f"Stripe Checkout Error: {e}")
    else:
        st.sidebar.warning("Stripe client interface offline.")

# ==========================================
# 5. GEOGRAPHIC MAP LAYOUT MATRIX
# ==========================================
st.header("Workspace Location Map")
st.write("Browse community-verified business environments throughout Fort Worth and Dallas.")

map_lat, map_lon = 32.837, -97.265
dfw_map = folium.Map(location=[map_lat, map_lon], zoom_start=11, tiles="OpenStreetMap")

folium.Marker(
    location=[32.895, -97.310],
    popup="<b>Alliance Workspace Hub</b><br>Logged clean with strong management scoring.",
    tooltip="Alliance Workspace Hub"
).add_to(dfw_map)

folium.Marker(
    location=[32.755, -97.330],
    popup="<b>Downtown FW Tech Space</b><br>High-speed amenities logged.",
    tooltip="Downtown FW Tech Space"
).add_to(dfw_map)

st_folium(dfw_map, width=850, height=450, returned_objects=[])
st.markdown("---")

# ==========================================
# 6. DYNAMIC SYSTEM LIVE REVIEWS FEED
# ==========================================
st.header("📋 Recent Workplace Ratings Feed")

reviews_data = []
if supabase:
    try:
        response = supabase.table("reviews").select("*").order("created_at", desc=True).execute()
        reviews_data = response.data
    except Exception as e:
        st.error(f"Database Query Error: {e}")

if reviews_data:
    for idx, review in enumerate(reviews_data):
        company = review.get("company_name", "Unspecified Facility")
        address = review.get("location_address", "No Address Token")
        score = review.get("overall_rating", 5.0)
        comment_text = review.get("comment", "")
        
        mgt = review.get("rating_management", 5)
        cln = review.get("rating_cleanliness", 5)
        trt = review.get("rating_treatment", 5)
        amn = review.get("rating_amenities", 5)
        grw = review.get("rating_growth", 5)
        
        st.markdown(
            f"""
            <div class="review-card">
                <span style='font-size: 1.25rem; font-weight: bold; color: #FDFBF7;'>🏢 {company}</span> 
                <span style='color: #D3CFC9; font-size: 0.9rem;'>— Location: {address}</span><br>
                <span style='color: #E6A23C; font-weight: bold;'>★ Overall Rating: {score}/5</span><br>
                <div style='margin-top: 5px; margin-bottom: 10px; font-size: 0.85rem; color: #D3CFC9;'>
                    Management: <b>{mgt}</b> | Cleanliness: <b>{cln}</b> | Treatment: <b>{trt}</b> | Amenities: <b>{amn}</b> | Career/Pay: <b>{grw}</b>
                </div>
                <p style='margin-top: 5px; color: #FDFBF7; font-style: italic;'>"{comment_text}"</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
else:
    st.info("No authenticated workplace profiles logged in database tables yet.")

st.markdown("---")

# ==========================================
# 7. EXPLICIT 5-RATER SUBMISSION LAYOUT
# ==========================================
st.header("✍️ Submit a Workplace Evaluation")
st.write("Log an anonymous evaluation profile for any company or branch facility.")

with st.form("workspace_review_form", clear_on_submit=True):
    col_input1, col_input2 = st.columns(2)
    
    with col_input1:
        company_name = st.text_input("Company or Venue Name *", placeholder="e.g. Target, local office space")
    with col_input2:
        location_address = st.text_input("Exact Physical Location Address *", placeholder="Street Address, City, State")
        
    st.markdown("##### Detailed Environmental Metric Sliders")
    
    rating_management = st.slider("1. Management Quality & Support", min_value=1, max_value=5, value=5, step=1)
    rating_cleanliness = st.slider("2. Workplace Cleanliness & Safety", min_value=1, max_value=5, value=5, step=1)
    rating_treatment = st.slider("3. Employee Treatment & Treatment Morale", min_value=1, max_value=5, value=5, step=1)
    rating_amenities = st.slider("4. Provided Amenities, Breaks, & Facilities", min_value=1, max_value=5, value=5, step=1)
    rating_growth = st.slider("5. Career Growth, Scheduling, & Fair Compensation", min_value=1, max_value=5, value=5, step=1)
    
    comment = st.text_area("Detailed Summary Review *", placeholder="Provide insights about conditions...")
    
    st.caption("* Indicates a required operational field.")
    submit_btn = st.form_submit_button("Submit Rating Details")

    if submit_btn:
        if company_name and location_address and comment:
            overall_avg = round((rating_management + rating_cleanliness + rating_treatment + rating_amenities + rating_growth) / 5, 1)
            
            new_review = {
                "company_name": company_name.strip(),
                "location_address": location_address.strip(),
                "rating_management": rating_management,
                "rating_cleanliness": rating_cleanliness,
                "rating_treatment": rating_treatment,
                "rating_amenities": rating_amenities,
                "rating_growth": rating_growth,
                "overall_rating": overall_avg,
                "comment": comment.strip()
            }
            
            if supabase:
                try:
                    supabase.table("reviews").insert(new_review).execute()
                    st.success("🎉 Detailed metrics logged successfully! Map feed reloading...")
                    time.sleep(1.0)
                    st.rerun()
                except Exception as e:
                    st.error(f"Supabase Database Failure: {e}")
            else:
                st.error("Database connectivity pipeline offline.")
        else:
st.error("Submission blocked. Please fill out all required fields.")
st.markdown("---")
st.caption("© 2026 TA Workspaces. Protected tracking pipelines active. Anti-bot scrapers enabled.")
