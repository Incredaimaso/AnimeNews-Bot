# duck/utils/scraper.py
import trafilatura
import logging

logger = logging.getLogger(__name__)

class NewsScraper:
    def scrape(self, url):
        """
        Visits the URL and extracts the FULL content and the main image.
        Returns a dictionary: {'text': ..., 'html': ..., 'image': ...}
        """
        try:
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                return None
            
            # Extract metadata (includes image)
            # We use extract() to get the main content
            result = trafilatura.extract(
                downloaded, 
                include_images=True, 
                include_links=True,
                output_format='json',
                with_metadata=True
            )
            
            if result:
                import json
                data = json.loads(result)
                
                # Get the HTML content for Telegraph
                html_content = trafilatura.extract(
                    downloaded, 
                    include_images=True, 
                    output_format='xml' # XML/HTML preserves structure for Telegraph
                )
                
                return {
                    "text": data.get("text", ""),
                    "image": data.get("image", None),
                    "html": html_content
                }
            return None
            
        except Exception as e:
            logger.error(f"Scraping Failed for {url}: {e}")
            return None

scraper = NewsScraper()

