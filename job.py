import streamlit as st

# ==============================================================================
# 1. STREAMLIT NAVIGATION SYSTEM (Prevents Infinite Loops)
# ==============================================================================
# We define the pages outside so Streamlit can register them cleanly.
home_page = st.Page("job.py", title="Workspace Rater", icon="🏠")
admin_page = st.Page("pages/admin.py", title="Staff Portal", icon="🔒")

# This check prevents the main page from crashing when it re-loads itself
if "__main__" in __name__:
    pg = st.navigation([home_page, admin_page])
    pg.run()
else:
    # ==============================================================================
    # 2. SITE CONTENT & INTERFACE (Runs inside the navigation view)
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
            st.switch_page(admin_page)

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

    for ws in workspaces:
        if search_query.lower() in ws["name"].lower() or search_query.lower() in ws["location"].lower():
            with st.container():
                st.markdown(f"### {ws['name']}")
                st.write(f"📍 Location: {ws['location']} | Score: {ws['rating']}")
                if st.button(f"View Reviews for {ws['name']}", key=ws['name']):
                    st.write("Reviews loading...")
                st.write("")

    # ==============================================================================
    # 3. SECURITY & LEGAL FOOTER
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
