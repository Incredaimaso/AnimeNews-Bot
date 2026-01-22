from google import genai
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
                self.client = genai.Client(api_key=GEMINI_API_KEY)
                self.is_active = True
                self.model_name = "gemini-1.5-flash-latest" 
            else:
                self.is_active = False
        except Exception as e:
            logger.error(f"Failed to load AI Model: {e}")
            self.is_active = False

    async def generate_hype_caption(self, title, summary, source_name):
        """Generates the Hype Caption with Custom Fonts."""
        
        # 1. FALLBACK (If AI is off or fails)
        fallback_text = f"{styler.convert(title, 'bold_sans')}\n\n{summary[:200]}..."

        if not self.is_active:
            return fallback_text
        
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

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            text = response.text
            
            # --- AGGRESSIVE FIX: If AI forgot tags, force bold the title ---
            if "<bold>" not in text and title in text:
                text = text.replace(title, f"<bold>{title}</bold>")
            
            return self._process_tags(text)
            
        except Exception as e:
            logger.error(f"AI Caption Error: {e}")
            return fallback_text

    async def format_article_html(self, title, full_text, image_url):
        """Generates the Telegraph Page HTML."""
        
        # 1. FALLBACK HTML (If AI fails)
        # We manually split paragraphs to prevent "congested" text
        clean_text = full_text.replace("\n\n", "</p><p>").replace("\n", "<br>")
        fallback_html = (
            f"<img src='{image_url}'>"
            f"<h3>{title}</h3>"
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
        5. Use <blockquote> for quotes.
        6. Return ONLY the valid HTML string.
        """
        
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            html = response.text.replace("```html", "").replace("```", "").strip()
            
            # Validation: If result is too short or empty, use fallback
            if len(html) < 50: 
                return fallback_html
                
            return html
        except Exception as e:
            logger.error(f"AI HTML Failed: {e}")
            return fallback_html

    def _process_tags(self, text):
        """Replaces XML tags with Custom Unicode Fonts."""
        # Helper to safely replace tags using Regex (handles nested tags better)
        def replace_match(match, font_style):
            return styler.convert(match.group(1), font_style)

        # 1. <bold> -> Bold Sans
        text = re.sub(r'<bold>(.*?)</bold>', lambda m: replace_match(m, "bold_sans"), text, flags=re.DOTALL)
        
        # 2. <mono> -> Monospace
        text = re.sub(r'<mono>(.*?)</mono>', lambda m: replace_match(m, "monospace"), text, flags=re.DOTALL)
        
        # 3. <small> -> Small Caps
        text = re.sub(r'<small>(.*?)</small>', lambda m: replace_match(m, "small_caps"), text, flags=re.DOTALL)
        
        # 4. Clean up any leftover tags just in case
        text = text.replace("<bold>", "").replace("</bold>", "")
        text = text.replace("<mono>", "").replace("</mono>", "")
        
        return text

ai_editor = AIEditor()
        
