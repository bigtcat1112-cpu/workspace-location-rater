import streamlit as st
import folium
from streamlit_folium import st_folium

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

# Workspace data sample (with exact coordinates)
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

# --- Real Interactive Map Section ---
if filtered_workspaces:
    st.write("### 🗺️ Live Workspace Map")
    
    # Create a real map centered around the DFW area
    m = folium.Map(location=[32.7767, -96.7970], zoom_start=9, control_scale=True)
    
    # Add interactive pins for each workspace
    for ws in filtered_workspaces:
        folium.Marker(
            location=[ws["lat"], ws["lon"]],
            popup=f"<b>{ws['name']}</b><br>{ws['rating']}",
            tooltip=ws["name"],
            icon=folium.Icon(color="purple", icon="briefcase", prefix="fa")
        ).add_to(m)
    
    # Render the real map on your Streamlit site
    st_folium(m, width=700, height=400)
else:
    st.warning("No workspaces found matching your search terms.")

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
