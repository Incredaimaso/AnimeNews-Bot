import os
import random
import aiohttp
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

class ImageGen:
    def __init__(self):
        # Paths
        self.ASSET_PATH = "duck/assets"
        self.FONTS_PATH = os.path.join(self.ASSET_PATH, "fonts")
        self.OVERLAYS_PATH = os.path.join(self.ASSET_PATH, "overlays")
        
        # Ensure directories exist
        os.makedirs(self.FONTS_PATH, exist_ok=True)
        os.makedirs(self.OVERLAYS_PATH, exist_ok=True)

    async def download_image(self, url):
        """Downloads image from URL into memory."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        return Image.open(BytesIO(data)).convert("RGBA")
        except:
            return None
        return None

    def get_font(self, size=40):
        """Helper to load a random custom font or default."""
        try:
            fonts = [f for f in os.listdir(self.FONTS_PATH) if f.endswith(".ttf")]
            if fonts:
                font_path = os.path.join(self.FONTS_PATH, random.choice(fonts))
                return ImageFont.truetype(font_path, size)
        except:
            pass
        return ImageFont.load_default()

    def apply_random_filter(self, img):
        """Applies a random color grade."""
        style = random.choice(["cyber", "noir", "drama", "normal"])
        
        if style == "cyber":
            img = ImageEnhance.Contrast(img).enhance(1.4)
            img = ImageEnhance.Brightness(img).enhance(1.1)
        elif style == "noir":
            img = img.convert("L").convert("RGBA")
            img = ImageEnhance.Contrast(img).enhance(1.6)
        elif style == "drama":
            img = ImageEnhance.Color(img).enhance(1.5)
            img = ImageEnhance.Contrast(img).enhance(1.2)
            
        return img

    def add_overlay(self, img):
        """Adds a random texture overlay."""
        try:
            # UPDATED: Detects png, jpg, jpeg
            overlays = [f for f in os.listdir(self.OVERLAYS_PATH) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if not overlays:
                return img

            overlay_name = random.choice(overlays)
            overlay = Image.open(os.path.join(self.OVERLAYS_PATH, overlay_name)).convert("RGBA")
            overlay = overlay.resize(img.size)
            
            # Subtle blend
            overlay.putalpha(random.randint(40, 90))
            return Image.alpha_composite(img, overlay)
        except:
            return img

    def draw_text_and_watermark(self, img, title):
        """Draws the Main Title AND the Watermark."""
        width, height = img.size
        draw = ImageDraw.Draw(img)
        
        # --- 1. THE WATERMARK (Duck's Bot) ---
        watermark_text = "Duck's Bot"
        wm_font = self.get_font(size=30)
        
        # Calculate size to position it Top-Right
        # bbox returns (left, top, right, bottom)
        wm_bbox = draw.textbbox((0, 0), watermark_text, font=wm_font)
        wm_width = wm_bbox[2] - wm_bbox[0]
        wm_height = wm_bbox[3] - wm_bbox[1]
        
        # Position: Top Right with 20px padding
        x_pos = width - wm_width - 30
        y_pos = 30
        
        # Draw Black Background Box for Watermark
        padding = 10
        draw.rectangle(
            [x_pos - padding, y_pos - padding, x_pos + wm_width + padding, y_pos + wm_height + padding],
            fill=(0, 0, 0, 180)  # Semi-transparent black
        )
        
        # Draw Watermark Text
        draw.text((x_pos, y_pos), watermark_text, font=wm_font, fill=(255, 255, 255, 200)) # White text

        # --- 2. BREAKING NEWS TITLE (Bottom) ---
        # Dark Gradient at bottom
        gradient = Image.new('RGBA', (width, height), (0,0,0,0))
        g_draw = ImageDraw.Draw(gradient)
        g_draw.rectangle([(0, height - 160), (width, height)], fill=(0, 0, 0, 220))
        img = Image.alpha_composite(img, gradient)
        
        # Refresh draw object for text on top of gradient
        draw = ImageDraw.Draw(img) 

        # "BREAKING NEWS" Tag
        tag_font = self.get_font(size=25)
        draw.text((30, height - 140), "⚡ BREAKING NEWS", font=tag_font, fill=(255, 215, 0))

        # Main Title
        title_font = self.get_font(size=45)
        # Truncate title if too long
        if len(title) > 40:
            title = title[:40] + "..."
            
        draw.text((30, height - 100), title, font=title_font, fill=(255, 255, 255))
        
        return img

    async def create_thumbnail(self, image_url, title):
        """Main function."""
        img = await self.download_image(image_url)
        if not img:
            return None

        # Standardize size (HD)
        img = img.resize((1280, 720))

        # Apply Filters & Overlay
        img = self.apply_random_filter(img)
        img = self.add_overlay(img)

        # Draw Text & Watermark
        img = self.draw_text_and_watermark(img, title)

        # Output
        output = BytesIO()
        img.convert("RGB").save(output, format="JPEG", quality=95)
        output.seek(0)
        
        return output

image_generator = ImageGen()
