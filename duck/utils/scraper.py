import trafilatura
from curl_cffi import requests
import logging
from urllib.parse import urlparse, urljoin
import re

logger = logging.getLogger(__name__)

class NewsScraper:
    def scrape(self, url):
        domain = urlparse(url).netloc
        path = urlparse(url).path

        # Block Video Pages
        if "crunchyroll.com" in domain and "/watch/" in path:
            return None

        try:
            # 1. Fetch with Chrome Impersonation
            response = requests.get(url, impersonate="chrome", timeout=15)
            if response.status_code != 200:
                logger.error(f"❌ Failed to fetch {url} - Status: {response.status_code}")
                return None
            
            html = response.text

            # 2. Try Trafilatura Extraction first
            result = trafilatura.extract(
                html, 
                include_images=True, 
                include_links=False, 
                output_format='json',
                with_metadata=True,
                url=url
            )
            
            data = {}
            if result:
                import json
                data = json.loads(result)

            # 3. MANUAL FALLBACK (If trafilatura failed to get text)
            # This fixes the "discarding data" error for Crunchyroll
            if not data.get("text"):
                logger.warning(f"⚠️ Trafilatura failed for {url}. Attempting manual meta extraction.")
                
                # Extract Description from <meta name="description">
                desc_match = re.search(r'<meta name="description" content="(.*?)"', html, re.IGNORECASE)
                og_desc_match = re.search(r'<meta property="og:description" content="(.*?)"', html, re.IGNORECASE)
                
                found_text = desc_match.group(1) if desc_match else (og_desc_match.group(1) if og_desc_match else "")
                
                if found_text:
                    data["text"] = found_text
                    data["title"] = "Anime News" # Will be overwritten by RSS title usually
                    # Extract Image from <meta property="og:image">
                    img_match = re.search(r'<meta property="og:image" content="(.*?)"', html, re.IGNORECASE)
                    if img_match:
                        data["image"] = img_match.group(1)

            # 4. Final Data Cleanup
            if data.get("text"):
                image_url = data.get("image", None)
                if image_url and image_url.startswith("/"):
                    image_url = urljoin(url, image_url)

                return {
                    "text": data.get("text"),
                    "image": image_url,
                    "source": data.get("source-hostname", domain)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Scraping Failed for {url}: {e}")
            return None

scraper = NewsScraper()
