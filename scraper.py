import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import re

def extract_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}
    
    soup = BeautifulSoup(response.content, 'lxml')
    
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
    
    # Extract text content
    text_content = ' '.join([p.get_text(strip=True) for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])])
    
    # Extract images
    images = [urljoin(url, img['src']) for img in soup.find_all('img') if img.get('src')]
    
    # Extract links
    links = [urljoin(url, a['href']) for a in soup.find_all('a') if a.get('href')]
    
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
        except:
            continue
    
    # Clean text content
    text_content = re.sub(r'\s+', ' ', text_content).strip()
    
    return {
        'metadata': metadata,
        'content': text_content,
        'images': images,
        'links': links,
        'tables': tables,
        'status': 'success'
    }