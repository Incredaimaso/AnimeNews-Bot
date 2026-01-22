# duck/utils/scraper.py
import trafilatura
import logging

logger = logging.getLogger(__name__)

class NewsScraper:
    def scrape(self, url):
        """
        Visits the URL and extracts content + all images.
        """
        try:
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                return None
            
            # Extract main content using trafilatura
            # We explicitly ask for JSON to parse images easily
            result = trafilatura.extract(
                downloaded, 
                include_images=True, 
                include_links=False,
                output_format='json',
                with_metadata=True
            )
            
            if result:
                import json
                data = json.loads(result)
                
                # Extract 'text' (cleaned body) and 'image' (main thumbnail)
                # Note: trafilatura puts all image URLs it finds in the text usually, 
                # but we can also try to find them if they are separate.
                
                return {
                    "title": data.get("title", ""),
                    "text": data.get("text", ""), # The full raw text
                    "image": data.get("image", None), # Main cover image
                    "source": data.get("source-hostname", "Unknown Source") # e.g. crunchyroll.com
                }
            return None
            
        except Exception as e:
            logger.error(f"Scraping Failed for {url}: {e}")
            return None

scraper = NewsScraper()
