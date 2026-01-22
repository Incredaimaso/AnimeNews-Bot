import google.generativeai as genai
import logging
import asyncio
from config import GEMINI_API_KEY
from duck.utils.text_styler import styler

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure AI
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("⚠️ No GEMINI_API_KEY found in config! AI features will be disabled.")

class AIEditor:
    def __init__(self):
        try:
            # We use 'gemini-pro' for text generation
            self.model = genai.GenerativeModel('gemini-pro')
            self.is_active = True if GEMINI_API_KEY else False
        except Exception as e:
            logger.error(f"Failed to load AI Model: {e}")
            self.is_active = False

    async def generate_hype_caption(self, title, summary):
        """
        Rewrites news to be hype. 
        Returns the styled text.
        """
        # Fallback if AI is broken or missing key
        if not self.is_active:
            return f"{styler.convert(title, 'bold_sans')}\n\n{summary}"

        # The Prompt: Instructs AI to use specific tags for formatting
        prompt = f"""
        Act as a professional hype-man for an Anime News Channel. 
        Rewrite this news into a short, punchy caption (max 60 words).
        
        Rules:
        1. NO EMOJIS (I will add them later).
        2. Tone: Exciting, Cool, Serious (like a movie trailer).
        3. Wrap the Main Anime Title (and only the title) in <bold> tags.
        4. Wrap impact words (like "BREAKING", "CONFIRMED", "NEW SEASON") in <mono> tags.
        5. Wrap studio names or dates in <small> tags.
        
        News Title: {title}
        News Summary: {summary}
        """

        try:
            # Generate response asynchronously
            response = await self.model.generate_content_async(prompt)
            raw_text = response.text
            
            # --- Post-Processing: Convert AI tags to Custom Fonts ---
            
            # 1. <bold> -> Bold Sans
            raw_text = self._replace_tag(raw_text, "bold", "bold_sans")

            # 2. <mono> -> Monospace
            raw_text = self._replace_tag(raw_text, "mono", "monospace")

            # 3. <small> -> Small Caps
            raw_text = self._replace_tag(raw_text, "small", "small_caps")
                
            return raw_text

        except Exception as e:
            logger.error(f"AI Generation failed: {e}")
            # Fallback style
            return f"{styler.convert(title, 'bold_sans')}\n\n{summary}"

    def _replace_tag(self, text, tag_name, font_style):
        """Helper to find <tag>text</tag> and replace it with styled text."""
        open_tag = f"<{tag_name}>"
        close_tag = f"</{tag_name}>"
        
        while open_tag in text:
            start = text.find(open_tag)
            end = text.find(close_tag)
            
            if end == -1: break # Safety break if closing tag missing
            
            # Extract the word inside tags
            content_start = start + len(open_tag)
            word = text[content_start:end]
            
            # Convert word to style
            styled_word = styler.convert(word, font_style)
            
            # Replace the whole <tag>word</tag> with styled_word
            text = text[:start] + styled_word + text[end + len(close_tag):]
            
        return text

# Export a single instance
ai_editor = AIEditor()
