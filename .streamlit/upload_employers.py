import streamlit as st
from supabase import create_client, Client

# 1. Grab your connected Supabase credentials
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# 2. Define the top 20 major employers in DFW
dfw_employers = [
    {"company_name": "American Airlines", "industry": "Airlines & Aerospace", "hq_city": "Fort Worth"},
    {"company_name": "Bank of America", "industry": "Financial Services", "hq_city": "Dallas"},
    {"company_name": "Baylor Scott & White Health", "industry": "Healthcare", "hq_city": "Dallas"},
    {"company_name": "AT&T", "industry": "Telecommunications", "hq_city": "Dallas"},
    {"company_name": "Lockheed Martin Aeronautics", "industry": "Defense & Aerospace", "hq_city": "Fort Worth"},
    {"company_name": "JPMorgan Chase", "industry": "Financial Services", "hq_city": "Plano"},
    {"company_name": "Southwest Airlines", "industry": "Airlines", "hq_city": "Dallas"},
    {"company_name": "Texas Health Resources", "industry": "Healthcare", "hq_city": "Arlington"},
    {"company_name": "Walmart", "industry": "Retail Logistics", "hq_city": "DFW Regional"},
    {"company_name": "Texas Instruments", "industry": "Technology & Semiconductors", "hq_city": "Dallas"},
    {"company_name": "Raytheon Technologies", "industry": "Defense & Aerospace", "hq_city": "McKinney"},
    {"company_name": "Medical City Healthcare", "industry": "Healthcare", "hq_city": "Dallas"},
    {"company_name": "Target", "industry": "Retail Logistics", "hq_city": "DFW Regional"},
    {"company_name": "Kroger", "industry": "Retail & Grocery", "hq_city": "DFW Regional"},
    {"company_name": "Fidelity Investments", "industry": "Financial Services", "hq_city": "Westlake"},
    {"company_name": "The Home Depot", "industry": "Retail & Home Improvement", "hq_city": "DFW Regional"},
    {"company_name": "Ericsson", "industry": "Telecommunications & Tech", "hq_city": "Plano"},
    {"company_name": "McDonald's Corporation", "industry": "Food Service", "hq_city": "DFW Regional"},
    {"company_name": "Brinker International", "industry": "Food Service & Hospitality", "hq_city": "Dallas"},
    {"company_name": "Infosys", "industry": "Information Technology", "hq_city": "Richardson"}
]

# 3. Push them all into your company/workspace table at once!
try:
    # Change "workspaces" to whatever your table name is (e.g., "companies")
    data, count = supabase.table("workspaces").insert(dfw_employers).execute()
    print("🚀 Success! All 20 major DFW employers have been loaded into Supabase.")
except Exception as e:
    print(f"❌ Upload failed: {e}")
