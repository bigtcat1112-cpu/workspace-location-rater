import streamlit as st
import folium
from streamlit_folium import st_folium
from supabase import create_client, Client

# Initialize Supabase Connection
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_supabase()

st.title("TA Workspaces - DFW Job Rater")
st.write("Explore exact job locations across DFW and find out how they really treat employees!")

# Organize the screen layout into clean, simple tabs
tab1, tab2, tab3 = st.tabs(["🗺️ Workspace Map", "✍️ Submit a Review", "📢 Recent Ratings"])

with tab1:
    st.subheader("Interactive Workspace Map")
    m = folium.Map(location=[32.7767, -96.7970], zoom_start=10)
    
    # Try to grab addresses dynamically to drop pins on the map
    try:
        pins_response = supabase.table("workspace_reviews").select("workspace_name, exact_street_address").eq("is_deleted", False).execute()
        for pin in pins_response.data:
            if pin.get('exact_street_address'):
                # Quick fallback coordinates for demo layout purposes
                folium.Marker(
                    [32.8232, -97.1739], 
                    popup=f"**{pin['workspace_name']}**", 
                    tooltip=pin['exact_street_address']
                ).add_to(m)
    except:
        folium.Marker([32.8232, -97.1739], popup="Target - Hurst", tooltip="Click for Info").add_to(m)

    st_folium(m, width=700, height=450)

with tab2:
    st.subheader("Submit an Exact Location Review")
    with st.form("review_form", clear_on_submit=True):
        workspace_name = st.text_input("Company Name (e.g., Target)")
        exact_street_address = st.text_input("Exact Location / Street Address (e.g., 1400 Precinct Line Rd, Hurst, TX)")
        rating = st.slider("Overall Rating (1 = Awful, 5 = Amazing!)", 1, 5, 3)
        
        treatment_details = st.text_area("Employee Treatment (How do managers treat staff? Schedule flexibility?)")
        specific_concerns = st.text_area("Every Concern / Red Flags (List anything future employees should watch out for)")
        comment = st.text_area("General Comments or Extra Thoughts")
        
        submit_button = st.form_submit_button("Submit Rating")

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
                st.success(f"Review for '{workspace_name}' successfully added to the live database!")
                st.rerun()
            except Exception as e:
                st.error(f"Could not save review: {e}")

with tab3:
    st.subheader("Recent Location Ratings")
    try:
        response = supabase.table("workspace_reviews").select("*").eq("is_deleted", False).order("created_at", desc=True).execute()
        live_reviews = response.data
    except Exception as e:
        st.error("Could not load recent reviews.")
        live_reviews = []

    if live_reviews:
        for rev in live_reviews:
            # Styled Card container format
            with st.container(border=True):
                st.markdown(f"### **{rev['workspace_name']}**")
                st.caption(f"📍 Location: {rev.get('exact_street_address', 'Not Specified')}")
                st.markdown(f"**Rating:** {'⭐' * rev['rating']}")
                
                if rev.get('treatment_details'):
                    st.markdown(f"🤝 **Employee Treatment:** {rev['treatment_details']}")
                if rev.get('specific_concerns'):
                    st.markdown(f"⚠️ **Concerns & Red Flags:** {rev['specific_concerns']}")
                if rev.get('comment'):
                    st.markdown(f"💬 **General Comment:** {rev['comment']}")
    else:
        st.info("No location reviews found yet. Be the first to add one above!")
