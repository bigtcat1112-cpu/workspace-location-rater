import streamlit as st
import pandas as pd

# ==============================================================================
# SITE CONTENT & INTERFACE 
# ==============================================================================
st.title("TA Workspaces 🏢")
st.write("Welcome to TA Workspaces! Search, rate, and review workspaces easily.")

# --- Quick Navigation Links ---
st.subheader("Quick Links")
col1, col2 = st.columns(2)

with col1:
    if st.button("Go to Search Hub"):
        st.info("You are already on the home hub!")

with col2:
    if st.button("Open Staff Portal"):
        st.switch_page("pages/admin.py")

# --- Workspace Database & Search Area ---
st.write("---")
st.subheader("🔍 Find a Workspace")

# Workspace data sample (Now with coordinates for mapping)
workspaces = [
    {"name": "Downtown Tech Hub", "location": "Dallas, TX", "rating": "⭐ 4.8", "lat": 32.7885, "lon": -96.8058},
    {"name": "Cozy Corner Cafe & Desk", "location": "Fort Worth, TX", "rating": "⭐ 4.5", "lat": 32.7555, "lon": -97.3308},
    {"name": "The Innovation Lab", "location": "Arlington, TX", "rating": "⭐ 4.2", "lat": 32.7301, "lon": -97.1143}
]

search_query = st.text_input("Type a city or workspace name to search:")

# Filter workspaces based on search query
filtered_workspaces = [
    ws for ws in workspaces 
    if search_query.lower() in ws["name"].lower() or search_query.lower() in ws["location"].lower()
]

# --- Interactive Map Unit ---
if filtered_workspaces:
    # Convert filtered workspaces to a Pandas DataFrame for the map widget
    map_data = pd.DataFrame(filtered_workspaces)
    
    st.write("### 🗺️ Workspace Map View")
    # Streamlit built-in map displays markers using 'lat' and 'lon' columns
    st.map(map_data[["lat", "lon"]])
else:
    st.warning("No workspaces found matching your search terms to plot on the map.")

# --- Search List Breakdown ---
st.write("### 📋 Workspace List")
for ws in filtered_workspaces:
    with st.container():
        st.markdown(f"#### {ws['name']}")
        st.write(f"📍 Location: {ws['location']} | Score: {ws['rating']}")
        if st.button(f"View Reviews for {ws['name']}", key=ws['name']):
            st.write("Reviews loading...")
        st.write("")

# ==============================================================================
# SECURITY & LEGAL FOOTER
# ==============================================================================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 12px;'>
        <strong>⚠️ ANTI-SCRAPING SECURITY ACTIVE:</strong> Automated bot tracking is enabled on this domain.<br>
        &copy; 2026 TA Workspaces. All Rights Reserved. Unauthorized data duplication is strictly prohibited.
    </div>
    """, 
    unsafe_allow_html=True
)
