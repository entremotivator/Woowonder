import streamlit as st
import requests
import pandas as pd

# Set Streamlit page configuration
st.set_page_config(page_title="WooWonder Member Exporter", layout="wide")

# Sidebar: API Configuration
st.sidebar.title("⚙️ API Configuration")
api_key = st.sidebar.text_input("🔑 Enter API Access Token", type="password")
base_url = st.sidebar.text_input("🌐 WooWonder API URL", "http://your-site.com/api/")

# Headers to prevent redirection issues
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Pagination settings
PAGE_SIZE = 20  # Limit to 20 users per API call
current_offset = st.session_state.get("offset", 0)

# Function to fetch 20 members at a time
def fetch_members(offset):
    if not api_key or not base_url:
        st.warning("⚠️ Please enter API details in the sidebar.")
        return []

    url = f"{base_url}/get-many-users-data?access_token={api_key}"
    params = {"limit": PAGE_SIZE, "offset": offset}
    
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("api_status") == 200 and "users" in data:
            return data["users"]
        else:
            return []
    except requests.exceptions.TooManyRedirects:
        st.error("❌ Too Many Redirects. Check your API URL.")
        return []
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API Error: {e}")
        return []

# UI: Display Members
st.title("👥 WooWonder Member Exporter")

if st.button("🔍 Fetch 20 Members"):
    with st.spinner("Fetching members..."):
        members = fetch_members(current_offset)
        if members:
            st.session_state["offset"] = current_offset + PAGE_SIZE  # Update offset for next batch
            st.success(f"✅ Loaded {len(members)} members!")
            df = pd.DataFrame(members)
            st.dataframe(df)
            
            # Export Options
            csv = df.to_csv(index=False).encode("utf-8")
            json_data = df.to_json(orient="records", indent=4)
            st.download_button("📥 Download CSV", csv, "members.csv", mime="text/csv")
            st.download_button("📥 Download JSON", json_data, "members.json", mime="application/json")
        else:
            st.warning("⚠️ No more members found.")





