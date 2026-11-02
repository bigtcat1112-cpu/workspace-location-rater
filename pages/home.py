import streamlit as st
import streamlit as st
import folium
from streamlit_folium import st_folium
from supabase import create_client, Client
import stripe
import folium
from streamlit_folium import st_folium
from supabase import create_client, Client
import stripe

# 1. Page Configuration
st.set_page_config(
    page_title="TA Workspaces",
    page_icon="📍",
    layout="wide"
)

# Custom Beige Theme Styling Injection
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

# Initialize local state cache for instant review injection feedback
if "local_reviews" not in st.session_state:
    st.session_state["local_reviews"] = []

# 2. Initialize Supabase Connection
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    if "supabase.com" in url.lower() and not ".supabase.co" in url.lower():
        st.error("❌ SUPABASE_URL secret is pointing to the wrong website domain! Update it to your project link.")
        st.stop()
    return create_client(url, key)

try:
    supabase = init_supabase()
except Exception as e:
    st.error("Failed to connect to the database. Check your Secrets configurations.")
    st.stop()

# Initialize Stripe
stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]

# 3. Track Metrics
try:
    supabase.table("analytics").insert({"page": "home", "type": "visit"}).execute()
except:
    pass

# 4. App Layout Main Panels
st.title("🚀 TA Workspaces")
st.markdown("Find and review the best study and workspaces in the DFW Metroplex.")
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 DFW Workspace Locations")
    m = folium.Map(location=[32.8232, -97.1749], zoom_start=11)
    
    try:
        locations_response = supabase.table("workspaces").select("*").execute()
        locations = locations_response.data
        if locations:
            for loc in locations:
                folium.Marker(
                    location=[loc["latitude"], loc["longitude"]],
                    popup=f"<b>{loc['name']}</b><br>{loc['address']}",
                    tooltip=loc["name"]
                ).add_to(m)
    except:
        pass

    st_folium(m, width=650, height=450, key="dfw_map")
    st.divider()

    # ✍️ Submit Review Form Container (NAME REMOVED, SPECIFICS ENFORCED)
    st.markdown('<div class="beige-box">', unsafe_allow_html=True)
    st.subheader("✍️ Leave a Workspace Review")
    with st.form("review_form", clear_on_submit=True):
        workspace_name = st.text_input("Workspace Name (e.g., Bedford Public Library, Cafe)")
        rating = st.slider("Work Quality Rating", 1, 5, 5)
        comment = st.text_area("Amenities & Comments (WiFi speed, seating, noise level)")
        got_job = st.checkbox("I Got the Job! 🎉")
        
        submit_button = st.form_submit_button("Submit Review")

        if submit_button:
            if workspace_name and comment:
                # Compile parameters into historical data snapshot
                new_review = {
                    "workspace": workspace_name,
                    "rating": rating,
                    "comment": comment,
                    "got_job": got_job
                }
                
                # Push immediately to local stack layer for fast rendering response
                st.session_state["local_reviews"].insert(0, new_review)
                
                # Push back upstream payload package to backend database columns
                try:
                    formatted_comment = f"{comment} {'(Got the Job! 🎉)' if got_job else ''}"
                    supabase.table("reviews").insert({
                        "name": workspace_name,  # Mapping name target column directly to specific property label
                        "rating": rating,
                        "comment": formatted_comment
                    }).execute()
                except Exception as e:
                    pass
                
                st.rerun()
            else:
                st.warning("Please specify a workspace location name and fill out your review text.")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # ⭐ Stripe Pass Premium Option Container Block
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
                        'product_data': {'name': 'TA Workspaces Premium Pass'},
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

    # 💬 Consolidated Specific Reviews Feed Presentation
    st.subheader("💬 Recent Reviews")
    all_display_reviews = []
    
    # 1. Mount session cache updates first for zero lag time feedback
    for lr in st.session_state["local_reviews"]:
        all_display_reviews.append({
            "workspace": lr["workspace"],
            "rating": lr["rating"],
            "comment": lr["comment"],
            "got_job": lr["got_job"]
        })
        
    # 2. Extract active records out from database query schema rows
    try:
        reviews_response = supabase.table("reviews").select("*").order("created_at", desc=True).execute()
        cloud_reviews = reviews_response.data
        if cloud_reviews:
            for cr in cloud_reviews:
                if not any(r["workspace"].lower() == cr["name"].lower() and cr["comment"] in r["comment"] for r in all_display_reviews):
                    all_display_reviews.append({
                        "workspace": cr["name"],
                        "rating": cr["rating"],
                        "comment": cr["comment"],
                        "got_job": "🎉" in cr["comment"]
                    })
    except:
        pass

    # Print out clean list blocks item elements
    if all_display_reviews:
        for rev in all_display_reviews:
            job_badge = " | 💼 Got the Job!" if rev.get("got_job") else ""
            st.markdown(f"**Workspace:** {rev['workspace']} — {'⭐' * rev['rating']}{job_badge}")
            st.caption(f"\"{rev['comment']}\"")
            st.divider()
    else:
        st.info("No reviews logged. Be the first to catalog a location profile item!")

# Copyright Footer Section Layout
st.markdown("---")
st.caption("© 2026 TA Workspaces. All rights reserved. Anti-scraping protection enabled.")
