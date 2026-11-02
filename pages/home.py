import streamlit as st
import stripe
from supabase import create_client, Client

# ==========================================
# 1. CONNECTIONS & SECRET CREDENTIALS
# ==========================================
# Make sure these names exactly match what is in your .streamlit/secrets.toml file!
stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]
price_id = st.secrets["STRIPE_PRICE_ID"]

url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# ==========================================
# 2. THE DATABASE HELPER FUNCTION
# ==========================================
def save_user_to_database(username, job_title, is_premium):
    # If they want premium, mark them as pending until Stripe clears the payment
    starting_tier = "Free"
    if is_premium:
        starting_tier = "Pending Premium" 
        
    try:
        # Insert a new row straight into your Supabase table
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
# 3. INTERFACE SCREEN CONTROLLER
# ==========================================
st.title("🎉 Celebrate Your New Job!")
st.write("Log your success completely anonymously and unlock career tips.")

# Initialize the screen step tracking if it isn't set yet
if "payment_step" not in st.session_state:
    st.session_state["payment_step"] = "form"

# --- SCREEN STEP A: THE REGISTRATION FORM ---
if st.session_state["payment_step"] == "form":
    with st.form("job_celebration_form"):
        st.subheader("Congratulations! Let's get you ready for Day 1:")
        
        username = st.text_input("Create an Anonymous Username", placeholder="e.g., DFW_Coder11")
        job_title = st.selectbox("What is your new role?", [
            "Cashier / Crew Member",
            "Stocking Associate",
            "Customer Service Rep",
            "Shift Supervisor",
            "Office Assistant"
        ])
        
        premium = st.checkbox("Upgrade to Daily Premium Tips ($20/mo) 💎")
        submit_job = st.form_submit_button("Next Step")
        
        if submit_job:
            if not username:
                st.error("Please enter a username to protect your identity!")
            else:
                # 🛠️ CALL THE DATABASE FUNCTION HERE
                success = save_user_to_database(username, job_title, premium)
                
                if success:
                    st.session_state["username"] = username
                    st.session_state["job_title"] = job_title
                    
                    # Direct them to the correct next screen based on their selection
                    if premium:
                        st.session_state["payment_step"] = "stripe_checkout"
                        st.rerun()
                    else:
                        st.session_state["payment_step"] = "free_success"
                        st.rerun()

# --- SCREEN STEP B: REDIRECT TO STRIPE FOR PREMIUM ---
elif st.session_state["payment_step"] == "stripe_checkout":
    st.subheader("💎 Activate Daily Premium Tips")
    st.write(f"Username: **{st.session_state['username']}**")
    st.write("Click the secure link below to complete your subscription on Stripe's official billing platform:")

    try:
        # Create a real checkout link session
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
        
        st.link_button("Go to Secure Payment Screen ↗", checkout_session.url, type="primary")
        
    except Exception as e:
        st.error("Stripe configuration error. Double check your API keys inside secrets.toml.")

# --- SCREEN STEP C: FREE SUCCESS CONFIRMATION ---
elif st.session_state["payment_step"] == "free_success":
    st.balloons()
    st.success(f"Profile saved! Your free weekly tips are locked in, {st.session_state['username']}!")
    
    if st.button("Back to Form"):
        st.session_state["payment_step"] = "form"
        st.rerun()
