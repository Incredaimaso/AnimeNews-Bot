import trafilatura
from curl_cffi import requests
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class NewsScraper:
    def scrape(self, url):
        """
        Visits the URL using 'curl_cffi'. 
        SKIPS scraping for Crunchyroll (video pages cannot be scraped easily).
        """
        domain = urlparse(url).netloc

        # 🛑 BLACKLIST: Do not scrape these sites (JS Heavy / Video Players)
        if "crunchyroll.com" in domain:
            logger.warning(f"⚠️ Skipping scrape for {domain} (Video Player Detected). Using RSS summary.")
            return None

        try:
            # impersonate="chrome" mimics a real browser
            response = requests.get(url, impersonate="chrome", timeout=15)
            
            if response.status_code != 200:
                logger.error(f"❌ Failed to fetch {url} - Status: {response.status_code}")
                return None
            
            # Extract content
            result = trafilatura.extract(
                response.text, 
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
                    "text": data.get("text", ""), 
                    "image": data.get("image", None), 
                    "source": data.get("source-hostname", domain) 
                }
            return None
            
        except Exception as e:
            logger.error(f"Scraping Failed for {url}: {e}")
            return None

scraper = NewsScraper()
