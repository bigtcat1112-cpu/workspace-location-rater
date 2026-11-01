import streamlit as st
import pandas as pd
import json
import os
import folium
from streamlit_folium import st_folium

# Name of our permanent database file
DB_FILE = "workplace_db.json"

# Load reviews from our permanent file, or create a brand new one if it doesn't exist
def load_database():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    else:
        # Initial starter locations in Fort Worth
        initial_db = {
            "place_id_starbucks_fw1": {
                "Company": "Starbucks",
                "Exact Address": "301 Main St, Fort Worth, TX 76102",
                "Latitude": 32.7553,
                "Longitude": -97.3308,
                "Overall Score": 4.2,
                "Management Support": 4.5,
                "Environment": 4.0,
                "Scheduling Fairness": 4.1,
                "Logs": ["The shift manager at this specific downtown branch is super flexible with schedules. Great team!"]
            },
            "place_id_walmart_fw2": {
                "Company": "Walmart Supercenter",
                "Exact Address": "2900 Renaissance Sq, Fort Worth, TX 76105",
                "Latitude": 32.7258,
                "Longitude": -97.2912,
                "Overall Score": 2.8,
                "Management Support": 2.1,
                "Environment": 3.0,
                "Scheduling Fairness": 3.3,
                "Logs": ["Management here cuts hours without any notice. Disorganized compared to other branches."]
            }
        }
        save_database(initial_db)
        return initial_db

def save_database(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Set up page configurations
st.set_page_config(page_title="Workplace Location Rater", layout="wide")
st.title("🏢 Workplace Location Ratings Engine")
st.subheader("Find out how local stores treat employees—by exact address.")

# Load database file into the current browser session
db = load_database()

# Create tabs for browsing vs submitting data
tab1, tab2 = st.tabs(["🔍 Search & Visual Map", "📝 Submit Anonymous Review"])

with tab1:
    st.write("### Browse Specific Workplace Locations")
    search_query = st.text_input("Enter a company name or street to filter local pins:", "").strip().lower()
    
    # 🌍 SETUP INTERACTIVE MAP PANEL
    st.write("#### 📍 Live Employee Data Map")
    # Center map near Fort Worth
    m = folium.Map(location=[32.7555, -97.3308], zoom_start=12)
    
    filtered_locations = {}
    for pid, data in db.items():
        if search_query in data["Exact Address"].lower() or search_query in data["Company"].lower():
            filtered_locations[pid] = data
            
            # Choose pin color based on job satisfaction overall score
            if data["Overall Score"] >= 4.0:
                pin_color = "green"
            elif data["Overall Score"] >= 3.0:
                pin_color = "orange"
            else:
                pin_color = "red"
                
            # Place interactive popup pin on map coordinate
            folium.Marker(
                location=[data["Latitude"], data["Longitude"]],
                popup=f"{data['Company']} ({data['Overall Score']} ⭐)",
                tooltip=data["Company"],
                icon=folium.Icon(color=pin_color, icon="briefcase")
            ).add_to(m)
            
    # Render map interface directly on screen
    st_folium(m, width=900, height=400, key="main_map")
    
    # Process and display matching data columns below map
    for pid, data in filtered_locations.items():
        with st.container():
            st.markdown(f"### **{data['Company']}**")
            st.caption(f"📍 Location: {data['Exact Address']}")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("⭐ Overall Score", f"{data['Overall Score']} / 5.0")
            col2.metric("👔 Management", f"{data['Management Support']} / 5.0")
            col3.metric("🌱 Environment", f"{data['Environment']} / 5.0")
            col4.metric("📅 Scheduling", f"{data['Scheduling Fairness']} / 5.0")
            
            st.write("**Employee Feedback Logs:**")
            for log in data["Logs"]:
                st.info(f'"{log}"')
            st.markdown("---")

with tab2:
    st.write("### Share Your Experience at a Specific Branch")
    
    with st.form("review_form", clear_on_submit=True):
        comp = st.text_input("Company Name:")
        addr = st.text_input("Exact Physical Address:")
        
        # Simple inputs to let users plot precise pin coordinates for new branches
        col_lat, col_lon = st.columns(2)
        lat = col_lat.number_input("Latitude Coords:", value=32.75)
        lon = col_lon.number_input("Longitude Coords:", value=-97.33)
        
        st.write("Rate these factors from 1 (Poor) to 5 (Excellent):")
        m_rate = st.slider("Management Support", 1.0, 5.0, 3.0, 0.1)
        e_rate = st.slider("Workplace Environment", 1.0, 5.0, 3.0, 0.1)
        s_rate = st.slider("Scheduling & Shift Fairness", 1.0, 5.0, 3.0, 0.1)
        feedback = st.text_area("Write your anonymous workplace log:")
        
        submitted = st.form_submit_button("Submit Anonymous Data Pin")
        
        if submitted:
            if not comp or not addr:
                st.error("Both the company name and physical address are required to drop a pin.")
            else:
                uid = addr.lower().replace(" ", "_").replace(",", "")
                
                if uid not in db:
                    db[uid] = {
                        "Company": comp, "Exact Address": addr, "Latitude": lat, "Longitude": lon,
                        "Overall Score": 0.0, "Management Support": m_rate, "Environment": e_rate, 
                        "Scheduling Fairness": s_rate, "Logs": []
                    }
                    new_score = (m_rate + e_rate + s_rate) / 3
                    db[uid]["Overall Score"] = round(new_score, 1)
                else:
                    target = db[uid]
                    target["Management Support"] = round((target["Management Support"] + m_rate) / 2, 1)
                    target["Environment"] = round((target["Environment"] + e_rate) / 2, 1)
                    target["Scheduling Fairness"] = round((target["Scheduling Fairness"] + s_rate) / 2, 1)
                    target["Overall Score"] = round((target["Management Support"] + target["Environment"] + target["Scheduling Fairness"]) / 3, 1)
                
                if feedback:
                    db[uid]["Logs"].insert(0, feedback)
                    
                # Save changes instantly to permanent JSON database file
                save_database(db)
                st.success(f"Pin dropped successfully! Workplace analytics permanently saved for {comp}.")
                st.rerun()
