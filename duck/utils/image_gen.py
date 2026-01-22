import os
import random
import aiohttp
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

class ImageGen:
    def __init__(self):
        # Paths to your assets (User must provide these)
        self.ASSET_PATH = "duck/assets"
        self.FONTS_PATH = os.path.join(self.ASSET_PATH, "fonts")
        self.OVERLAYS_PATH = os.path.join(self.ASSET_PATH, "overlays")
        
        # Create directories if they don't exist
        os.makedirs(self.FONTS_PATH, exist_ok=True)
        os.makedirs(self.OVERLAYS_PATH, exist_ok=True)

    async def download_image(self, url):
        """Downloads image from URL into memory."""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    return Image.open(BytesIO(data)).convert("RGBA")
        return None

    def apply_random_filter(self, img):
        """Applies a random color grade/style to the image."""
        style = random.choice(["cyber", "noir", "warm", "faded", "drama"])
        
        if style == "cyber":
            # High contrast, slight blue tint
            img = ImageEnhance.Contrast(img).enhance(1.5)
            r, g, b, a = img.split()
            b = ImageEnhance.Brightness(b).enhance(1.3)
            img = Image.merge("RGBA", (r, g, b, a))
            
        elif style == "noir":
            # Black and White, high contrast
            img = img.convert("L").convert("RGBA")
            img = ImageEnhance.Contrast(img).enhance(1.8)
            
        elif style == "drama":
            # Darker, high saturation
            img = ImageEnhance.Brightness(img).enhance(0.8)
            img = ImageEnhance.Color(img).enhance(1.5)
            
        return img

    def add_overlay(self, img):
        """Adds a random texture overlay (dust, scratches) if available."""
        try:
            overlays = [f for f in os.listdir(self.OVERLAYS_PATH) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if not overlays:
                return img

            overlay_name = random.choice(overlays)
            overlay = Image.open(os.path.join(self.OVERLAYS_PATH, overlay_name)).convert("RGBA")
            
            # Resize overlay to match image
            overlay = overlay.resize(img.size)
            
            # Blend overlay (simulate "Screen" or "Overlay" mode by alpha blending)
            # We use a random alpha to make it subtle
            overlay.putalpha(random.randint(50, 150))
            
            return Image.alpha_composite(img, overlay)
        except Exception as e:
            print(f"Overlay Error: {e}")
            return img

    def draw_text(self, img, text):
        """Draws the Breaking News text."""
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        # 1. Draw a dark gradient at the bottom for readability
        gradient = Image.new('RGBA', (width, height), (0,0,0,0))
        g_draw = ImageDraw.Draw(gradient)
        # Simple semi-transparent black bar
        g_draw.rectangle([(0, height - 150), (width, height)], fill=(0, 0, 0, 200))
        img = Image.alpha_composite(img, gradient)
        draw = ImageDraw.Draw(img) # Re-init draw on new composite

        # 2. Load Font (Fallback to default if custom missing)
        try:
            fonts = [f for f in os.listdir(self.FONTS_PATH) if f.endswith(".ttf")]
            if fonts:
                font_path = os.path.join(self.FONTS_PATH, random.choice(fonts))
                font = ImageFont.truetype(font_path, 40)
                tag_font = ImageFont.truetype(font_path, 25)
            else:
                raise Exception("No fonts found")
        except:
            font = ImageFont.load_default()
            tag_font = ImageFont.load_default()

        # 3. Draw "BREAKING NEWS" Tag
        draw.text((20, height - 130), "⚡ BREAKING NEWS", font=tag_font, fill=(255, 215, 0)) # Gold color

        # 4. Draw Title (Truncate if too long)
        if len(text) > 30:
            text = text[:30] + "..."
        
        draw.text((20, height - 90), text, font=font, fill=(255, 255, 255))
        
        return img

    async def create_thumbnail(self, image_url, title):
        """Main function to call from bot."""
        img = await self.download_image(image_url)
        if not img:
            return None

        # 1. Resize to standard aspect ratio (e.g., 1080x1080 or 1280x720)
        img = img.resize((1280, 720))

        # 2. Apply Random Style
        img = self.apply_random_filter(img)

        # 3. Apply Random Overlay (Texture)
        img = self.add_overlay(img)

        # 4. Add Text
        img = self.draw_text(img, title)

        # 5. Save to bytes
        output = BytesIO()
        img.convert("RGB").save(output, format="JPEG", quality=95)
        output.seek(0)
        
        return output

# Export instance
image_generator = ImageGen()

