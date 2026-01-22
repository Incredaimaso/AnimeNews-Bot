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
                # FIX: Use the 'latest' alias which is safer
                self.model_name = "gemini-1.5-flash-latest" 
            else:
                self.is_active = False
        except Exception as e:
            logger.error(f"Failed to load AI Model: {e}")
            self.is_active = False

    async def generate_hype_caption(self, title, summary, source_name):
        # Fallback with Styling if AI is off
        if not self.is_active:
            return f"{styler.convert(title, 'bold_sans')}\n\n{summary}"

        prompt = f"""
        Act as a professional Anime News Anchor. Write a short, hype caption (max 50 words).
        
        Input Data:
        - Title: {title}
        - Summary: {summary}
        - Source: {source_name}
        
        Rules:
        1. NO EMOJIS.
        2. Tone: Serious but exciting.
        3. Wrap the Anime Name in <bold> tags.
        4. Wrap impact words (like "BREAKING") in <mono> tags.
        """

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return self._process_tags(response.text)
        except Exception as e:
            logger.error(f"AI Caption Error: {e}")
            # FIX: Fallback MUST still use the custom font style
            return f"{styler.convert(title, 'bold_sans')}\n\n{summary}"

    async def format_article_html(self, title, full_text, image_url):
        if not self.is_active:
            return f"<img src='{image_url}'><br><h3>{title}</h3><br>{full_text}"

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
        5. Return ONLY the HTML string.
        """
        
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            html = response.text.replace("```html", "").replace("```", "").strip()
            return html
        except Exception as e:
            logger.error(f"AI HTML Failed: {e}")
            return f"<img src='{image_url}'><br><h3>{title}</h3><br>{full_text}"

    def _process_tags(self, text):
        text = self._replace_tag(text, "bold", "bold_sans")
        text = self._replace_tag(text, "mono", "monospace")
        text = self._replace_tag(text, "small", "small_caps")
        return text

    def _replace_tag(self, text, tag_name, font_style):
        open_tag = f"<{tag_name}>"
        close_tag = f"</{tag_name}>"
        while open_tag in text:
            start = text.find(open_tag)
            end = text.find(close_tag)
            if end == -1: break
            content_start = start + len(open_tag)
            word = text[content_start:end]
            styled_word = styler.convert(word, font_style)
            text = text[:start] + styled_word + text[end + len(close_tag):]
        return text

ai_editor = AIEditor()
        
