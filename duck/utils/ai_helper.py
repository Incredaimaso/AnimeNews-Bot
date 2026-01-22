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
            # UPDATED: Changed from 'gemini-pro' to 'gemini-1.5-flash'
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.is_active = True if GEMINI_API_KEY else False
        except Exception as e:
            logger.error(f"Failed to load AI Model: {e}")
            self.is_active = False

    async def generate_hype_caption(self, title, summary):
        if not self.is_active:
            return f"{styler.convert(title, 'bold_sans')}\n\n{summary}"

        prompt = f"""
        Act as a hype-man for an Anime News Channel. 
        Rewrite this news into a short, punchy caption (max 60 words).
        
        Rules:
        1. NO EMOJIS.
        2. Tone: Exciting, Cool, Serious.
        3. Wrap the Main Anime Title in <bold> tags.
        4. Wrap impact words (like "BREAKING", "CONFIRMED") in <mono> tags.
        
        News Title: {title}
        News Summary: {summary}
        """

        try:
            response = await self.model.generate_content_async(prompt)
            raw_text = response.text
            
            # Post-Processing
            raw_text = self._replace_tag(raw_text, "bold", "bold_sans")
            raw_text = self._replace_tag(raw_text, "mono", "monospace")
            raw_text = self._replace_tag(raw_text, "small", "small_caps")
                
            return raw_text

        except Exception as e:
            logger.error(f"AI Generation failed: {e}")
            return f"{styler.convert(title, 'bold_sans')}\n\n{summary}"

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
