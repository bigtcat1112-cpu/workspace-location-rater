import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from supabase import create_client
import stripe

# --- RESTORED CUSTOM DARK THEME (Dark Beige Grey with Brighter Accents) ---
st.markdown(
    """
    <style>
    /* Main Page Background & Base Text */
    .stApp {
        background-color: #3E3D3A; /* Dark Beige Grey Background */
        color: #FDFBF7; /* Bright Clear Beige Text */
    }
    
    /* Input Fields Background Style */
    div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea {
        background-color: #FDFBF7 !important; /* Brighter Contrast Inside Inputs */
        color: #3E3D3A !important;
        border-color: #D3CFC9 !important;
    }
    
    /* Side Bar Styling */
    section[data-testid="stSidebar"] {
        background-color: #2E2D2A !important;
    }
    
    /* Headings and Labels */
    h1, h2, h3, h4, label, .stSlider {
        color: #FDFBF7 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- SECURE API CLIENT INITIALIZATION ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
    stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]
except Exception as e:
    st.error("🔒 Configuration Key Check Failed. Verify your settings in your Streamlit Cloud Secrets dashboard.")
    st.stop()

st.title("📍 TA Workspaces")
st.subheader("Real Location and Job Ratings Dashboard")

# --- STRIPE LIVE SUBSCRIPTION PORTAL ---
st.sidebar.header("Premium Subscription")
if st.sidebar.button("Subscribe for $20/month"):
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
        st.sidebar.success("Payment Checkout generated successfully!")
        st.sidebar.markdown(f"[👉 Click here to complete subscription session]({session.url})")
    except Exception as e:
        st.sidebar.error(f"Stripe Checkout Error: {e}")

# --- DFW WORKSPACE GEOGRAPHIC MAP ---
st.header("Workspace Location Map")
dfw_map = folium.Map(location=[32.837, -97.265], zoom_start=11)

try:
    locations_query = supabase.table("reviews").select("company_name, location_address").execute().data
except:
    pass

st_folium(dfw_map, width=700, height=450, returned_objects=[])

# --- DYNAMIC REVIEWS FEED ---
st.header("Recent Workplace Ratings")
try:
    response = supabase.table("reviews").select("*").order("created_at", descending=True).execute()
    reviews_data = response.data
except Exception as e:
    reviews_data = []

if reviews_data:
    for r in reviews_data:
        # Calculate overall score dynamically from stored scores if needed
        st.markdown(
            f"""
            <div style='background-color: #2E2D2A; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 5px solid #D3CFC9;'>
                <strong style='color: #FDFBF7;'>🏢 {r.get('company_name', 'Unknown Location')}</strong> ({r.get('location_address', 'No Address Provided')})<br>
                <span style='color: #E6A23C;'>⭐ Overall Rating: {r.get('overall_rating', 5)}/5</span><br>
                <small style='color: #D3CFC9;'>
                    Management: {r.get('rating_management', 5)} | 
                    Workplace Cleanliness: {r.get('rating_cleanliness', 5)} | 
                    Employee Treatment: {r.get('rating_treatment', 5)} | 
                    Amenities: {r.get('rating_amenities', 5)} | 
                    Growth/Pay: {r.get('rating_growth', 5)}
                </small>
                <p style='margin-top: 5px; color: #FDFBF7;'>"{r.get('comment', '')}"</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
else:
    st.write("No location profiles submitted yet.")

# --- SUBMIT REVIEWS FORM WITH 5 SPECIFIC RATING CRITERIA ---
st.subheader("Rate a Specific Work Location")
with st.form("workspace_review_form", clear_on_submit=True):
    company_name = st.text_input("Company or Venue Name", placeholder="e.g. Target, local office space")
    location_address = st.text_input("Exact Physical Location Address", placeholder="Street Address, City, State")
    
    # Restored 5 custom lines for explicit breakdowns
    rating_management = st.slider("1. Management Quality & Support", min_value=1, max_value=5, value=5)
    rating_cleanliness = st.slider("2. Workplace Cleanliness & Environment", min_value=1, max_value=5, value=5)
    rating_treatment = st.slider("3. Employee Treatment & Safety", min_value=1, max_value=5, value=5)
    rating_amenities = st.slider("4. Provided Amenities & Facilities", min_value=1, max_value=5, value=5)
    rating_growth = st.slider("5. Career Growth & Fair Compensation", min_value=1, max_value=5, value=5)
    
    comment = st.text_area("Detailed Summary Review")
    
    submit_btn = st.form_submit_button("Submit Rating Details")

    if submit_btn:
        if company_name and location_address and comment:
            # Calculate overall average slider score dynamically
            overall_avg = round((rating_management + rating_cleanliness + rating_treatment + rating_amenities + rating_growth) / 5, 1)
            
            new_review = {
                "company_name": company_name, 
                "location_address": location_address, 
                "rating_management": rating_management,
                "rating_cleanliness": rating_cleanliness,
                "rating_treatment": rating_treatment,
                "rating_amenities": rating_amenities,
                "rating_growth": rating_growth,
                "overall_rating": overall_avg,
                "comment": comment
            }
            try:
                supabase.table("reviews").insert(new_review).execute()
                st.success("🎉 Detailed metrics logged successfully! Map feed reloading...")
                st.rerun()
            except Exception as e:
                st.error(f"Supabase Database Failure: {e}")
        else:
            st.error("Please fill in the Company, Address, and Review fields before submitting.")
