# Website to API Converter 🔌

Transform any website into a reusable API endpoint with structured data extraction.

## Features
- Extract text content, images, links, and tables from websites
- Generate persistent API endpoints
- Simple web interface for URL submission
- Programmatic access to structured data

## Installation
1. Clone repository:
```bash
git clone https://github.com/yourusername/website-to-api.git
cd website-to-api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage
1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Open `http://localhost:8501` in your browser

3. Enter a website URL to generate an API endpoint

## Deployment

### Streamlit Cloud (Recommended)
1. Create a GitHub repository with these files
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Click "New app" and connect your GitHub repository
4. Set branch to `main` and file path to `app.py`
5. Click "Deploy"

### Hugging Face Spaces
1. Create a new Space on [Hugging Face](https://huggingface.co/spaces)
2. Select "Streamlit" SDK
3. Add files through web interface or Git
4. Add `requirements.txt` with dependencies

### Other Deployment Options
- **Vercel**: Use Streamlit component
- **Heroku**: Add `Procfile` with `web: streamlit run app.py --server.port $PORT`
- **PythonAnywhere**: Upload files and run as Python script

## API Testing Examples

### Python
```python
import requests

API_KEY = "your_api_key_here"
URL = "your_streamlit_app_url_here"

response = requests.get(f"{URL}/?api_key={API_KEY}")
data = response.json()

# Print extracted content
print(data['content'])
```

### cURL
```bash
curl "https://your-streamlit-app.streamlit.app/?api_key=your_api_key"
```

## Contributing
Contributions are welcome! Please open an issue or submit a PR.

## License
MIT License