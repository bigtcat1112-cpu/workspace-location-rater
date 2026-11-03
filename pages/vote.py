import streamlit as st
from supabase import create_client
import pandas as pd

# Secure Connection Check
if "password_correct" in st.session_state and st.session_state.password_correct:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)

    st.markdown("---")
    st.header("🏆 DFW Workspace of the Month")
    st.write("Cast your vote for the ultimate remote work location in the metroplex. Results update in real-time!")

    # Local temporary session tracking to prevent single-session click spamming
    if "has_voted_this_session" not in st.session_state:
        st.session_state.has_voted_this_session = False

    # 1. FETCH LIVE CONTENDERS AND VOTES
    try:
        votes_query = supabase.table("employer_votes").select("*").order("votes_count", desc=True).execute()
        contenders = votes_query.data
    except Exception as fetch_err:
        st.error(f"Could not load live leaderboard: {fetch_err}")
        contenders = []

    # 2. RENDER INTERACTIVE LEADERBOARD
    if contenders:
        # Layout columns to display choices neatly side-by-side
        cols = st.columns(len(contenders))
        
        for index, row in enumerate(contenders):
            name = row["employer_name"]
            current_votes = row["votes_count"]
            row_id = row["id"]
            
            with cols[index]:
                # Visual Container Card
                st.markdown(
                    f"""
                    <div style="background-color: #2E2D2A; padding: 15px; border-radius: 8px; text-align: center; border-top: 4px solid #409EFF; margin-bottom: 10px;">
                        <b style="color: #FDFBF7; font-size: 1rem;">{name}</b>
                        <h2 style="color: #E6A23C; margin: 5px 0;">{current_votes}</h2>
                        <p style="color: #D3CFC9; font-size: 0.8rem; margin: 0;">Verified Votes</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
                # Dynamic action button that disables instantly if they've voted
                button_disabled = st.session_state.has_voted_this_session
                if st.button(f"Vote for {name.split(' - ')[0]}", key=f"vote_btn_{row_id}", disabled=button_disabled):
                    try:
                        # Database Update Action: Increment target row safely by 1
                        new_vote_total = current_votes + 1
                        supabase.table("employer_votes").update({"votes_count": new_vote_total}).eq("id", row_id).execute()
                        
                        # Lock session state and refresh panel instantly
                        st.session_state.has_voted_this_session = True
                        st.success(f"Vote registered for {name}!")
                        st.rerun()
                    except Exception as vote_err:
                        st.error(f"Transaction failed: {vote_err}")
                        
        if st.session_state.has_voted_this_session:
            st.caption("🔒 Thanks for voting! Your selection has been safely logged in the database for this session.")
    else:
        st.info("No active contenders set up in your database table for this month's tracking cycle yet.")
