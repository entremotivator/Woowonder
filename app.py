import streamlit as st
import requests
import pandas as pd

# Configure page layout and title
st.set_page_config(page_title="ZZATEM Exporter", layout="wide")

# --- Sidebar Settings ---

st.sidebar.title("⚙️ Settings")
api_key = st.sidebar.text_input("🔑 Enter WooWonder API Key", type="password")
base_url = st.sidebar.text_input("🌐 WooWonder API URL", "https://your-woowonder-site.com/api/")

# A simple API connection test to display status
def test_api_connection():
    if not api_key or not base_url:
        return "Not Configured"
    try:
        test_endpoint = f"{base_url}status"  # Adjust if your API provides a status endpoint
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(test_endpoint, headers=headers, timeout=5)
        if response.status_code == 200:
            return "Connected"
        else:
            return f"Error {response.status_code}"
    except Exception as e:
        return f"Error: {e}"

connection_status = test_api_connection()
st.sidebar.info(f"API Connection Status: **{connection_status}**")

# Navigation options
page = st.sidebar.radio("📌 Navigation", ["🏆 Export Members", "📝 Export Posts"])

# --- Helper Functions ---

@st.cache_data(show_spinner=False)
def fetch_data(endpoint, params=None):
    """
    Fetch data from the WooWonder API and return JSON.
    Caches the results to reduce redundant calls.
    """
    if not api_key:
        st.warning("⚠️ Please enter your API key in the sidebar.")
        return None

    url = f"{base_url}{endpoint}"
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"❌ API Error {response.status_code}: {response.text}")
            return None
    except requests.RequestException as e:
        st.error(f"🚨 Connection Error: {e}")
        return None

def export_data(data, filename, format_type):
    """
    Export data in CSV or JSON format using Streamlit's download button.
    """
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

def display_paginated_table(data, page_size=10):
    """
    Display a DataFrame with simple pagination.
    """
    df = pd.DataFrame(data)
    total = len(df)
    if total == 0:
        st.info("No records to display.")
        return

    # Pagination controls
    page_number = st.number_input("Page", min_value=1, max_value=(total // page_size) + 1, value=1, step=1)
    start_idx = (page_number - 1) * page_size
    end_idx = start_idx + page_size
    st.dataframe(df.iloc[start_idx:end_idx])
    st.write(f"Showing records {start_idx + 1} to {min(end_idx, total)} out of {total}")

def sort_dataframe(data, sort_by):
    """
    Sort the DataFrame based on the selected column.
    """
    df = pd.DataFrame(data)
    if sort_by in df.columns:
        df = df.sort_values(by=sort_by)
    return df

# --- Main Application Sections ---

if page == "🏆 Export Members":
    st.title("👥 Export ZZATEM Members")

    # Fetch members with a loading spinner
    with st.spinner("Loading members data..."):
        members = fetch_data("get_members")
    if members:
        st.success("✅ Members Data Loaded!")
        df_members = pd.DataFrame(members)

        # Sorting option
        sort_column = st.selectbox("Sort Members By", options=df_members.columns, index=0)
        df_members = sort_dataframe(members, sort_column)

        # Search filter for members
        search_query = st.text_input("🔍 Search Members by any field")
        if search_query:
            df_members = df_members[df_members.apply(lambda row: search_query.lower() in str(row.values).lower(), axis=1)]
        
        # Display paginated table
        display_paginated_table(df_members, page_size=10)

        # Export options for members
        st.subheader("📤 Export Members Data")
        col1, col2 = st.columns(2)
        with col1:
            export_data(df_members.to_dict(orient="records"), "members.csv", "CSV")
        with col2:
            export_data(df_members.to_dict(orient="records"), "members.json", "JSON")
    else:
        st.error("No member data available. Please check your API configuration and try again.")

elif page == "📝 Export Posts":
    st.title("📝 Export WooWonder Posts")

    # Fetch posts with a loading spinner
    with st.spinner("Loading posts data..."):
        posts = fetch_data("get_posts")
    if posts:
        st.success("✅ Posts Data Loaded!")
        df_posts = pd.DataFrame(posts)

        # Sorting option
        sort_column = st.selectbox("Sort Posts By", options=df_posts.columns, index=0)
        df_posts = sort_dataframe(posts, sort_column)

        # Search filter for posts
        search_query = st.text_input("🔍 Search Posts by content, user, etc.")
        if search_query:
            df_posts = df_posts[df_posts.apply(lambda row: search_query.lower() in str(row.values).lower(), axis=1)]
        
        # Display paginated table
        display_paginated_table(df_posts, page_size=10)

        # Export options for posts
        st.subheader("📤 Export Posts Data")
        col1, col2 = st.columns(2)
        with col1:
            export_data(df_posts.to_dict(orient="records"), "posts.csv", "CSV")
        with col2:
            export_data(df_posts.to_dict(orient="records"), "posts.json", "JSON")
    else:
        st.error("No posts data available. Please check your API configuration and try again.")





