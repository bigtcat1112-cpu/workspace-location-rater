import streamlit as st
import stripe
from supabase import create_client, Client

# ==========================================
# 1. DATABASE & BANKING CLIENT CONNECTIONS
# ==========================================
stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]
price_id = st.secrets["STRIPE_PRICE_ID"]

url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# Helper function to log entries anonymously to your Supabase table
def save_user_to_database(username, job_title, is_premium):
    starting_tier = "Free"
    if is_premium:
        starting_tier = "Pending Premium" 
    try:
        supabase.table("profiles").insert({
            "username": username,
            "job_title": job_title,
            "tier": starting_tier
        }).execute()
        return True
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

# ==========================================
# 2. PART A: THE ORIGINAL RATINGS ENGINE
# ==========================================
st.title("📍 TA Workspaces Location Rater")
st.write("Browse honest, exact-location workplace environments across the DFW Metroplex:")

# Your core starter database list of companies
companies = [
    {"name": "TA Workspaces", "location": "Hurst, TX", "rating": 5.0, "link": "https://linkedin.com", "is_featured": True},
    {"name": "Example Tech Corp", "location": "Fort Worth, TX", "rating": 4.2, "link": "https://linkedin.com", "is_featured": False},
    {"name": "DFW Logistics Hub", "location": "Euless, TX", "rating": 3.9, "link": "https://linkedin.com", "is_featured": False},
]

# Render your standard clickable directory blocks
for co in companies:
    # Highlight paid or featured slots dynamically at the top
    bg_color = "#fffdf0" if co["is_featured"] else "#f9f9f9"
    border_color = "#ffda79" if co["is_featured"] else "#ddd"
    badge = "⭐ FEATURED PARTNER" if co["is_featured"] else "🏢 Regular Listing"
    
    card_html = f"""
    <a href="{co['link']}" target="_blank" style="text-decoration: none; color: inherit;">
        <div style="
            padding: 15px; 
            border-radius: 10px; 
            border: 1px solid {border_color}; 
            margin-bottom: 12px; 
            cursor: pointer;
            background-color: {bg_color};
            transition: 0.2s;
        " onMouseOver="this.style.transform='scale(1.01)'" onMouseOut="this.style.transform='scale(1)'">
            <span style="font-size: 11px; font-weight: bold; color: #777;">{badge}</span>
            <h3 style="margin: 3px 0 0 0; color: #0077B5;">{co['name']}</h3>
            <p style="margin: 5px 0 0 0; font-size: 14px; color: #555;">📍 {co['location']} | Score: **{co['rating']}/5**</p>
        </div>
    </a>
    """
    st.markdown(card_html, unsafe_allow_html=True)

st.divider()

# ==========================================
# 3. PART B: THE USER RETENTION REVENUE ENGINE
# ==========================================
st.header("🎉 Celebrations & Weekly Pro Tips")
st.write("Did our platform help you land a new local gig? Tell the community anonymously!")

# Initialize state controllers
if "payment_step" not in st.session_state:
    st.session_state["payment_step"] = "form"

# --- LAYOUT SCREEN 1: THE RECRUITMENT INPUT FORM ---
if st.session_state["payment_step"] == "form":
    with st.form("job_celebration_form"):
        st.subheader("I Got the Job! 🚀")
        
        username = st.text_input("Create an Anonymous Username", placeholder="e.g., DFW_Coder11")
        job_title = st.selectbox("What is your new role?", [
            "Cashier / Crew Member",
            "Stocking Associate",
            "Customer Service Rep",
            "Shift Supervisor",
            "Office Assistant"
        ])
        
        premium = st.checkbox("Upgrade to Daily Premium Tips ($20/mo) 💎")
        submit_job = st.form_submit_button("Secure My Tips Link")
        
        if submit_job:
            if not username:
                st.error("Please provide an anonymous profile handle first!")
            else:
                success = save_user_to_database(username, job_title, premium)
                if success:
                    st.session_state["username"] = username
                    st.session_state["job_title"] = job_title
                    
                    if premium:
                        st.session_state["payment_step"] = "stripe_checkout"
                        st.rerun()
                    else:
                        st.session_state["payment_step"] = "free_success"
                        st.rerun()

# --- LAYOUT SCREEN 2: STRIPE VAULT GATEWAY LINK ---
elif st.session_state["payment_step"] == "stripe_checkout":
    st.info("💎 Premium Option Highlighted")
    st.write(f"Account Handle: **{st.session_state['username']}**")
    st.write("Click the secure terminal below to complete your billing registration with Stripe:")
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url='https://streamlit.app',
            cancel_url='https://streamlit.app',
            client_reference_id=st.session_state["username"]
        )
        st.link_button("Proceed to Bank Vault Stripe Checkout ↗", checkout_session.url, type="primary")
    except Exception as e:
        st.error("Stripe configuration error. Verify keys inside settings.")
        
    if st.button("Cancel & Return"):
        st.session_state["payment_step"] = "form"
        st.rerun()

# --- LAYOUT SCREEN 3: STANDARD REGISTRATION SUCCESS ---
elif st.session_state["payment_step"] == "free_success":
    st.balloons()
    st.success(f"Log successful! Welcome to the weekly free tip feed, {st.session_state['username']}!")
    
    if st.button("Return to Dashboard View"):
        st.session_state["payment_step"] = "form"
        st.rerun()
