import os
import asyncio
import logging
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from huggingface_hub import InferenceClient
from config import HF_TOKEN

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageGen:
    def __init__(self):
        # 1. Setup Hugging Face Client for Stable Diffusion
        if HF_TOKEN:
            self.client = InferenceClient(token=HF_TOKEN)
            # You can swap this model for "cagliostrolab/animagine-xl-3.1" if you want 100% anime style
            self.model_id = "stabilityai/stable-diffusion-xl-base-1.0"
        else:
            self.client = None
            logger.warning("⚠️ No HF_TOKEN found! AI Image Generation disabled.")

        # 2. Setup Assets paths
        self.ASSET_PATH = "duck/assets"
        self.FONTS_PATH = os.path.join(self.ASSET_PATH, "fonts")
        os.makedirs(self.FONTS_PATH, exist_ok=True)

    async def generate_ai_image(self, prompt):
        """
        Uses Stable Diffusion to generate an image from text.
        """
        if not self.client: return None

        logger.info(f"🎨 Generating AI Image for: {prompt[:30]}...")
        
        # Enhanced Anime Prompt
        full_prompt = f"anime style, key visual, {prompt}, masterpiece, vibrant colors, high contrast, 8k, detailed background"
        negative_prompt = "blurry, low quality, ugly, text, watermark, bad anatomy, deformed"

        try:
            # We run this in a thread executor because HF's client is sync by default
            loop = asyncio.get_running_loop()
            image = await loop.run_in_executor(
                None, 
                lambda: self.client.text_to_image(
                    full_prompt, 
                    negative_prompt=negative_prompt, 
                    model=self.model_id,
                    height=768, # SDXL optimal size
                    width=1024
                )
            )
            return image
        except Exception as e:
            logger.error(f"❌ Stable Diffusion Failed: {e}")
            return None

    def get_font(self, size=40):
        try:
            fonts = [f for f in os.listdir(self.FONTS_PATH) if f.endswith(".ttf")]
            if fonts:
                return ImageFont.truetype(os.path.join(self.FONTS_PATH, fonts[0]), size)
        except:
            pass
        return ImageFont.load_default()

    def draw_overlay(self, img, title):
        """
        Applies the 'Duck's Bot' Watermark and Title Bar.
        """
        # Ensure image is RGBA
        img = img.convert("RGBA")
        width, height = img.size
        
        draw = ImageDraw.Draw(img)
        
        # --- 1. WATERMARK (Top Right) ---
        wm_text = "Duck's Bot"
        wm_font = self.get_font(size=30)
        
        # Calculate box size
        bbox = draw.textbbox((0, 0), wm_text, font=wm_font)
        w_wm = bbox[2] - bbox[0] + 20
        h_wm = bbox[3] - bbox[1] + 20
        
        x_wm = width - w_wm - 20
        y_wm = 20
        
        # Draw Black Box
        draw.rectangle([x_wm, y_wm, x_wm + w_wm, y_wm + h_wm], fill=(0, 0, 0, 180))
        # Draw Text
        draw.text((x_wm + 10, y_wm + 5), wm_text, font=wm_font, fill="white")

        # --- 2. TITLE BAR (Bottom) ---
        # Gradient Effect
        gradient = Image.new('RGBA', (width, height), (0,0,0,0))
        g_draw = ImageDraw.Draw(gradient)
        g_draw.rectangle([(0, height - 150), (width, height)], fill=(0, 0, 0, 220))
        img = Image.alpha_composite(img, gradient)
        
        # Draw Title
        draw = ImageDraw.Draw(img)
        title_font = self.get_font(size=40)
        
        # Shorten title if too long
        display_title = title[:45] + "..." if len(title) > 45 else title
        
        draw.text((30, height - 120), "⚡ BREAKING NEWS", font=self.get_font(size=25), fill="yellow")
        draw.text((30, height - 80), display_title, font=title_font, fill="white")
        
        return img

    async def create_thumbnail(self, image_url, title):
        """
        Main Handler:
        1. Tries to download real news image.
        2. If NO image -> Generates AI Art (Stable Diffusion).
        3. Applies Watermark & Title.
        """
        img = None
        
        # A. Try downloading Real Image
        if image_url:
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(image_url) as resp:
                        if resp.status == 200:
                            data = await resp.read()
                            img = Image.open(BytesIO(data))
            except Exception as e:
                logger.error(f"Download Failed: {e}")

        # B. Fallback: Use Stable Diffusion
        if not img:
            logger.info("⚠️ No image found. Generating with Stable Diffusion...")
            img = await self.generate_ai_image(title)

        # If everything failed, give up
        if not img: return None

        # C. Processing (Resize & Watermark)
        try:
            # Resize to HD standard
            img = img.resize((1280, 720), Image.Resampling.LANCZOS)
            
            # Add Watermark & Text
            final_img = self.draw_overlay(img, title)
            
            # Save to buffer
            output = BytesIO()
            final_img.convert("RGB").save(output, format="JPEG", quality=95)
            output.seek(0)
            return output
            
        except Exception as e:
            logger.error(f"Processing Error: {e}")
            return None

image_generator = ImageGen()
