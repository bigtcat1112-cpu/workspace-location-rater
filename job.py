import os
import json
import time
import streamlit as str

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
# Track submission timestamps in session memory to stop bot floods
if 'last_submission_time' not in str.session_state:
    str.session_state.last_submission_time = 0.0

def check_rate_limit():
    """Returns True if the user is submitting too quickly (bot behavior)."""
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
# SECURE RATINGS SUBMISSION FORM
# -------------------------------------------------------------
with str.form("rating_form", clear_on_submit=True):
    company_name = str.text_input("Company Name")
    exact_location = str.text_input("Exact Location (Full Address or Neighborhood)")
    rating_score = str.slider("Rating Score", 1, 5, 3)
    review_text = str.text_area("Review / Employee Concerns")
    
    # Perfectly aligned submission button line
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
                'rating_score': rating_score,
                'review_text': review_text,
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            str.session_state.ratings.append(new_entry)
            save_data(str.session_state.ratings)
            str.success("Rating submitted and encrypted into database successfully!")

# -------------------------------------------------------------
# SECURED DATA LAYOUT VIEW
# -------------------------------------------------------------
str.write("---")
str.write("### 🔒 Verified Workplace Location Ratings")

if not str.session_state.ratings:
    str.info("No ratings available for this area yet.")
else:
    for r in reversed(str.session_state.ratings):
        str.write(f"**{r['company_name']}** — *{r['exact_location']}*")
        str.write(f"Rating: {'⭐' * r['rating_score']}")
        if r['review_text']:
            str.write(f"\"{r['review_text']}\"")
        str.write("---")

# -------------------------------------------------------------
# LEGAL COMPLIANCE FOOTER
# -------------------------------------------------------------
str.markdown("<br><br>", unsafe_allow_html=True)
str.write("---")
str.caption("© 2026 TA workspaces. All rights reserved. Warning: Scraping or copying proprietary data from this site is strictly prohibited by our legal terms.")

