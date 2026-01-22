# utils/ai_helper.py
import google.generativeai as genai
from config import GEMINI_API_KEY
from utils.text_styler import styler

genai.configure(api_key=GEMINI_API_KEY)

class AI_Editor:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')

    async def generate_hype_caption(self, news_title, news_summary):
        """
        Rewrites news to be hype, without emojis, using tags for styling.
        """
        prompt = f"""
        Act as a professional Anime News Editor. 
        Rewrite this news into a short, hype-inducing caption (max 50 words).
        Rules:
        1. NO EMOJIS.
        2. Use a cool, serious tone.
        3. Wrap the most important keywords in <bold>...</bold> tags.
        4. Wrap the Anime/Manga name in <caps>...</caps> tags.
        
        Title: {news_title}
        Summary: {news_summary}
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            raw_text = response.text
            
            # Post-Process: Apply the Font Styles based on AI tags
            processed_text = raw_text.replace("<bold>", "").replace("</bold>", "") 
            # Note: You would write a regex here to actually extract and map
            # For simplicity, let's just map the Title manually in the main loop
            
            return raw_text # Return raw for now, we process tags in main
        except Exception:
            return f"{news_title}\n{news_summary}" # Fallback
          
