from google import genai
from google.genai import types
import logging
import re
from config import GEMINI_API_KEY
from duck.utils.text_styler import styler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIEditor:
    def __init__(self):
        try:
            if GEMINI_API_KEY:
                # Initialize Client
                self.client = genai.Client(api_key=GEMINI_API_KEY)
                self.is_active = True
                
                # USE 'gemini-1.5-flash' (No 'latest', no 'pro', just the base name)
                # This is the most stable identifier currently.
                self.model_name = "gemini-1.5-flash"
            else:
                self.is_active = False
        except Exception as e:
            logger.error(f"Failed to load AI Model: {e}")
            self.is_active = False

    async def _generate(self, prompt):
        """Helper to generate content with fallback."""
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            logger.warning(f"⚠️ Primary Model Failed ({e}). Trying fallback 'gemini-2.0-flash-exp'...")
            try:
                # If 1.5 fails, try 2.0 (newer, might work if your key is new)
                response = await self.client.aio.models.generate_content(
                    model='gemini-2.0-flash-exp',
                    contents=prompt
                )
                return response.text
            except Exception as e2:
                logger.error(f"❌ All AI Models Failed: {e2}")
                return None

    async def generate_hype_caption(self, title, summary, source_name):
        """Generates the Hype Caption with Custom Fonts."""
        
        # Default Fallback (Styled)
        fallback = f"{styler.convert(title, 'bold_sans')}\n\n{summary[:200]}..."

        if not self.is_active:
            return fallback
        
        prompt = f"""
        Act as a professional Anime News Anchor. Write a short, hype caption (max 50 words).
        
        Input Data:
        - Title: {title}
        - Summary: {summary}
        - Source: {source_name}
        
        Rules:
        1. NO EMOJIS.
        2. Tone: Serious but exciting.
        3. **CRITICAL:** You MUST wrap the Anime Title in <bold> tags.
        4. **CRITICAL:** You MUST wrap impact words (like "BREAKING") in <mono> tags.
        """

        text = await self._generate(prompt)
        
        if text:
            # Aggressive Fix: Ensure title is bolded if AI forgot
            if "<bold>" not in text and title in text:
                text = text.replace(title, f"<bold>{title}</bold>")
            return self._process_tags(text)
        
        return fallback

    async def format_article_html(self, title, full_text, image_url):
        """Generates the Telegraph Page HTML."""
        
        # Manual Fallback HTML
        clean_text = full_text.replace("\n", "<br>")
        fallback_html = (
            f"<img src='{image_url}'><br>"
            f"<h3>{title}</h3><br>"
            f"<p>{clean_text}</p>"
        )

        if not self.is_active:
            return fallback_html

        prompt = f"""
        You are an elite Editor for an Anime News Blog.
        Convert the raw text below into a structured HTML article for Telegraph.

        Data:
        - Title: {title}
        - Main Image: {image_url}
        - Raw Text: {full_text}

        HTML Rules:
        1. Start with: <img src="{image_url}">
        2. **CRITICAL:** Split the text into multiple short paragraphs using <p> tags. 
        3. Do NOT produce one giant block of text.
        4. Use <h3> for subheadings.
        5. Return ONLY the valid HTML string.
        """
        
        text = await self._generate(prompt)
        
        if text:
            return text.replace("```html", "").replace("```", "").strip()
            
        return fallback_html

    def _process_tags(self, text):
        def replace_match(match, font_style):
            return styler.convert(match.group(1), font_style)

        text = re.sub(r'<bold>(.*?)</bold>', lambda m: replace_match(m, "bold_sans"), text, flags=re.DOTALL)
        text = re.sub(r'<mono>(.*?)</mono>', lambda m: replace_match(m, "monospace"), text, flags=re.DOTALL)
        text = re.sub(r'<small>(.*?)</small>', lambda m: replace_match(m, "small_caps"), text, flags=re.DOTALL)
        
        return text.replace("<bold>", "").replace("</bold>", "").replace("<mono>", "").replace("</mono>", "")

ai_editor = AIEditor()
