import streamlit as st
import folium
from streamlit_folium import st_folium
from supabase import create_client, Client

# 1. Initialize Supabase Connection
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_supabase()

st.title("TA Workspaces - DFW Job Rater")
st.write("Explore exact job locations across DFW and find out how they really treat employees!")

# 2. Interactive Map Component
st.subheader("Workspace Location Map")
m = folium.Map(location=[32.7767, -96.7970], zoom_start=10)

# Add our existing workspace marker tags
folium.Marker(
    [32.8232, -97.1739], 
    popup="Target - Hurst (Example)", 
    tooltip="Click for Info"
).add_to(m)

st_folium(m, width=700, height=450)

st.markdown("---")

# 3. Live User Submission Form with Specifics
st.subheader("Submit an Exact Location Review")

with st.form("review_form", clear_on_submit=True):
    workspace_name = st.text_input("Company Name (e.g., Target)")
    exact_street_address = st.text_input("Exact Location / Street Address (e.g., 1400 Precinct Line Rd, Hurst, TX)")
    rating = st.slider("Overall Rating (1 = Awful, 5 = Amazing!)", 1, 5, 3)
    
    treatment_details = st.text_area("Employee Treatment (How do managers treat staff? Schedule flexibility?)")
    specific_concerns = st.text_area("Every Concern / Red Flags (List anything future employees should watch out for)")
    comment = st.text_area("General Comments or Extra Thoughts")
    
    submit_button = st.form_submit_button("Submit Rating")

# Handle database submission
if submit_button:
    if workspace_name.strip() == "" or exact_street_address.strip() == "":
        st.warning("Please type in both the Company Name and the Exact Location before submitting!")
    else:
        new_row = {
            "workspace_name": workspace_name,
            "exact_street_address": exact_street_address,
            "rating": rating,
            "treatment_details": treatment_details,
            "specific_concerns": specific_concerns,
            "comment": comment
        }
        try:
            supabase.table("workspace_reviews").insert(new_row).execute()
            st.success(f"Review for '{workspace_name}' at {exact_street_address} successfully added to the live database!")
            st.rerun()  # Refreshes the page to show the new review instantly below!
        except Exception as e:
            st.error(f"Could not connect to database: {e}")

st.markdown("---")

# 4. Live Review Feed (Displaying the Data)
st.subheader("Recent Location Ratings")

try:
    response = supabase.table("workspace_reviews").select("*").order("created_at", desc=True).execute()
    live_reviews = response.data
except Exception as e:
    st.error("Could not load recent reviews.")
    live_reviews = []

if live_reviews:
    for rev in live_reviews:
        with st.container():
            st.markdown(f"### **{rev['workspace_name']}**")
            st.caption(f"📍 Location: {rev.get('exact_street_address', 'Not Specified')}")
            st.markdown(f"**Rating:** {'⭐' * rev['rating']}")
            
            if rev.get('treatment_details'):
                st.markdown(f"🤝 **Employee Treatment:** {rev['treatment_details']}")
            if rev.get('specific_concerns'):
                st.markdown(f"⚠️ **Concerns & Red Flags:** {rev['specific_concerns']}")
            if rev.get('comment'):
                st.markdown(f"💬 **General Comment:** {rev['comment']}")
                
            st.markdown("<small>Submitted recently</small>", unsafe_allow_html=True)
            st.markdown("---")
else:
    st.info("No location reviews found yet. Be the first to add one above!")
