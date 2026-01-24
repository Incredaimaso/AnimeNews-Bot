from google import genai
import logging
import re
import asyncio
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
                # NEW PRIORITY ORDER:
                # 1. Flash (High Rate Limits, Stable)
                # 2. Flash-8b (Fastest, High Limits)
                # 3. 2.0-Exp (Smartest, but LOW Limits - Use as backup)
                self.model_queue = [
                    "gemini-1.5-flash", 
                    "gemini-1.5-flash-8b",
                    "gemini-2.0-flash-exp"
                ]
            else:
                self.is_active = False
        except Exception as e:
            logger.error(f"Failed to load AI Client: {e}")
            self.is_active = False

    async def _generate(self, prompt):
        """
        Tries every model in the queue. 
        If one fails (404 or 429), it immediately moves to the next.
        """
        for model_name in self.model_queue:
            try:
                # logger.info(f"🤖 Trying AI Model: {model_name}...")
                response = await self.client.aio.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                return response.text

            except Exception as e:
                error_str = str(e)
                
                # Check for common errors
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    logger.warning(f"⚠️ Quota Limit on {model_name}. Switching...")
                    continue # Skip to next model immediately
                
                elif "404" in error_str or "NOT_FOUND" in error_str:
                    logger.warning(f"⚠️ Model {model_name} not found. Switching...")
                    continue # Skip to next model
                
                else:
                    logger.error(f"❌ Error on {model_name}: {e}")
                    continue # Try next model anyway

        logger.error("❌ All AI Models failed.")
        return None

    async def generate_hype_caption(self, title, summary, source_name):
        # Fallback (Styled)
        fallback = f"{styler.convert(title, 'bold_sans')}\n\n{summary[:250]}..."

        if not self.is_active:
            return fallback
        
        prompt = f"""
        Act as a professional Anime News Anchor. Write a short, hype caption (max 50 words).
        Rules:
        1. NO EMOJIS.
        2. Tone: Exciting, Cool.
        3. Wrap the Anime Title in <bold> tags.
        4. Wrap impact words (like "BREAKING") in <mono> tags.
        
        News: {title}
        Source: {source_name}
        Context: {summary}
        """

        text = await self._generate(prompt)
        
        if text:
            # Fix missing tags logic
            if "<bold>" not in text and title in text:
                text = text.replace(title, f"<bold>{title}</bold>")
            return self._process_tags(text)
        
        return fallback

    async def format_article_html(self, title, full_text, image_url):
        # Fallback HTML
        clean_text = full_text.replace("\n", "<br>")
        fallback_html = (
            f"<img src='{image_url}'><br>"
            f"<h3>{title}</h3><br>"
            f"<p>{clean_text}</p>"
        )

        if not self.is_active:
            return fallback_html

        prompt = f"""
        Format this anime news into HTML for a Telegraph blog post.
        
        Data:
        Title: {title}
        Image: {image_url}
        Text: {full_text}

        Rules:
        1. Start with <img src="{image_url}">
        2. Split text into short <p> paragraphs.
        3. Use <h3> for subheadings.
        4. Return ONLY valid HTML.
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
