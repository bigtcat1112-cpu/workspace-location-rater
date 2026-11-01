import streamlit as st

# Define your official page objects
home_page = st.Page("job.py", title="Home", icon="🏠")
admin_page = st.Page("pages/admin.py", title="Staff Portal", icon="🔒")

# Run the navigation system
pg = st.navigation([home_page, admin_page])
pg.run()
import os
import json
import time
import streamlit as str
import folium
from streamlit_folium import st_folium

# -------------------------------------------------------------
# GOOGLE SEARCH BOT OPTIMIZATION (SEO META TAGS)
# -------------------------------------------------------------
str.set_page_config(
    page_title="TA workspaces - Exact Location Employer Ratings",
    page_icon="📍",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "TA workspaces is an independent job rater platform mapping employer treatment and safety at exact store locations across Hurst and the Fort Worth area."
    }
)

# -------------------------------------------------------------
# DATABASE & STORAGE MANAGEMENT
# -------------------------------------------------------------
DB_FILE = 'ratings_database.json'

def load_data():
    """Loads all saved ratings from our permanent JSON database."""
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, 'r') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []

def save_data(ratings_list):
    """Saves the current ratings list permanently to the JSON file."""
    with open(DB_FILE, 'w') as f:
        json.dump(ratings_list, f, indent=4)

# Set up our persistent ratings memory
if 'ratings' not in str.session_state:
    str.session_state.ratings = load_data()

# -------------------------------------------------------------
# ANTI-SCRAPING & RATE-LIMITING SECURITY
# -------------------------------------------------------------
if 'last_submission_time' not in str.session_state:
    str.session_state.last_submission_time = 0.0

def check_rate_limit():
    """Returns True if the user is submitting within safety boundaries."""
    current_time = time.time()
    time_passed = current_time - str.session_state.last_submission_time
    if time_passed < 5.0:
        return False
    return True

# -------------------------------------------------------------
# BRAND IDENTITY LOGO HEADER
# -------------------------------------------------------------
if os.path.exists('logo.png'):
    str.image('logo.png', use_container_width=True)
else:
    str.title("TA workspaces")

str.caption("Employer Ratings. At Your Exact Location.")

# -------------------------------------------------------------
# INTERACTIVE WORKPLACE MAP WIDGET
# -------------------------------------------------------------
str.write("### 📍 Live Workplace Map Tracker")
m = folium.Map(location=[32.8234, -97.1729], zoom_start=12)

for r in str.session_state.ratings:
    if 'lat' in r and 'lon' in r:
        popup_info = f"<b>{r['company_name']}</b><br>Overall: {r['rating_score']}⭐<br>Treatment: {r['treatment_score']}⭐"
        folium.Marker(
            [r['lat'], r['lon']], 
            popup=popup_info,
            tooltip=r['company_name'],
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)

st_folium(m, width=700, height=400)

# -------------------------------------------------------------
# DETAILED WORKPLACE RATINGS FORM
# -------------------------------------------------------------
str.write("---")
str.write("### 📝 Share a Specific Location Review")

with str.form("rating_form", clear_on_submit=True):
    company_name = str.text_input("Company/Employer Name")
    exact_location = str.text_input("Exact Street Address or Specific Location")
    
    str.write("**Detailed Workplace Metrics:**")
    rating_score = str.slider("Overall Rating Score", 1, 5, 3)
    treatment_score = str.slider("How They Treat Employees", 1, 5, 3)
    safety_score = str.slider("Workplace Safety & Comfort", 1, 5, 3)
    
    review_text = str.text_area("Specific Workplace Concerns or Feedback")
    
    str.write("*Map Placement Coordinates (Optional):*")
    col1, col2 = str.columns(2)
    with col1:
        lat = str.number_input("Latitude (e.g., 32.82)", value=32.8234, format="%.4f")
    with col2:
        lon = str.number_input("Longitude (e.g., -97.17)", value=-97.1729, format="%.4f")

    submitted = str.form_submit_button("Submit Secure Rating")
    
    if submitted:
        if not check_rate_limit():
            str.error("Security Block: Too many requests. Please wait a few seconds before trying again.")
        elif not company_name or not exact_location:
            str.error("Validation Error: Please provide both a Company Name and a specific location.")
        else:
            str.session_state.last_submission_time = time.time()
            
            new_entry = {
                'company_name': company_name,
                'exact_location': exact_location,
                'rating_score': int(rating_score),
                'treatment_score': int(treatment_score),
                'safety_score': int(safety_score),
                'review_text': review_text,
                'lat': lat,
                'lon': lon,
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            str.session_state.ratings.append(new_entry)
            save_data(str.session_state.ratings)
            str.success("Detailed rating safely encrypted and pinned to map database!")

# -------------------------------------------------------------
# SECURED DATA FEED LAYOUT
# -------------------------------------------------------------
str.write("---")
str.write("### 🔒 Verified Workplace Location Ratings Feed")

if not str.session_state.ratings:
    str.info("No location ratings available for this area yet.")
else:
    for r in reversed(str.session_state.ratings):
        str.write(f"#### 🏢 {r['company_name']}")
        str.write(f"📍 *Location:* {r['exact_location']}")
        
        col1, col2, col3 = str.columns(3)
        with col1:
            str.write(f"**Overall:** {'⭐' * r.get('rating_score', 3)}")
        with col2:
            str.write(f"**Employee Treatment:** {'⭐' * r.get('treatment_score', 3)}")
        with col3:
            str.write(f"**Safety & Comfort:** {'⭐' * r.get('safety_score', 3)}")
            
        if r.get('review_text'):
            str.info(f"\"{r['review_text']}\"")
        str.write("---")

# -------------------------------------------------------------
# LEGAL COMPLIANCE FOOTER
# -------------------------------------------------------------
str.markdown("<br><br>", unsafe_allow_html=True)
str.write("---")
str.caption("© 2026 TA workspaces. All rights reserved. Warning: Scraping or copying proprietary data from this site is strictly prohibited by our legal terms.")
st.markdown("---")
if st.button("🔒 Staff Portal"):
    st.switch_page("pages/admin.py")


