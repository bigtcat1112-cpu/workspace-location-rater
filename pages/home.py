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
        pass  # Silent fail so it doesn't break the UI layout for users

track_visitor()

# 4. App Header Layout
st.title("🚀 TA Workspaces")
st.markdown("Find and review the best study and workspaces in the DFW Metroplex.")
st.divider()

# Create two columns: Left for Map & Actions, Right for Reviews & Subscriptions
col1, col2 = st.columns([2, 1.5])

with col1:
    st.subheader("📍 DFW Workspace Locations")
    
    try:
        # Fetch live map marker data from Supabase
        locations_response = supabase.table("workspaces").select("*").execute()
        locations = locations_response.data

        if locations:
            # Center the map around the DFW center point
            m = folium.Map(location=[32.8232, -97.1749], zoom_start=11)
            
            # Drop interactive markers onto the map layout
            for loc in locations:
                folium.Marker(
                    location=[loc["latitude"], loc["longitude"]],
                    popup=f"<b>{loc['name']}</b><br>{loc['address']}",
                    tooltip=loc["name"]
                ).add_to(m)
            
            # Display map object inside Streamlit layout
            st_folium(m, width=650, height=450, key="dfw_map")
        else:
            st.info("No workspace locations found in the database. Add some via the admin panel!")
            
    except Exception as e:
        st.error(f"Could not load the workspace map layout: {e}")

    st.divider()

    # Submit Review Section
    st.subheader("✍️ Leave a Review")
    with st.form("review_form", clear_on_submit=True):
        user_name = st.text_input("Your Name")
        rating = st.slider("Rating", 1, 5, 5)
        comment = st.text_area("Review Comments")
        submit_button = st.form_submit_button("Submit Review")

        if submit_button:
            if user_name and comment:
                try:
                    # Insert the new review row into Supabase
                    new_review = {
                        "name": user_name,
                        "rating": rating,
                        "comment": comment
                    }
                    supabase.table("reviews").insert(new_review).execute()
                    
                    st.success("Thank you! Your review has been submitted.")
                    
                    # Force Streamlit to instantly rerun and pull the fresh review feed
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Failed to save your review: {e}")
            else:
                st.warning("Please fill out both your name and comment fields.")

with col2:
    # Stripe Premium Subscription Section
    st.subheader("⭐ TA Premium Workspace Pass")
    st.markdown("Get access to exclusive private desks, high-speed fiber internet, and free printing terminals.")
    st.markdown("**Price:** $20.00 / month")
    
    if st.button("Subscribe Now", type="primary"):
        try:
            # Create a real Stripe Checkout Session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'TA Workspaces Premium Subscription',
                        },
                        'unit_amount': 2000, # $20.00 in cents
                        'recurring': {'interval': 'month'},
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url='https://streamlit.app',
                cancel_url='https://streamlit.app',
            )
            # Direct link to checkout
            st.link_button("Complete Payment on Stripe", session.url)
            
            # Log subscription attempt event
            supabase.table("analytics").insert({"page": "home", "type": "checkout_click"}).execute()
        except Exception as e:
            st.error(f"Stripe Checkout integration error: {e}")

    st.divider()

    # Recent Reviews Feed Section
    st.subheader("💬 Recent Reviews")
    try:
        # Fetch reviews directly sorted by newest first
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

# 5. Copyright Legal Warning Footer Layout
st.markdown("---")
st.caption("© 2026 TA Workspaces. All rights reserved. Anti-scraping protection enabled.")
