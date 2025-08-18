import streamlit as st
from scraper import extract_content
from database import save_data, get_data
import json
import requests
from io import StringIO

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
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            with st.spinner("Extracting website content..."):
                data = extract_content(url)
                
                if 'error' in data:
                    st.error(f"Error: {data['error']}")
                else:
                    api_key = save_data(url, data)
                    api_url = f"{st.experimental_get_query_params().get('_st_base_url', [''])[0]}/?api_key={api_key}"
                    
                    st.success("API Endpoint Created Successfully!")
                    st.code(api_url, language="text")
                    
                    st.subheader("Extracted Content Preview")
                    st.json(data, expanded=False)
    
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
        data = response.json()
        
        # Access extracted content
        print(data['content'])
        print(data['images'])
        ```
        
        #### Example using cURL:
        ```bash
        curl "your_streamlit_app_url/?api_key=your_api_key"
        ```
        """)
    
    with tab3:
        st.subheader("Test API Endpoint")
        api_key = st.text_input("Enter API Key:", placeholder="Paste your API key here")
        
        if st.button("Test Endpoint"):
            if api_key:
                data = get_data(api_key)
                if data:
                    st.success("API Response Received!")
                    st.json(data)
                else:
                    st.error("Invalid API key or data not found")
            else:
                st.warning("Please enter an API key")

# Handle API requests
query_params = st.experimental_get_query_params()
if 'api_key' in query_params:
    api_key = query_params['api_key'][0]
    data = get_data(api_key)
    if data:
        st.json(data)
        st.stop()
    else:
        st.error("Invalid API key")
        st.stop()

if __name__ == "__main__":
    main()