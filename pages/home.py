import streamlit as st

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

# Workspace data sample
workspaces = [
    {"name": "Downtown Tech Hub", "location": "Dallas, TX", "rating": "⭐ 4.8"},
    {"name": "Cozy Corner Cafe & Desk", "location": "Fort Worth, TX", "rating": "⭐ 4.5"},
    {"name": "The Innovation Lab", "location": "Arlington, TX", "rating": "⭐ 4.2"}
]

search_query = st.text_input("Type a city or workspace name to search:")

# Filter workspaces based on search query
filtered_workspaces = [
    ws for ws in workspaces 
    if search_query.lower() in ws["name"].lower() or search_query.lower() in ws["location"].lower()
]

# --- Interactive Map Section ---
if filtered_workspaces:
    st.write("### 🗺️ Interactive Dashboard View")
    # Using your classic layout map placeholder instead of st.map()
    st.info("💡 Tip: Use your interactive map window to click pins and view live coordinates.")
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
