from huggingface_hub import InferenceClient
import logging
import re
import asyncio
from config import HF_TOKEN
from duck.utils.text_styler import styler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIEditor:
    def __init__(self):
        try:
            if HF_TOKEN:
                # 1. Use the model you requested
                # Note: If this specific ID gives trouble, fallback to "THUDM/glm-4-9b-chat"
                self.repo_id = "zai-org/GLM-4.7-Flash" 
                self.client = InferenceClient(token=HF_TOKEN)
                self.is_active = True
            else:
                logger.warning("⚠️ No HF_TOKEN found! AI features disabled.")
                self.is_active = False
        except Exception as e:
            logger.error(f"Failed to init Hugging Face Client: {e}")
            self.is_active = False

    async def _generate(self, system_instruction, user_prompt):
        """
        Uses Hugging Face 'chat_completion' API.
        This fixes the 'task not supported' error.
        """
        if not self.is_active: return None

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ]

        # Retry loop for model loading / timeouts
        for attempt in range(3):
            try:
                # We use chat_completion which works for "Conversational" models
                response = self.client.chat_completion(
                    messages,
                    model=self.repo_id,
                    max_tokens=1500,
                    temperature=0.7
                )
                
                # Extract the message content
                return response.choices[0].message.content.strip()

            except Exception as e:
                error_str = str(e).lower()
                if "loading" in error_str or "rate limit" in error_str:
                    logger.warning(f"⚠️ GLM-4 Loading/Busy (Attempt {attempt+1}). Sleeping 10s...")
                    await asyncio.sleep(10)
                elif "not supported for task" in error_str:
                    logger.error(f"❌ Model Task Error: {e}")
                    return None
                else:
                    logger.error(f"❌ HF Error: {e}")
                    return None
        return None

    async def generate_hype_caption(self, title, summary, source_name):
        # Fallback text
        fallback = f"{styler.convert(title, 'bold_sans')}\n\n{summary[:250]}..."
        
        system_prompt = (
            "You are a professional Anime News Anchor. "
            "Your style is: High Energy, Serious, Concise. "
            "Do NOT use Emojis."
        )

        user_prompt = f"""
        Write a short, hype caption (max 50 words) for this news.
        
        Rules:
        1. Wrap the Anime Title in <bold> tags.
        2. Wrap impact words (like "BREAKING") in <mono> tags.
        3. NO Markdown bold (**), use the tags provided.
        
        News Title: {title}
        Source: {source_name}
        Context: {summary}
        """

        text = await self._generate(system_prompt, user_prompt)
        
        if text:
            # Fix bolding if the model forgot
            if "<bold>" not in text and title in text:
                text = text.replace(title, f"<bold>{title}</bold>")
            return self._process_tags(text)
        
        return fallback

    async def format_article_html(self, title, full_text, image_url):
        # Fallback HTML
        clean_text = full_text.replace("\n", "<br>")
        fallback = f"<img src='{image_url}'><br><h3>{title}</h3><br><p>{clean_text}</p>"

        system_prompt = (
            "You are an expert HTML Editor for a blog. "
            "Output ONLY valid HTML code. No markdown formatting (```html)."
        )

        user_prompt = f"""
        Convert this news text into a clean HTML structure.

        Input Data:
        - Image: {image_url}
        - Title: {title}
        - Body: {full_text}

        Requirements:
        1. Start exactly with: <img src="{image_url}">
        2. Follow with: <h3>{title}</h3>
        3. Wrap paragraphs in <p> tags.
        4. Do NOT include <html>, <head>, or <body> tags.
        5. Just return the content inside the body.
        """
        
        text = await self._generate(system_prompt, user_prompt)
        
        if text:
            # Strip markdown code blocks if present
            text = text.replace("```html", "").replace("```", "").strip()
            return text
            
        return fallback

    def _process_tags(self, text):
        def replace_match(match, font_style):
            return styler.convert(match.group(1), font_style)

        text = re.sub(r'<bold>(.*?)</bold>', lambda m: replace_match(m, "bold_sans"), text, flags=re.DOTALL)
        text = re.sub(r'<mono>(.*?)</mono>', lambda m: replace_match(m, "monospace"), text, flags=re.DOTALL)
        text = re.sub(r'<small>(.*?)</small>', lambda m: replace_match(m, "small_caps"), text, flags=re.DOTALL)
        
        # Cleanup
        return text.replace("<bold>", "").replace("</bold>", "").replace("<mono>", "").replace("</mono>", "")

ai_editor = AIEditor()
