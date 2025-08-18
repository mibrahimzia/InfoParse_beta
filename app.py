import streamlit as st
from scraper import extract_content
from database import save_data, get_data
import json
import requests
import time

# Page configuration
st.set_page_config(
    page_title="Website to API Converter",
    page_icon="🔌",
    layout="wide"
)

# Main application
def main():
    st.title("🔌 Website to API Converter")
    st.markdown("Transform any website into a reusable API endpoint")
    
    tab1, tab2, tab3 = st.tabs(["Scrape Website", "API Documentation", "Test Endpoint"])
    
    with tab1:
        st.subheader("Create New API Endpoint")
        url = st.text_input("Enter Website URL:", placeholder="https://example.com")
        
        if st.button("Generate API Endpoint"):
            if not url:
                st.warning("Please enter a URL")
                st.stop()
                
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            with st.spinner("Extracting website content..."):
                start_time = time.time()
                data = extract_content(url)
                elapsed = time.time() - start_time
                
                if 'error' in data:
                    st.error(f"Error: {data['error']}")
                    if "429" in data['error']:
                        st.info("Tip: This site has anti-scraping protection. Try using a different URL or come back later.")
                else:
                    api_key = save_data(url, data)
                    base_url = st.secrets.get("BASE_URL", "https://your-app-name.streamlit.app")
                    api_url = f"{base_url}/?api_key={api_key}"
                    
                    st.success(f"API Endpoint Created in {elapsed:.2f}s!")
                    st.code(api_url, language="text")
                    
                    st.subheader("Extracted Content Preview")
                    with st.expander("View Extracted Data"):
                        st.json(data)
    
    with tab2:
        st.subheader("API Usage Guide")
        st.markdown("""
        ### Access Your Structured Data
        
        Use this endpoint to retrieve structured data:
        ```
        GET /?api_key={your_api_key}
        ```
        
        #### Example using Python:
        ```python
        import requests
        
        API_KEY = "your_generated_api_key_here"
        BASE_URL = "your_streamlit_app_url_here"
        
        response = requests.get(f"{BASE_URL}/?api_key={API_KEY}")
        
        if response.status_code == 200:
            data = response.json()
            print(data['content'][:500])  # First 500 characters
        else:
            print("Error:", response.text)
        ```
        
        #### Example using cURL:
        ```bash
        curl "https://your-streamlit-app.streamlit.app/?api_key=your_api_key"
        ```
        
        ### Common Errors
        - `429 Too Many Requests`: Website has anti-bot protection
        - `404 Not Found`: Invalid API key or expired data
        - `500 Server Error`: Problem with the extraction service
        """)
    
    with tab3:
        st.subheader("Test API Endpoint")
        api_key = st.text_input("Enter API Key:", placeholder="Paste your API key here", key="api_key_input")
        
        if st.button("Test Endpoint", key="test_button"):
            if api_key:
                with st.spinner("Fetching data..."):
                    data = get_data(api_key)
                    if data:
                        st.success("API Response Received!")
                        with st.expander("View Full Response"):
                            st.json(data)
                    else:
                        st.error("Invalid API key or data not found")
            else:
                st.warning("Please enter an API key")

# Handle API requests
query_params = st.query_params
if 'api_key' in query_params:
    api_key = query_params['api_key']
    data = get_data(api_key)
    if data:
        st.json(data)
        st.stop()
    else:
        st.error("Invalid API key")
        st.stop()

if __name__ == "__main__":
    main()
