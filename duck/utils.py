# utils/text_styler.py

class TextStyler:
    def __init__(self):
        # 1. Define your Symbol Sets
        self.bullets = [
    "►", "◼", "●", "✦", "★", "✶", "✴", "❄", "➤", "➥", 
    "➦", "➧", "➨", "➩", "➪", "➯", "➱", "➲", "➳", "➼", 
    "➽", "➾", "➔", "➜", "➝", "➞", "✐", "✎", "✏", "✑", 
    "✒", "✓", "✔", "✕", "✖", "✗", "✘", "✙", "✚", "✛", 
    "✜", "✝", "✞", "✟", "✠", "✡", "✢", "✣", "✤", "✥"
]

        
        # 2. Define Font Mappings (The translation tables)
        self.fonts = {
            "bold_sans": str.maketrans(
                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
                "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵"
            ),
            "small_caps": str.maketrans(
                "abcdefghijklmnopqrstuvwxyz",
                "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
            ),
            "script": str.maketrans(
                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
                "𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩"
            ),
            "bubble": str.maketrans(
                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
                "ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ⓪①②③④⑤⑥⑦⑧⑨"
            )
        }

    def apply_style(self, text, style_name="bold_sans"):
        """Converts text to the specified font style."""
        if style_name in self.fonts:
            return text.translate(self.fonts[style_name])
        return text

    def get_random_bullet(self):
        import random
        return random.choice(self.bullets)

# Initialize
styler = TextStyler()
