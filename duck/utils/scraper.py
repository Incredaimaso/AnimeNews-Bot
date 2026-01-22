import trafilatura
import requests
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class NewsScraper:
    def __init__(self):
        # Fake a Real Browser to bypass 403 Errors
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/"
        }

    def scrape(self, url):
        """
        Visits the URL using 'requests' with fake headers, then extracts content.
        """
        try:
            # 1. Download HTML with fake headers
            response = requests.get(url, headers=self.headers, timeout=15)
            
            # Check for 403/404 errors
            if response.status_code != 200:
                logger.error(f"❌ Failed to fetch {url} - Status: {response.status_code}")
                return None
            
            html_content = response.text

            # 2. Extract Data using Trafilatura
            # We pass the 'html_content' string directly instead of the URL
            result = trafilatura.extract(
                html_content, 
                include_images=True, 
                include_links=False,
                output_format='json',
                with_metadata=True,
                url=url # Helps trafilatura resolve relative image links
            )
            
            if result:
                import json
                data = json.loads(result)
                
                # Extract 'text' (cleaned body) and 'image' (main thumbnail)
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
