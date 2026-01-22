from google import genai
import logging
from config import GEMINI_API_KEY
from duck.utils.text_styler import styler

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIEditor:
    def __init__(self):
        try:
            # Initialize the new Client
            if GEMINI_API_KEY:
                self.client = genai.Client(api_key=GEMINI_API_KEY)
                self.is_active = True
            else:
                logger.warning("⚠️ No GEMINI_API_KEY found!")
                self.is_active = False
        except Exception as e:
            logger.error(f"Failed to load AI Model: {e}")
            self.is_active = False

    async def generate_hype_caption(self, title, summary, source_name):
        """Generates the Telegram Message Caption."""
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
            # New Async Call format for google-genai
            response = await self.client.aio.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt
            )
            return self._process_tags(response.text)
        except Exception as e:
            logger.error(f"AI Caption Failed: {e}")
            return f"{styler.convert(title, 'bold_sans')}\n\n{summary}"

    async def format_article_html(self, title, full_text, image_url):
        """Rewrites the FULL article into beautiful HTML for Telegraph."""
        if not self.is_active:
            return full_text.replace("\n", "<br>")

        prompt = f"""
        You are an elite Editor for an Anime Blog.
        Format the following news text into a clean, readable HTML article.

        Input Text:
        {full_text}

        Main Image URL: {image_url}

        Rules for HTML:
        1. Start with the Main Image using <img src="{image_url}">.
        2. Use <h3> for sub-headings.
        3. Use <blockquote> for quotes.
        4. Use <b> for key names.
        5. Output ONLY the HTML string.
        """
        
        try:
            response = await self.client.aio.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt
            )
            # Cleanup markdown code blocks if AI adds them
            clean_html = response.text.replace("```html", "").replace("```", "")
            return clean_html
        except Exception as e:
            logger.error(f"AI HTML Failed: {e}")
            return full_text.replace("\n", "<br>")

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
        
