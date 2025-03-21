import streamlit as st
import requests
import pandas as pd

# Configure Streamlit page
st.set_page_config(page_title="WooWonder Exporter", layout="wide")

# Sidebar: API settings
st.sidebar.title("⚙️ Settings")
api_key = st.sidebar.text_input("🔑 Enter WooWonder API Key", type="password")
base_url = st.sidebar.text_input("🌐 WooWonder API URL", "https://your-woowonder-site.com/api/")

# API Connection Test
def test_api_connection():
    if not api_key or not base_url:
        return "Not Configured"
    try:
        test_endpoint = f"{base_url}status"
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(test_endpoint, headers=headers, timeout=5)
        return "Connected" if response.status_code == 200 else f"Error {response.status_code}"
    except Exception as e:
        return f"Error: {e}"

connection_status = test_api_connection()
st.sidebar.info(f"API Connection Status: **{connection_status}**")

# Navigation options
page = st.sidebar.radio("📌 Navigation", ["🏆 Export Members", "📝 Export Posts"])

# Function to fetch multiple users' data
def fetch_users(user_ids):
    if not api_key:
        st.warning("⚠️ Please enter your API key in the sidebar.")
        return None

    url = f"{base_url}get-many-users-data"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"user_ids": ",".join(map(str, user_ids))}
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("api_status") == 200:
                return data.get("users", [])
            else:
                st.error(f"API Error: {data.get('message', 'Unknown error')}")
        else:
            st.error(f"❌ API Error {response.status_code}: {response.text}")
    except requests.RequestException as e:
        st.error(f"🚨 Connection Error: {e}")
    return None

# Function to export data
def export_data(data, filename, format_type):
    df = pd.DataFrame(data)
    if df.empty:
        st.warning("⚠️ No data available to export.")
        return

    if format_type == "CSV":
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", csv, file_name=filename, mime="text/csv")
    elif format_type == "JSON":
        json_data = df.to_json(orient="records", indent=4)
        st.download_button("📥 Download JSON", json_data, file_name=filename, mime="application/json")

# Function to display paginated table
def display_paginated_table(data, page_size=10):
    df = pd.DataFrame(data)
    total = len(df)
    if total == 0:
        st.info("No records to display.")
        return

    page_number = st.number_input("Page", min_value=1, max_value=(total // page_size) + 1, value=1, step=1)
    start_idx = (page_number - 1) * page_size
    end_idx = start_idx + page_size
    st.dataframe(df.iloc[start_idx:end_idx])
    st.write(f"Showing records {start_idx + 1} to {min(end_idx, total)} out of {total}")

# --- Main Section: Export Members ---
if page == "🏆 Export Members":
    st.title("👥 Export WooWonder Members")

    user_ids_input = st.text_area("Enter User IDs (comma-separated)", "1,2,3,4,5")
    user_ids = [uid.strip() for uid in user_ids_input.split(",") if uid.strip().isdigit()]
    
    if st.button("🔍 Fetch Members"):
        if user_ids:
            with st.spinner("Loading users data..."):
                members = fetch_users(user_ids)
            if members:
                st.success("✅ Members Data Loaded!")
                display_paginated_table(members, page_size=10)
                export_data(members, "members.csv", "CSV")
                export_data(members, "members.json", "JSON")
            else:
                st.error("No member data available.")
        else:
            st.warning("⚠️ Please enter valid user IDs.")

# --- Main Section: Export Posts ---
elif page == "📝 Export Posts":
    st.title("📝 Export WooWonder Posts")

    # Fetch and display posts (Modify this function if needed)
    st.warning("⚠️ This feature needs a valid endpoint for fetching posts.")

