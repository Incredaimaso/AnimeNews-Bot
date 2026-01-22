import google.generativeai as genai
import logging
from config import GEMINI_API_KEY
from duck.utils.text_styler import styler

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure AI
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("No GEMINI_API_KEY found in config!")

class AIEditor:
    def __init__(self):
        try:
            self.model = genai.GenerativeModel('gemini-pro')
            self.is_active = True
        except Exception as e:
            logger.error(f"Failed to load AI Model: {e}")
            self.is_active = False

    async def generate_hype_caption(self, title, summary):
        """
        Rewrites news to be hype. 
        Returns tuple: (processed_text, keywords_list)
        """
        if not self.is_active:
            return f"{title}\n\n{summary}"

        # The Prompt: Instructs AI to use specific tags for formatting
        prompt = f"""
        Act as a hype-man for an Anime News Channel. Rewrite this news into a short, punchy caption (max 60 words).
        
        Rules:
        1. NO EMOJIS (I will add them later).
        2. Tone: Exciting, Cool, Serious.
        3. Wrap the Main Anime Title in <bold> tags.
        4. Wrap impact words (like "BREAKING", "CONFIRMED") in <mono> tags.
        
        News Title: {title}
        News Summary: {summary}
        """

        try:
            response = await self.model.generate_content_async(prompt)
            raw_text = response.text
            
            # Post-Processing: Convert AI tags to our Custom Fonts
            # 1. <bold> -> Bold Sans
            while "<bold>" in raw_text:
                start = raw_text.find("<bold>") + 6
                end = raw_text.find("</bold>")
                if end == -1: break
                word = raw_text[start:end]
                raw_text = raw_text.replace(f"<bold>{word}</bold>", styler.convert(word, "bold_sans"))

            # 2. <mono> -> Monospace
            while "<mono>" in raw_text:
                start = raw_text.find("<mono>") + 6
                end = raw_text.find("</mono>")
                if end == -1: break
                word = raw_text[start:end]
                raw_text = raw_text.replace(f"<mono>{word}</mono>", styler.convert(word, "monospace"))
                
            return raw_text

        except Exception as e:
            logger.error(f"AI Generation failed: {e}")
            return f"{title}\n\n{summary}" # Fallback to original text

ai_editor = AIEditor()
