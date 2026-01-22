import trafilatura
from curl_cffi import requests
import logging
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)

class NewsScraper:
    def scrape(self, url):
        """
        Visits the URL using 'curl_cffi' to bypass Cloudflare and extracts content.
        Handles relative image URLs and blocks video players.
        """
        domain = urlparse(url).netloc
        path = urlparse(url).path

        # 🛑 BLACKLIST LOGIC
        # Block Crunchyroll Video Pages (/watch/) but ALLOW News (/news/)
        if "crunchyroll.com" in domain and "/watch/" in path:
            logger.warning(f"⚠️ Skipping Video Page: {url}")
            return None

        try:
            # 1. FETCH
            # impersonate="chrome" makes the request look exactly like a real browser
            response = requests.get(url, impersonate="chrome", timeout=15)
            
            if response.status_code != 200:
                logger.error(f"❌ Failed to fetch {url} - Status: {response.status_code}")
                return None
            
            # 2. EXTRACT
            # We pass the URL parameter so trafilatura can fix some relative links automatically
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
                
                # 3. FIX IMAGE URLS
                image_url = data.get("image", None)
                
                # If image is relative (e.g. "/assets/img.jpg"), make it absolute
                if image_url and image_url.startswith("/"):
                    image_url = urljoin(url, image_url)
                
                # If no image found in metadata, try to find in body (fallback)
                if not image_url:
                    # Trafilatura sometimes puts images in the XML output, 
                    # but for now, we trust the metadata or the feed's fallback.
                    pass

                return {
                    "title": data.get("title", ""),
                    "text": data.get("text", ""), 
                    "image": image_url, 
                    "source": data.get("source-hostname", domain) 
                }
            return None
            
        except Exception as e:
            logger.error(f"Scraping Failed for {url}: {e}")
            return None

# Export instance
scraper = NewsScraper()
