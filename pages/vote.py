import streamlit as st
from supabase import create_client
import time

# ==========================================
# 1. RETRO DARK MODE THEME INJECTION
# ==========================================
st.set_page_config(page_title="Vote - TA Workspaces", layout="wide")

st.markdown(
    """
    <style>
    /* Main App Background Overrides */
    .stApp {
        background-color: #1e1e1e !important;
        color: #f5f5dc !important;
    }
    
    /* Document Component Header Colors */
    h1, h2, h3, h4, label, p {
        color: #f5f5dc !important;
    }
    
    /* Leaderboard Container Card Blocks */
    .leaderboard-card {
        background-color: #2E2D2A;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        border-top: 4px solid #E6A23C;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        margin-bottom: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 2. SECURE SUPABASE CONNECTION SETUP
# ==========================================
@st.cache_resource
def get_supabase_client():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

supabase = get_supabase_client()

# ==========================================
# 3. INTERACTIVE VOTING INTERFACE
# ==========================================
st.title("🏆 DFW Workspace of the Month")
st.write("Cast your vote for the ultimate remote work location in the metroplex. Results update in real-time!")
st.markdown("---")

# Initialize session anti-spam switch 
if "has_voted_this_session" not in st.session_state:
    st.session_state.has_voted_this_session = False

if supabase:
    # 1. FETCH LIVE CONTENDERS AND VOTES FROM SUPABASE
    try:
        votes_query = supabase.table("employer_votes").select("*").order("votes_count", desc=True).execute()
        contenders = votes_query.data
    except Exception as fetch_err:
        st.error(f"Could not sync live leaderboard profiles: {fetch_err}")
        contenders = []

    # 2. RENDER THE DYNAMIC CARDS
    if contenders:
        # Create equal columns side-by-side dynamically based on row counts
        cols = st.columns(len(contenders))
        
        for index, row in enumerate(contenders):
            name = row["employer_name"]
            current_votes = row["votes_count"]
            row_id = row["id"]
            
            with cols[index]:
                # Visual Container Card Injection
                st.markdown(
                    f"""
                    <div class="leaderboard-card">
                        <span style="font-size: 1.8rem;">📍</span>
                        <h4 style="margin: 10px 0 5px 0; font-family: sans-serif; font-size: 1.1rem;">{name}</h4>
                        <h1 style="color: #E6A23C; margin: 5px 0; font-size: 2.5rem;">{current_votes}</h1>
                        <p style="color: #D3CFC9; font-size: 0.8rem; margin: 0; font-family: sans-serif;">Verified Votes</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
                # Check button state block
                button_disabled = st.session_state.has_voted_this_session
                
                # Dynamic action button centered under card
                if st.button(f"Vote for {name.split(' - ')[0]}", key=f"vote_btn_{row_id}", disabled=button_disabled, use_container_width=True):
                    try:
                        # Database Transaction: Safely increment column value by 1
                        new_vote_total = current_votes + 1
                        supabase.table("employer_votes").update({"votes_count": new_vote_total}).eq("id", row_id).execute()
                        
                        # Set lock state flags and restart client view instantly
                        st.session_state.has_voted_this_session = True
                        st.toast(f"🎉 Vote registered for {name}!")
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as vote_err:
                        st.error(f"Transaction failed: {vote_err}")
                        
        st.markdown("---")
        if st.session_state.has_voted_this_session:
            st.info("🔒 Thanks for casting your vote! Your choice has been safely saved in the cloud database container for this session.")
    else:
        st.info("No active contenders set up in your database table for this month's tracking cycle yet.")
else:
    st.warning("Application requires active database client tokens inside your local system secrets configuration pipeline.")

st.markdown("---")
st.caption("© 2026 TA Workspaces. Real-time platform data sync active.")
