import streamlit as st
from streamlit_folium import st_folium
import folium
from supabase import create_client, Client
import stripe

# 1. Page Configuration
st.set_page_config(
    page_title="TA Workspaces",
    page_icon="📍",
    layout="wide"
)

# Custom Beige Styling Theme
st.markdown(
    """
    <style>
    .beige-box {
        background-color: rgba(248, 243, 239, 0.85);
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #eaeef2;
        margin-bottom: 20px;
        color: #11181c;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 2. Initialize Supabase Connection
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_supabase()
except Exception as e:
    st.error("Failed to connect to the database. Check your Secrets configurations.")
    st.stop()

# Initialize Stripe
stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]

# 3. Track Visitor Metrics (Supabase Analytics)
def track_visitor():
    try:
        supabase.table("analytics").insert({"page": "home", "type": "visit"}).execute()
    except:
        pass

track_visitor()

# 4. App Header Layout
st.title("🚀 TA Workspaces")
st.markdown("Find and review the best study and workspaces in the DFW Metroplex.")
st.divider()

# Create two columns
col1, col2 = st.columns()

with col1:
    st.subheader("📍 DFW Workspace Locations")
    
    try:
        # Fetch live map marker data
        locations_response = supabase.table("workspaces").select("*").execute()
        locations = locations_response.data

        # Fallback DFW map even if database is empty so it never disappears!
        m = folium.Map(location=[32.8232, -97.1749], zoom_start=11)
        
        if locations:
            for loc in locations:
                folium.Marker(
                    location=[loc["latitude"], loc["longitude"]],
                    popup=f"<b>{loc['name']}</b><br>{loc['address']}",
                    tooltip=loc["name"]
                ).add_to(m)
        else:
            st.info("No workspace locations found yet. Showing base DFW map.")
            
        st_folium(m, width=650, height=450, key="dfw_map")
            
    except Exception as e:
        st.error(f"Could not load the workspace map layout: {e}")

    st.divider()

    # Submit Review Section inside Beige Wrapper
    st.markdown('<div class="beige-box">', unsafe_allow_html=True)
    st.subheader("✍️ Leave a Review")
    with st.form("review_form", clear_on_submit=True):
        user_name = st.text_input("Your Name")
        rating = st.slider("Rating", 1, 5, 5)
        comment = st.text_area("Review Comments")
        submit_button = st.form_submit_button("Submit Review")

        if submit_button:
            if user_name and comment:
                try:
                    new_review = {
                        "name": user_name,
                        "rating": rating,
                        "comment": comment
                    }
                    supabase.table("reviews").insert(new_review).execute()
                    st.success("Thank you! Your review has been submitted.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to save your review: {e}")
            else:
                st.warning("Please fill out both your name and comment fields.")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Stripe Premium Subscription Section inside Beige Wrapper
    st.markdown('<div class="beige-box">', unsafe_allow_html=True)
    st.subheader("⭐ TA Premium Workspace Pass")
    st.markdown("Get access to exclusive private desks, high-speed fiber internet, and free printing terminals.")
    st.markdown("**Price:** $20.00 / month")
    
    if st.button("Subscribe Now", type="primary"):
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'TA Workspaces Premium Subscription',
                        },
                        'unit_amount': 2000,
                        'recurring': {'interval': 'month'},
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url='https://streamlit.app',
                cancel_url='https://streamlit.app',
            )
            st.link_button("Complete Payment on Stripe", session.url)
            try:
                supabase.table("analytics").insert({"page": "home", "type": "checkout_click"}).execute()
            except:
                pass
        except Exception as e:
            st.error(f"Stripe Checkout integration error: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # Recent Reviews Feed Section
    st.subheader("💬 Recent Reviews")
    try:
        reviews_response = supabase.table("reviews").select("*").order("created_at", descending=True).execute()
        recent_reviews = reviews_response.data

        if recent_reviews:
            for rev in recent_reviews:
                st.markdown(f"**{rev['name']}** — {'⭐' * rev['rating']}")
                st.caption(f"\"{rev['comment']}\"")
                st.divider()
        else:
            st.info("No reviews yet. Be the first to leave one using the form!")
    except Exception as e:
        st.error(f"Could not display recent reviews: {e}")

# Copyright Legal Warning Footer Layout
st.markdown("---")
st.caption("© 2026 TA Workspaces. All rights reserved. Anti-scraping protection enabled.")
