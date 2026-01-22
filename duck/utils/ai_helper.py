# duck/utils/ai_helper.py
import google.generativeai as genai
import logging
from config import GEMINI_API_KEY
from duck.utils.text_styler import styler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class AIEditor:
    def __init__(self):
        try:
            self.model = genai.GenerativeModel('gemini-pro')
            self.is_active = True if GEMINI_API_KEY else False
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
        1. NO EMOJIS (I add them later).
        2. Tone: Serious but exciting.
        3. Wrap the Anime Name in <bold> tags.
        4. Wrap impact words (like "BREAKING") in <mono> tags.
        """

        try:
            response = await self.model.generate_content_async(prompt)
            raw_text = self._process_tags(response.text)
            return raw_text
        except Exception as e:
            logger.error(f"AI Caption Failed: {e}")
            return title

    async def format_article_html(self, title, full_text, image_url):
        """
        Rewrites the FULL article into beautiful HTML for Telegraph.
        """
        if not self.is_active:
            # Fallback: Just return text with simple breaks
            return full_text.replace("\n", "<br>")

        prompt = f"""
        You are an elite Editor for an Anime Blog.
        Format the following news text into a clean, readable HTML article.

        Input Text:
        {full_text}

        Main Image URL: {image_url}

        Rules for HTML:
        1. Start with the Main Image using <img src="{image_url}">.
        2. Use <h3> for sub-headings to break up topics.
        3. Use <blockquote> for any quotes or official statements.
        4. Use <b> for key character names or dates.
        5. Use <ul><li> for lists if applicable.
        6. Do NOT use <h1> or <h2> (Telegraph uses Title for that).
        7. Keep paragraphs short (2-3 sentences max).
        
        Output ONLY the HTML string. No markdown code blocks.
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            # clean up if AI wraps it in ```html ... ```
            clean_html = response.text.replace("```html", "").replace("```", "")
            return clean_html
        except Exception as e:
            logger.error(f"AI HTML Failed: {e}")
            return full_text.replace("\n", "<br>")

    def _process_tags(self, text):
        """Helper to apply fonts."""
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
        
