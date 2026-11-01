import streamlit as st

# Define your pages cleanly by pointing straight to the files inside your pages folder
home_page = st.Page("pages/home.py", title="Workspace Rater", icon="🏠", default=True)
admin_page = st.Page("pages/admin.py", title="Staff Portal", icon="🔒")

# Load the navigation bar
pg = st.navigation([home_page, admin_page])
pg.run()
