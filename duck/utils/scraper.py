import trafilatura
from curl_cffi import requests
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class NewsScraper:
    def __init__(self):
        # No complex headers needed; curl_cffi handles the impersonation
        pass

    def scrape(self, url):
        """
        Visits the URL using 'curl_cffi' to bypass Cloudflare/403s.
        """
        try:
            # impersonate="chrome" mimics a real browser's TLS signature
            response = requests.get(url, impersonate="chrome", timeout=15)
            
            # Check for 403/404 errors
            if response.status_code != 200:
                logger.error(f"❌ Failed to fetch {url} - Status: {response.status_code}")
                return None
            
            html_content = response.text

            # Extract Data using Trafilatura
            result = trafilatura.extract(
                html_content, 
                include_images=True, 
                include_links=False,
                output_format='json',
                with_metadata=True,
                url=url
            )
            
            if result:
                import json
                data = json.loads(result)
                
                return {
                    "title": data.get("title", ""),
                    "text": data.get("text", ""), 
                    "image": data.get("image", None), 
                    "source": data.get("source-hostname", urlparse(url).netloc) 
                }
            return None
            
        except Exception as e:
            logger.error(f"Scraping Failed for {url}: {e}")
            return None

scraper = NewsScraper()
