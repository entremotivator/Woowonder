import streamlit as st
import requests
import pandas as pd

# Configure Streamlit Page
st.set_page_config(page_title="WooWonder Exporter", layout="wide")

# Sidebar: API Configuration
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

# Function to fetch all users
def fetch_all_users():
    if not api_key:
        st.warning("⚠️ Please enter your API key in the sidebar.")
        return None

    users = []
    limit = 50  # Adjust based on API limits
    offset = 0
    url = f"{base_url}get-many-users-data"
    headers = {"Authorization": f"Bearer {api_key}"}

    while True:
        params = {"limit": limit, "offset": offset}
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("api_status") == 200 and data.get("users"):
                users.extend(data["users"])
                offset += limit
            else:
                break  # Stop when no more users are returned
        else:
            st.error(f"❌ API Error {response.status_code}: {response.text}")
            break

    return users

# Function to fetch posts
def fetch_all_posts():
    if not api_key:
        st.warning("⚠️ Please enter your API key in the sidebar.")
        return None

    posts = []
    limit = 50  # Adjust based on API limits
    offset = 0
    url = f"{base_url}get-posts"  # Modify this endpoint as per your API docs
    headers = {"Authorization": f"Bearer {api_key}"}

    while True:
        params = {"limit": limit, "offset": offset}
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("api_status") == 200 and data.get("posts"):
                posts.extend(data["posts"])
                offset += limit
            else:
                break  # Stop when no more posts are returned
        else:
            st.error(f"❌ API Error {response.status_code}: {response.text}")
            break

    return posts

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
    
    if st.button("🔍 Fetch All Members"):
        with st.spinner("Loading members..."):
            members = fetch_all_users()
        
        if members:
            st.success(f"✅ Loaded {len(members)} members!")
            display_paginated_table(members, page_size=10)
            export_data(members, "members.csv", "CSV")
            export_data(members, "members.json", "JSON")
        else:
            st.error("No member data available.")

# --- Main Section: Export Posts ---
elif page == "📝 Export Posts":
    st.title("📝 Export WooWonder Posts")

    if st.button("🔍 Fetch All Posts"):
        with st.spinner("Loading posts..."):
            posts = fetch_all_posts()
        
        if posts:
            st.success(f"✅ Loaded {len(posts)} posts!")
            display_paginated_table(posts, page_size=10)
            export_data(posts, "posts.csv", "CSV")
            export_data(posts, "posts.json", "JSON")
        else:
            st.error("No post data available.")


