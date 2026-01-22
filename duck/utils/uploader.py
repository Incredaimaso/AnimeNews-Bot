import aiohttp
import logging
from io import BytesIO

logger = logging.getLogger(__name__)

class CatboxUploader:
    def __init__(self):
        self.api_url = "https://catbox.moe/user/api.php"

    async def upload_image(self, image_data):
        """
        Uploads binary image data (bytes) to Catbox.
        Returns the new URL (str) or None.
        """
        try:
            data = aiohttp.FormData()
            data.add_field('reqtype', 'fileupload')
            data.add_field('userhash', '') # Optional: Add your userhash if you want to track uploads
            data.add_field('fileToUpload', image_data, filename='image.jpg')

            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, data=data) as response:
                    if response.status == 200:
                        url = await response.text()
                        return url.strip()
                    else:
                        logger.error(f"Catbox Upload Failed: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Upload Error: {e}")
            return None

    async def upload_from_url(self, image_url):
        """
        Downloads image from original source -> Uploads to Catbox.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    if resp.status == 200:
                        image_bytes = await resp.read()
                        return await self.upload_image(image_bytes)
        except Exception as e:
            logger.error(f"Download Error: {e}")
            return None

catbox = CatboxUploader()

