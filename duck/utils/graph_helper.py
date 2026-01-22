from html_telegraph_poster import TelegraphPoster
import logging

logger = logging.getLogger(__name__)

class GraphHelper:
    def __init__(self):
        self.t = TelegraphPoster(use_api=True)
        # Check if we have a token or need to create one
        # Ideally store this token in config/db after first run to avoid spamming API
        try:
            self.t.create_api_token('AnimeNewsBot', 'Mr. Duck')
        except Exception as e:
            logger.error(f"Telegraph Init Failed: {e}")

    def create_page(self, title, content_html, author_name="Mr. Duck"):
        """
        Creates a Telegraph page.
        content_html: Can contain <p>, <img>, <br>, <iframe> (youtube)
        """
        try:
            page = self.t.post(
                title=title,
                author=author_name,
                text=content_html
            )
            return page['url']
        except Exception as e:
            logger.error(f"Telegraph Posting Failed: {e}")
            return None

graph_maker = GraphHelper()
