import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# ==========================================
# 1. RETRO DARK MODE THEME INJECTION
# ==========================================
st.set_page_config(page_title="Leaderboard - TA Workspaces", layout="wide")

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
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        border-top: 4px solid #E6A23C;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        margin-bottom: 15px;
    }
    
    .winner-card {
        background-color: #2E2D2A;
        padding: 30px;
        border-radius: 12px;
        text-align: center;
        border: 2px solid #E6A23C;
        box-shadow: 0 6px 15px rgba(230, 162, 60, 0.2);
        margin-bottom: 25px;
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
        url = st.secrets.get("SUPABASE_URL") or st.secrets.get("supabase_url")
        key = st.secrets.get("SUPABASE_KEY") or st.secrets.get("supabase_key")
        
        if url and key:
            return create_client(url, key)
        else:
            return None
    except Exception as e:
        return None

supabase = get_supabase_client()

# ==========================================
# 3. AUTOMATED LEADERBOARD ENGINE
# ==========================================
current_month_name = datetime.now().strftime('%B %Y')
st.title(f"🏆 DFW Workspace Leaderboard — {current_month_name}")
st.write("This leaderboard ranks local workspaces automatically based on live, verified user reviews.")
st.markdown("---")

if supabase:
    try:
        # 1. FETCH ALL REAL LIVE REVIEWS
        reviews_query = supabase.table("reviews").select("company_name", "overall_rating").execute()
        raw_reviews = reviews_query.data
        
        if raw_reviews:
            # 2. PROCESS LIVE DATABASE MATH WITH PANDAS
            df = pd.DataFrame(raw_reviews)
            
            # Count total reviews per company
            total_counts = df["company_name"].value_counts()
            
            # Count how many 5-star reviews each company has
            five_star_df = df[df["overall_rating"] == 5.0]
            five_star_counts = five_star_df["company_name"].value_counts()
            
            # Combine the calculations into a single leaderboard dataframe
            leaderboard_data = []
            for company in total_counts.index:
                votes = int(five_star_counts.get(company, 0))
                total = int(total_counts.get(company, 0))
                leaderboard_data.append({
                    "company_name": company,
                    "votes_count": votes,
                    "total_reviews": total
                })
            
            # Sort companies so the one with the most 5-star reviews is first
            leaderboard_data = sorted(leaderboard_data, key=lambda x: x["votes_count"], reverse=True)
            
            # 3. AUTOMATICALLY DISPLAY THE CURRENT WINNER
            winner = leaderboard_data[0]
            st.markdown(
                f"""
                <div class="winner-card">
                    <span style="font-size: 3rem;">👑</span>
                    <h2 style="color: #E6A23C; margin: 10px 0 5px 0; letter-spacing: 1px;">CURRENT MONTHLY LEADER</h2>
                    <h1 style="font-size: 2.8rem; margin: 5px 0;">{winner['company_name']}</h1>
                    <p style="color: #D3CFC9; font-size: 1.1rem; margin: 0;">
                        Dominating the charts with <b>{winner['votes_count']}</b> perfect 5-Star ratings!
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown("### 📊 Live Standings")
            
            # 4. RENDER THE REST OF THE CONTENDERS IN CLEAN COLUMNS
            cols = st.columns(min(len(leaderboard_data), 4))
            for index, row in enumerate(leaderboard_data):
                col_index = index % 4
                with cols[col_index]:
                    st.markdown(
                        f"""
                        <div class="leaderboard-card">
                            <span style="font-size: 1.5rem;">📍 Rank #{index + 1}</span>
                            <h4 style="margin: 10px 0 5px 0; font-family: sans-serif; font-size: 1.1rem;">{row['company_name']}</h4>
                            <h1 style="color: #E6A23C; margin: 5px 0; font-size: 2.2rem;">{row['votes_count']}</h1>
                            <p style="color: #D3CFC9; font-size: 0.8rem; margin: 0; font-family: sans-serif;">
                                5-Star Votes ({row['total_reviews']} total reviews)
                            </p>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
        else:
            st.info("No reviews have been submitted to your database yet. Drop a review on the main page to kickstart the leaderboard standings!")
            
    except Exception as db_err:
        st.error(f"Live database calculation stream failed: {db_err}")
else:
    st.warning("Application requires active database connection pipelines.")

st.markdown("---")
st.caption("© 2026 TA Workspaces. Fully automated live metrics tracking active.")
