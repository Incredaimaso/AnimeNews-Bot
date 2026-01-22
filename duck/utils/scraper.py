# duck/utils/scraper.py
import trafilatura
from curl_cffi import requests
import logging
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

class NewsScraper:
    def scrape(self, url):
        """
        Visits the URL using 'curl_cffi' to bypass Cloudflare.
        """
        domain = urlparse(url).netloc
        path = urlparse(url).path

        # 🛑 REFINED BLOCKLIST: Only block Video Players, allow News
        # Crunchyroll videos have '/watch/', News has '/news/'
        if "crunchyroll.com" in domain and "/watch/" in path:
            logger.warning(f"⚠️ Skipping Video Page: {url}")
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
                
                # --- FIX: RESOLVE RELATIVE IMAGE URLS ---
                image_url = data.get("image", None)
                if image_url and image_url.startswith("/"):
                    # Converts '/thumbs/img.jpg' -> 'https://site.com/thumbs/img.jpg'
                    image_url = urljoin(url, image_url)

                return {
                    "text": data.get("text", ""), 
                    "image": image_url, 
                    "source": data.get("source-hostname", domain) 
                }
            return None
            
        except Exception as e:
            logger.error(f"Scraping Failed for {url}: {e}")
            return None

scraper = NewsScraper()
