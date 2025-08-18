import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import re
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(429, 500, 502, 503, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def extract_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }
    
    try:
        session = requests_retry_session()
        response = session.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Check for Cloudflare protection
        if "cloudflare" in response.headers.get("Server", "").lower():
            if response.status_code == 403 or "cf-chl-bypass" in response.text:
                return {'error': "Website protected by Cloudflare (403 Forbidden)"}
                
        if response.status_code == 429:
            return {'error': "Too many requests (429). Website has anti-scraping protection."}
            
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}
    
    try:
        soup = BeautifulSoup(response.content, 'lxml')
    except Exception as e:
        return {'error': f"HTML parsing error: {str(e)}"}
    
    # Extract metadata
    metadata = {
        'title': soup.title.string if soup.title else '',
        'description': soup.find('meta', attrs={'name': 'description'})['content'] 
                     if soup.find('meta', attrs={'name': 'description'}) else '',
        'keywords': soup.find('meta', attrs={'name': 'keywords'})['content'] 
                   if soup.find('meta', attrs={'name': 'keywords'}) else '',
        'og:title': soup.find('meta', property='og:title')['content'] 
                  if soup.find('meta', property='og:title') else '',
        'og:description': soup.find('meta', property='og:description')['content'] 
                        if soup.find('meta', property='og:description') else '',
        'og:image': soup.find('meta', property='og:image')['content'] 
                  if soup.find('meta', property='og:image') else ''
    }
    
    # Extract main content using common semantic tags
    main_content = soup.find(['article', 'main', 'div.article', 'div.content', 'div.post-content'])
    if main_content:
        text_content = ' '.join([p.get_text(strip=True) for p in main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])])
    else:
        text_content = ' '.join([p.get_text(strip=True) for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])])
    
    # Clean text content
    text_content = re.sub(r'\s+', ' ', text_content).strip()
    
    # Extract images
    images = []
    for img in soup.find_all('img'):
        if img.get('src'):
            img_url = urljoin(url, img['src'])
            images.append(img_url)
        elif img.get('data-src'):
            img_url = urljoin(url, img['data-src'])
            images.append(img_url)
    
    # Extract links
    links = []
    for a in soup.find_all('a'):
        if a.get('href'):
            link_url = urljoin(url, a['href'])
            links.append(link_url)
    
    # Extract tables
    tables = []
    for table in soup.find_all('table'):
        try:
            df = pd.read_html(str(table))[0]
            tables.append({
                'html': str(table),
                'markdown': df.to_markdown(index=False),
                'json': df.to_dict(orient='records')
            })
        except Exception:
            continue
    
    return {
        'metadata': metadata,
        'content': text_content[:10000] + "..." if len(text_content) > 10000 else text_content,
        'images': images[:50],  # Limit to first 50 images
        'links': links[:50],    # Limit to first 50 links
        'tables': tables,
        'status': 'success',
        'url': url,
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    }
