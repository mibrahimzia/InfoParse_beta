import requests
from bs4 import BeautifulSoup
import pandas as pd
import readability
from htmldate import find_date
import re
from urllib.parse import urljoin
import logging

logger = logging.getLogger("webtapi.scraper")

def extract_data(url: str, plan: dict) -> dict:
    """Extract structured data based on AI-generated plan"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        results = {
            "metadata": {
                "url": url,
                "timestamp": find_date(response.text) or "Unknown",
                "status_code": response.status_code
            },
            "content": {}
        }
        
        # Extract based on AI plan
        if "text" in plan["elements"]:
            try:
                doc = readability.Document(response.text)
                results["content"]["article"] = {
                    "title": doc.title(),
                    "content": doc.summary()
                }
            except Exception as e:
                logger.warning(f"Article extraction failed: {str(e)}")
                results["content"]["text"] = [p.get_text(strip=True) for p in soup.find_all("p")]
        
        if "images" in plan["elements"]:
            images = []
            for img in soup.find_all("img"):
                src = img.get("src", "") or img.get("data-src", "")
                if not src:
                    continue
                    
                # Resolve relative URLs
                src = urljoin(url, src)
                
                images.append({
                    "src": src,
                    "alt": img.get("alt", "")[:100],
                    "width": img.get("width"),
                    "height": img.get("height")
                })
            results["content"]["images"] = images
        
        if "tables" in plan["elements"]:
            tables = []
            for i, table in enumerate(soup.find_all("table")):
                try:
                    df = pd.read_html(str(table))[0]
                    tables.append({
                        "table_index": i,
                        "html": str(table),
                        "markdown": df.to_markdown(),
                        "json": df.to_dict(orient="records")
                    })
                except Exception as e:
                    logger.debug(f"Table extraction failed: {str(e)}")
                    continue
            results["content"]["tables"] = tables
        
        if "links" in plan["elements"]:
            links = []
            for a in soup.find_all("a"):
                href = a.get("href", "")
                if not href or href.startswith(("#", "javascript:")):
                    continue
                    
                # Resolve relative URLs
                href = urljoin(url, href)
                
                links.append({
                    "text": a.get_text(strip=True)[:200],
                    "href": href
                })
            results["content"]["links"] = links
        
        # Add custom extraction based on plan filters
        if plan.get("filters"):
            custom_elements = []
            for selector in plan["filters"].get("include_selectors", []):
                for el in soup.select(selector):
                    custom_elements.append({
                        "selector": selector,
                        "text": el.get_text(strip=True),
                        "html": str(el)
                    })
            results["content"]["custom"] = custom_elements
        
        return results
        
    except requests.exceptions.RequestException as re:
        logger.error(f"Network error: {str(re)}")
        raise Exception("Network error occurred during scraping")
    except Exception as e:
        logger.error(f"Extraction failed: {str(e)}")
        raise Exception("Data extraction failed")