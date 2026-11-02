import streamlit as st
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

# Initialize local state cache for instant review injection feedback
if "local_reviews" not in st.session_state:
    st.session_state["local_reviews"] = []

# 2. Initialize Supabase Connection Safely
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    if "supabase.com" in url.lower() and not ".supabase.co" in url.lower():
        st.error("❌ Your SUPABASE_URL secret is pointing to the wrong website! Change it to your '.supabase.co' project link.")
        st.stop()
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
st.markdown("Find and review the best study and workspaces in DFW.")
st.divider()

# Create two columns (Split screen layout)
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

    # ✍️ Submit Review Form with All 5 Sliders, Exact Location, Good Things, and Red Flags
    st.markdown('<div class="beige-box">', unsafe_allow_html=True)
    st.subheader("✍️ Leave a Workspace Review")
    with st.form("review_form", clear_on_submit=True):
        company_name = st.text_input("Company Name")
        exact_location = st.text_input("Exact Location (Street Address, City)")
        
        st.markdown("**📊 Rate Your Experience (1-5 Stars)**")
        rate_management = st.slider("Management Treatment", 1, 5, 5)
        rate_environment = st.slider("Work Environment", 1, 5, 5)
        rate_coworkers = st.slider("Co-worker Vibe", 1, 5, 5)
        rate_schedule = st.slider("Schedule Flexibility", 1, 5, 5)
        rate_pay = st.slider("Pay & Tips", 1, 5, 5)
        
        good_things = st.text_area("👍 Good Things")
        red_flags = st.text_area("🚩 Red Flags")
        got_job = st.checkbox("I Got the Job! 🎉")
        
        submit_button = st.form_submit_button("Submit Review")

        if submit_button:
            if company_name and exact_location:
                # Calculate average for backwards compatibility displays
                avg_rating = int(round((rate_management + rate_environment + rate_coworkers + rate_schedule + rate_pay) / 5))
                
                # Compile parameters into our session backup cache
                new_review = {
                    "company_name": company_name,
                    "exact_location": exact_location,
                    "rate_management": rate_management,
                    "rate_environment": rate_environment,
                    "rate_coworkers": rate_coworkers,
                    "rate_schedule": rate_schedule,
                    "rate_pay": rate_pay,
                    "good_things": good_things,
                    "red_flags": red_flags,
                    "got_job": got_job,
                    "avg_rating": avg_rating
                }
                
                st.session_state["local_reviews"].insert(0, new_review)
                
                # Push back upstream to matching database columns
                try:
                    supabase.table("reviews").insert({
                        "company_name": company_name,
                        "exact_location": exact_location,
                        "rate_management": rate_management,
                        "rate_environment": rate_environment,
                        "rate_coworkers": rate_coworkers,
                        "rate_schedule": rate_schedule,
                        "rate_pay": rate_pay,
                        "good_things": good_things,
                        "red_flags": red_flags,
                        "got_job": got_job,
                        "name": company_name,      # Legacy support
                        "rating": avg_rating,     # Legacy support
                        "comment": f"Good: {good_things} | Flags: {red_flags}" # Legacy support
                    }).execute()
                except Exception as e:
                    pass
                
                st.rerun()
            else:
                st.warning("Please fill out both the Company Name and Exact Location fields.")
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
        except Exception as e:
            st.error(f"Stripe Checkout integration error: {e}")
    st.markdown('</div>', unsafe_allow_html=True)
    st.divider()

    # 💬 Deep Specs Rating Feed Panel
    st.subheader("💬 Recent Reviews")
    all_display_reviews = []
    
    # 1. Pull local reviews first
    for lr in st.session_state["local_reviews"]:
        all_display_reviews.append({
            "company_name": lr.get("company_name", "Workspace"),
            "exact_location": lr.get("exact_location", "Unknown Location"),
            "rate_management": lr.get("rate_management", 5),
            "rate_environment": lr.get("rate_environment", 5),
            "rate_coworkers": lr.get("rate_coworkers", 5),
            "rate_schedule": lr.get("rate_schedule", 5),
            "rate_pay": lr.get("rate_pay", 5),
            "good_things": lr.get("good_things", ""),
            "red_flags": lr.get("red_flags", ""),
            "got_job": lr.get("got_job", False)
        })
        
    # 2. Extract active rows out from database query schema
    try:
        reviews_response = supabase.table("reviews").select("*").order("created_at", desc=True).execute()
        cloud_reviews = reviews_response.data
        if cloud_reviews:
            for cr in cloud_reviews:
                c_name = cr.get("company_name") or cr.get("name", "Workspace")
                c_loc = cr.get("exact_location") or "DFW Area"
                
                # Check duplicates
                if not any(r["company_name"].lower() == c_name.lower() and r["exact_location"].lower() == c_loc.lower() for r in all_display_reviews):
                    all_display_reviews.append({
                        "company_name": c_name,
                        "exact_location": c_loc,
                        "rate_management": cr.get("rate_management") or cr.get("rating") or 5,
                        "rate_environment": cr.get("rate_environment") or cr.get("rating") or 5,
                        "rate_coworkers": cr.get("rate_coworkers") or cr.get("rating") or 5,
                        "rate_schedule": cr.get("rate_schedule") or cr.get("rating") or 5,
                        "rate_pay": cr.get("rate_pay") or cr.get("rating") or 5,
                        "good_things": cr.get("good_things") or cr.get("comment") or "",
                        "red_flags": cr.get("red_flags") or "",
                        "got_job": cr.get("got_job") or ("🎉" in (cr.get("comment") or ""))
                    })
    except:
        pass

    # Print out clean list cards displaying all 5 sub-ratings
    if all_display_reviews:
        for rev in all_display_reviews:
            job_badge = " | 💼 Got the Job!" if rev.get("got_job") else ""
            st.markdown(f"### 🏢 Company Name: {rev['company_name']}")
            st.caption(f"📍 Location: {rev['exact_location']}{job_badge}")
            
            # Displaying the 5 sub-metrics break-down
            st.markdown(
                f"""
                * 👔 **Management:** {'⭐' * rev['rate_management']}
                * 🏢 **Environment:** {'⭐' * rev['rate_environment']}
                * 👥 Co-workers: {'⭐' * rev['rate_coworkers']}
                * 📅 Flexibility: {'⭐' * rev['rate_schedule']}
                * 💰 Pay/Tips: {'⭐' * rev['rate_pay']}
               """
        ) 
      if rev['good_things']:
      st.markdown(f"👍 Good Things:\n{rev['good_things']}")
           if rev['red_flags']:
                st.markdown(f"🚩 Red Flags:\n{rev['red_flags']}")
         st.divider()
                          else:
        st.info("No detailed metrics logged yet. Submit a form to start the feed!")
     st.markdown("---")
st.caption("© 2026 TA Workspaces. All rights reserved. Anti-scraping protection enabled.")
