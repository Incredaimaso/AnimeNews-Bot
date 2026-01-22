# utils/telegraph_helper.py
from html_telegraph_poster import TelegraphPoster

class TelegraphEngine:
    def __init__(self):
        self.t = TelegraphPoster(use_api=True)
        self.t.create_api_token('AnimeNewsBot') # One-time creation

    def create_page(self, title, html_content, author_name="Mr. Duck"):
        """
        Creates a Graph.org page with full content.
        html_content can contain <img src="..."> and <iframe src="youtube...">
        """
        try:
            page = self.t.post(
                title=title,
                author=author_name,
                text=html_content
            )
            return page['url']
        except Exception as e:
            print(f"Telegraph Error: {e}")
            return None
          
