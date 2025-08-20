import streamlit as st
import requests
import os
import threading
import time
import json
import csv
import io
from uvicorn import Config, Server
from backend.main import app as fastapi_app
from utils.ui_helpers import styled_container, render_footer

# Start FastAPI backend in a separate thread
def run_fastapi():
    config = Config(
        app=fastapi_app,
        host="0.0.0.0",
        port=8000,
        log_level="warning"
    )
    server = Server(config)
    server.run()

threading.Thread(target=run_fastapi, daemon=True).start()

# Wait for backend to initialize
time.sleep(2)

# Configure Streamlit page
st.set_page_config(
    page_title="WebToAPI Converter",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for stunning UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .header {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        padding: 1.5rem;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        color: white !important;
        margin-bottom: 2rem;
    }
    
    .card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        margin-bottom: 2rem;
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(75, 108, 183, 0.4);
    }
    
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 12px;
        padding: 1rem;
    }
    
    .success-box {
        background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
        color: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin-top: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Function to convert data to selected format
def convert_to_format(data, format_type):
    if format_type == "JSON":
        return json.dumps(data, indent=2), "application/json"
    elif format_type == "CSV":
        # Flatten the data for CSV conversion
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        if "content" in data:
            for key in data["content"]:
                if isinstance(data["content"][key], list) and len(data["content"][key]) > 0:
                    if key == "tables":
                        # Handle tables specially
                        for i, table in enumerate(data["content"][key]):
                            if "json" in table:
                                writer.writerow([f"Table {i+1}"])
                                writer.writerow(table["json"][0].keys())
                                for row in table["json"]:
                                    writer.writerow(row.values())
                                writer.writerow([])
                    else:
                        writer.writerow([key.upper()])
                        if len(data["content"][key]) > 0:
                            writer.writerow(data["content"][key][0].keys())
                            for item in data["content"][key]:
                                writer.writerow(item.values())
                        writer.writerow([])
        
        return output.getvalue(), "text/csv"
    return data, "application/json"

# Main UI
def main():
    st.markdown('<div class="header"><h1>🌐 WebToAPI Converter</h1><p>Turn websites into reusable API endpoints with AI</p></div>', 
                unsafe_allow_html=True)
    
    # URL input - only user-provided URLs
    url = st.text_input("Enter Website URL:", placeholder="https://example.com/products")
    
    query = st.text_area("What would you like to extract?", 
                        placeholder="e.g. 'All product names, prices and images' or 'Latest news headlines and links'",
                        height=120)
    
    # Advanced options
    with st.expander("⚙️ Advanced Options"):
        output_format = st.selectbox("Output Format", ["JSON", "CSV"])
        cache_duration = st.slider("Cache Duration (hours)", 1, 72, 24)
    
    # Action button
    if st.button("✨ Generate API Endpoint", use_container_width=True, type="primary"):
        if not url or not query:
            st.error("Please provide both a URL and extraction instructions")
        else:
            with st.spinner("🔍 Analyzing website and creating API..."):
                try:
                    response = requests.post(
                        "http://localhost:8000/generate",
                        json={
                            "url": url,
                            "query": query,
                            "output_format": output_format,
                            "cache_hours": cache_duration
                        },
                        timeout=120
                    )
                    
                    if response.status_code == 200:
                        res = response.json()
                        st.session_state.api_endpoint = res["api_endpoint"]
                        st.session_state.sample_data = res["sample_data"]
                        st.session_state.output_format = output_format
                        st.experimental_rerun()
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Processing failed')}")
                        
                except Exception as e:
                    st.error(f"Connection to backend failed: {str(e)}")
    
    # Results section
    if "api_endpoint" in st.session_state:
        st.markdown(f"""
        <div class="success-box">
            <h3>✅ API Endpoint Created!</h3>
            <p>Your reusable API is ready:</p>
            <code>{st.session_state.api_endpoint}</code>
        </div>
        """, unsafe_allow_html=True)
        
        # Convert data to selected format
        formatted_data, mime_type = convert_to_format(st.session_state.sample_data, st.session_state.output_format)
        
        st.markdown("### Sample Data Preview")
        
        if st.session_state.output_format == "JSON":
            st.json(st.session_state.sample_data)
        else:
            st.text(formatted_data)
        
        # Download button
        st.download_button(
            label=f"📥 Download as {st.session_state.output_format}",
            data=formatted_data,
            file_name=f"extracted_data.{st.session_state.output_format.lower()}",
            mime=mime_type
        )
        
        st.divider()
        st.markdown("### Try Your API")
        
        test_col1, test_col2 = st.columns([4, 1])
        with test_col1:
            st.code(f"""curl -X GET '{st.session_state.api_endpoint}'""", language="bash")
        with test_col2:
            if st.button("📋 Copy CURL Command", use_container_width=True):
                st.toast("Copied to clipboard!")
        
        if st.button("🔄 Test Endpoint Now", type="secondary", use_container_width=True):
            with st.spinner("Fetching data..."):
                try:
                    test_res = requests.get(f"http://localhost:8000{st.session_state.api_endpoint}")
                    
                    # Convert response to selected format
                    test_data = test_res.json()
                    test_formatted, test_mime = convert_to_format(test_data, st.session_state.output_format)
                    
                    if st.session_state.output_format == "JSON":
                        st.json(test_data)
                    else:
                        st.text(test_formatted)
                        
                    # Download button for test results
                    st.download_button(
                        label=f"📥 Download Test Results as {st.session_state.output_format}",
                        data=test_formatted,
                        file_name=f"test_results.{st.session_state.output_format.lower()}",
                        mime=test_mime
                    )
                except Exception as e:
                    st.error(f"Test failed: {str(e)}")
    
    # Footer
    render_footer()

if __name__ == "__main__":
    main()