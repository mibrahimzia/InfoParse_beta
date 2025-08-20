from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from cachetools import TTLCache
from datetime import timedelta
import uuid
import logging
from .security import validate_url
from .ai_interpreter import parse_query
from .scraper import extract_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("webtapi")

app = FastAPI(
    title="WebToAPI Converter",
    description="Convert websites to reusable API endpoints",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache configuration
cache = TTLCache(maxsize=1000, ttl=86400)  # Default 24-hour cache

class GenerationRequest:
    def __init__(self, url: str, query: str, output_format: str, cache_hours: int):
        self.url = url
        self.query = query
        self.output_format = output_format
        self.cache_hours = cache_hours

@app.post("/generate")
async def generate_endpoint(request: Request):
    try:
        data = await request.json()
        gen_request = GenerationRequest(
            url=data.get("url"),
            query=data.get("query"),
            output_format=data.get("output_format", "JSON"),
            cache_hours=data.get("cache_hours", 24)
        )
        
        # Validate inputs
        if not gen_request.url or not gen_request.query:
            raise HTTPException(400, "Missing required parameters: url or query")
        
        # Security validation
        if not validate_url(gen_request.url):
            raise HTTPException(400, "URL failed security checks or is not publicly accessible")
        
        # Parse natural language query
        extraction_plan = parse_query(gen_request.query)
        
        # Extract data from website
        extracted_data = extract_data(gen_request.url, extraction_plan)
        
        # Create API endpoint
        endpoint_id = str(uuid.uuid4())
        cache[endpoint_id] = {
            "data": extracted_data,
            "output_format": gen_request.output_format,
            "expires": timedelta(hours=gen_request.cache_hours)
        }
        
        return JSONResponse({
            "api_endpoint": f"/api/{endpoint_id}",
            "sample_data": extracted_data
        })
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        raise HTTPException(500, "Internal server error")

@app.get("/api/{endpoint_id}")
async def get_data(endpoint_id: str):
    data = cache.get(endpoint_id)
    if not data:
        raise HTTPException(404, "Endpoint expired or not found")
    return data["data"]

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}