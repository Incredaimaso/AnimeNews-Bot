from google import genai
from google.genai import types
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
                # Use the specific stable version to avoid 404s
                self.model_name = "gemini-1.5-flash-002"
            else:
                self.is_active = False
        except Exception as e:
            logger.error(f"Failed to load AI Model: {e}")
            self.is_active = False

    async def _generate(self, prompt, retries=2):
        """Generates content with Rate Limit (429) handling."""
        for attempt in range(retries + 1):
            try:
                response = await self.client.aio.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                return response.text
            except Exception as e:
                error_str = str(e)
                # 429 = Rate Limit (Too Fast)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    wait_time = 20 * (attempt + 1)
                    logger.warning(f"⚠️ Rate Limit Hit (429). Sleeping for {wait_time}s...")
                    await asyncio.sleep(wait_time)
                
                # 404 = Model Not Found (Try Fallback)
                elif "404" in error_str and attempt == 0:
                    logger.warning("⚠️ Model 404. Switching to 'gemini-pro'...")
                    self.model_name = "gemini-pro"
                    # Retry immediately with new model
                    continue
                else:
                    logger.error(f"❌ AI Error: {e}")
                    return None
        return None

    async def generate_hype_caption(self, title, summary, source_name):
        # Fallback text
        fallback = f"{styler.convert(title, 'bold_sans')}\n\n{summary[:200]}..."

        if not self.is_active:
            return fallback
        
        prompt = f"""
        Act as a professional Anime News Anchor. Write a short, hype caption (max 50 words).
        Rules:
        1. NO EMOJIS.
        2. Tone: Exciting.
        3. Wrap the Anime Title in <bold> tags.
        4. Wrap impact words (like "BREAKING") in <mono> tags.
        
        News: {title} - {summary}
        Source: {source_name}
        """

        text = await self._generate(prompt)
        
        if text:
            # Fix missing tags
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
        Format this anime news into HTML for a blog.
        
        Data:
        Title: {title}
        Image: {image_url}
        Text: {full_text}

        Rules:
        1. Start with <img src="{image_url}">
        2. Use <p> for paragraphs.
        3. Use <h3> for subheadings.
        4. Return ONLY HTML.
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
