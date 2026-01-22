from google import genai
import logging
from config import GEMINI_API_KEY
from duck.utils.text_styler import styler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIEditor:
    def __init__(self):
        try:
            if GEMINI_API_KEY:
                self.client = genai.Client(api_key=GEMINI_API_KEY)
                self.is_active = True
            else:
                self.is_active = False
        except Exception as e:
            logger.error(f"Failed to load AI Model: {e}")
            self.is_active = False

    async def generate_hype_caption(self, title, summary, source_name):
        # (Keep your existing caption logic here, it was fine)
        if not self.is_active:
            return f"{styler.convert(title, 'bold_sans')}\n\n{summary}"
        
        prompt = f"Write a short, hype anime news caption for: {title}. Source: {source_name}. No emojis."
        try:
            response = await self.client.aio.models.generate_content(model='gemini-1.5-flash', contents=prompt)
            return self._process_tags(response.text)
        except:
            return title

    async def format_article_html(self, title, full_text, image_url):
        """
        Generates a RICH HTML page for Telegraph.
        """
        if not self.is_active:
            return f"<img src='{image_url}'><br><br>{full_text.replace(chr(10), '<br>')}"

        prompt = f"""
        You are an elite Editor for an Anime News Blog.
        Convert the raw text below into a structured HTML article.

        Data:
        - Title: {title}
        - Main Image: {image_url}
        - Raw Text: {full_text}

        HTML Rules:
        1. **MUST** start with the image: <img src="{image_url}">
        2. Wrap every paragraph in <p> tags.
        3. Use <h3> for subheadings.
        4. Use <blockquote> for quotes.
        5. Use <b> for key names/dates.
        6. Do NOT use markdown (no ```html). Just return the raw HTML string.
        """
        
        try:
            response = await self.client.aio.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt
            )
            # Clean formatting
            html = response.text.replace("```html", "").replace("```", "").strip()
            return html
        except Exception as e:
            logger.error(f"AI HTML Failed: {e}")
            # Fallback HTML with image
            return f"<img src='{image_url}'><br><br><p>{full_text}</p>"

    def _process_tags(self, text):
        # (Keep your existing tag helper)
        return text

ai_editor = AIEditor()
        
