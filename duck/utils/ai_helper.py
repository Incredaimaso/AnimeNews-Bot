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
                # We use Zephyr-7B-Beta because it follows instructions perfectly
                self.repo_id = "HuggingFaceH4/zephyr-7b-beta"
                self.client = InferenceClient(model=self.repo_id, token=HF_TOKEN)
                self.is_active = True
            else:
                logger.warning("⚠️ No HF_TOKEN found in config!")
                self.is_active = False
        except Exception as e:
            logger.error(f"Failed to init Hugging Face Client: {e}")
            self.is_active = False

    async def _generate(self, prompt):
        """
        Sends prompt to Hugging Face Inference API.
        """
        if not self.is_active: return None

        # Retry loop for stability
        for attempt in range(3):
            try:
                # We use the text-generation task
                # Zephyr expects a specific chat format: <|user|>\n...\n<|assistant|>
                formatted_prompt = f"<|user|>\n{prompt}</s>\n<|assistant|>\n"

                response = self.client.text_generation(
                    formatted_prompt,
                    max_new_tokens=1024,
                    temperature=0.7,
                    return_full_text=False
                )
                return response.strip()

            except Exception as e:
                if "rate limit" in str(e).lower() or "loading" in str(e).lower():
                    logger.warning(f"⚠️ HF Busy/Loading (Attempt {attempt+1}). Sleeping 10s...")
                    await asyncio.sleep(10)
                else:
                    logger.error(f"❌ HF Error: {e}")
                    return None
        return None

    async def generate_hype_caption(self, title, summary, source_name):
        # Fallback
        fallback = f"{styler.convert(title, 'bold_sans')}\n\n{summary[:250]}..."
        
        prompt = f"""
        You are an Anime News Anchor. Write a short, hype caption (max 50 words).
        
        Rules:
        1. NO EMOJIS.
        2. Tone: Exciting, Cool.
        3. Wrap the Anime Title in <bold> tags.
        4. Wrap impact words (like "BREAKING", "CONFIRMED") in <mono> tags.
        
        News: {title}
        Source: {source_name}
        Context: {summary}
        """

        text = await self._generate(prompt)
        
        if text:
            # Cleanup if the model hallucinates extra tags
            text = text.replace("</s>", "").strip()
            # Fix missing title bolding
            if "<bold>" not in text and title in text:
                text = text.replace(title, f"<bold>{title}</bold>")
            return self._process_tags(text)
        
        return fallback

    async def format_article_html(self, title, full_text, image_url):
        # Fallback HTML
        clean_text = full_text.replace("\n", "<br>")
        fallback = f"<img src='{image_url}'><br><h3>{title}</h3><br><p>{clean_text}</p>"

        prompt = f"""
        You are an HTML Editor. Format this anime news into a clean HTML body for a blog.
        
        Input Data:
        Title: {title}
        Image URL: {image_url}
        Body Text: {full_text}

        Instructions:
        1. Start strictly with: <img src="{image_url}">
        2. Use <h3> for subheadings.
        3. Wrap paragraphs in <p> tags.
        4. Do NOT use markdown code blocks (```). Just raw HTML.
        5. Do NOT include <html>, <head>, or <body> tags. Just the content.
        """
        
        text = await self._generate(prompt)
        
        if text:
            # Remove markdown code blocks if the model adds them
            text = text.replace("```html", "").replace("```", "")
            return text.strip()
            
        return fallback

    def _process_tags(self, text):
        def replace_match(match, font_style):
            return styler.convert(match.group(1), font_style)

        text = re.sub(r'<bold>(.*?)</bold>', lambda m: replace_match(m, "bold_sans"), text, flags=re.DOTALL)
        text = re.sub(r'<mono>(.*?)</mono>', lambda m: replace_match(m, "monospace"), text, flags=re.DOTALL)
        text = re.sub(r'<small>(.*?)</small>', lambda m: replace_match(m, "small_caps"), text, flags=re.DOTALL)
        
        return text.replace("<bold>", "").replace("</bold>", "").replace("<mono>", "").replace("</mono>", "")

ai_editor = AIEditor()
