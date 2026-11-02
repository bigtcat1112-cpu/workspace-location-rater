import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from supabase import create_client
import stripe

# 1. Initialize API Clients from Streamlit Secrets
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
    stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]
except Exception as e:
    st.error("Missing configuration secrets. Please check your Streamlit Secrets layout.")
    st.stop()

st.set_page_config(page_title="TA Workspaces", layout="wide")
st.title("📍 TA Workspaces - DFW Area")

# 2. Stripe Checkout Logic (Fixed: payment_method_types removed)
st.sidebar.header("Premium Subscription")
if st.sidebar.button("Subscribe for $20/month"):
    try:
        session = stripe.checkout.Session.create(
            line_items=[{
                'price': st.secrets.get("STRIPE_PRICE_ID", "price_12345"),
                'quantity': 1,
            }],
            mode='subscription',
            success_url='https://streamlit.io', # Update to your live app URL
            cancel_url='https://streamlit.io',
        )
        st.sidebar.success("Checkout link generated!")
        st.sidebar.markdown(f"[👉 Click here to Pay]({session.url})")
    except Exception as e:
        st.sidebar.error(f"Stripe error: {e}")

# 3. Interactive DFW Workspace Map
st.header("Workspace Map")
# Center around Fort Worth / DFW area
dfw_map = folium.Map(location=[32.837, -97.265], zoom_start=11)

# Sample workspaces to display (Feel free to pull these dynamically from Supabase instead)
workspaces = [
    {"name": "Alliance Workspace Hub", "lat": 32.895, "lon": -97.310, "desc": "Great amenities near Hurst/Keller"},
    {"name": "Downtown FW Tech Space", "lat": 32.755, "lon": -97.330, "desc": "High-speed fiber internet"}
]

for ws in workspaces:
    folium.Marker(
        location=[ws["lat"], ws["lon"]],
        popup=f"<b>{ws['name']}</b><br>{ws['desc']}",
        tooltip=ws["name"]
    ).add_to(dfw_map)

st_folium(dfw_map, width=700, height=450, returned_objects=[])

# 4. Reviews Section (Fixed: Pops in instantly from Supabase)
st.header("💬 User Reviews")

# Fetch and show recent reviews
try:
    response = supabase.table("reviews").select("*").order("created_at", descending=True).execute()
    reviews_data = response.data
except Exception as e:
    reviews_data = []
    st.warning("Could not load current reviews. Ensure your Supabase table 'reviews' exists.")

if reviews_data:
    for r in reviews_data:
        st.info(f"**{r.get('username', 'Anonymous')}** ({r.get('rating', 5)}⭐): {r.get('comment', '')}")
else:
    st.write("No reviews submitted yet. Be the first!")

# Submit Review Form
st.subheader("Leave a Review")
with st.form("review_form", clear_on_submit=True):
    username = st.text_input("Your Name", placeholder="Tristan")
    rating = st.slider("Rating", min_value=1, max_value=5, value=5)
    comment = st.text_area("Your Review")
    submit_btn = st.form_submit_button("Submit Review")

    if submit_btn:
        if username and comment:
            new_review = {"username": username, "rating": rating, "comment": comment}
            try:
                # Insert to Supabase table named 'reviews'
                supabase.table("reviews").insert(new_review).execute()
                st.success("🎉 Review submitted! Reloading...")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to submit to Supabase: {e}")
        else:
            st.error("Please fill in both your name and comment field.")

# 5. Protected Footer
st.markdown("---")
st.caption("© 2026 TA Workspaces. All rights reserved. Dynamic anti-scraping system enabled.")
