import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from supabase import create_client
import stripe

# --- CUSTOM BEIGE & GRAY DESIGN STYLING ---
st.markdown(
    """
    <style>
    /* Main Page Background & Base Text */
    .stApp {
        background-color: #FDFBF7; /* Bright Clear Beige */
        color: #4A4A4A; /* Dark Beige Grey Text Contrast */
    }
    
    /* Input Fields Border and Background Style */
    div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea {
        background-color: #F5F2EB !important; /* Soft Cream Beige Inside Inputs */
        color: #4A4A4A !important;
        border-color: #D3CFC9 !important;
    }
    
    /* Headings and Titles color matching your theme */
    h1, h2, h3, h4, .stSlider {
        color: #3E3D3A !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- SECURE API CLIENT INITIALIZATION ---
try:
    # Safely pulling all secrets from Streamlit Secrets Management
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
        # Fixed: payment_method_types is removed; uses Dashboard dynamic settings
        session = stripe.checkout.Session.create(
            line_items=[{
                'price': 'price_1UXNrfEbNBWTyWzqE2qkw78S', # Your production price ID
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
    locations_query = supabase.table("reviews").select("company_name, location_address, rating").execute().data
    if locations_query:
        df = pd.DataFrame(locations_query)
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
        st.markdown(
            f"""
            <div style='background-color: #F5F2EB; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 5px solid #D3CFC9;'>
                <strong style='color: #3E3D3A;'>🏢 {r.get('company_name', 'Unknown Location')}</strong> ({r.get('location_address', 'No Address Provided')})<br>
                <span style='color: #E6A23C;'>{'★' * int(r.get('rating', 5))}</span><br>
                <p style='margin-top: 5px; color: #4A4A4A;'>"{r.get('comment', '')}"</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
else:
    st.write("No location profiles submitted yet.")

# --- SUBMIT REVIEWS FORM (No username field) ---
st.subheader("Rate a Specific Work Location")
with st.form("workspace_review_form", clear_on_submit=True):
    company_name = st.text_input("Company or Venue Name", placeholder="e.g. Target, local office space")
    location_address = st.text_input("Exact Physical Location Address", placeholder="Street Address, City, State")
    rating = st.slider("Work Environment Rating", min_value=1, max_value=5, value=5)
    comment = st.text_area("Detailed Review (Workspace cleanliness, management, treatment, amenities)")
    
    submit_btn = st.form_submit_button("Submit Rating Details")

    if submit_btn:
        if company_name and location_address and comment:
            new_review = {
                "company_name": company_name, 
                "location_address": location_address, 
                "rating": rating, 
                "comment": comment
            }
            try:
                supabase.table("reviews").insert(new_review).execute()
                st.success("🎉 Location details logged! The public map feed is updating...")
                st.rerun()
            except Exception as e:
                st.error(f"Supabase Database Failure: {e}")
        else:
            st.error("Please fill in the Company, Address, and Review fields before submitting.")

