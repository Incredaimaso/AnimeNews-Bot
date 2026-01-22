# duck/utils/text_styler.py
import random

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

        self.separators = [
            "─ ─ ─ ─ ─ ─ ─ ─",
            "▪ ▪ ▪ ▪ ▪ ▪ ▪ ▪",
            "━━━━━━━━━━━━━━",
            "• • • • • • • •",
            "∼∼∼∼∼∼∼∼∼∼∼∼∼∼",
            "❖ ❖ ❖ ❖ ❖ ❖ ❖"
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
            ),
            "monospace": str.maketrans(
                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
                "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿"
            ),
             "fraktur": str.maketrans(
                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
                "𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ"
            )
        }

    def convert(self, text, style_name="bold_sans"):
        """Converts text to the specified font style."""
        if style_name in self.fonts:
            return text.translate(self.fonts[style_name])
        return text

    def get_random_bullet(self):
        return random.choice(self.bullets)

    def get_separator(self):
        return random.choice(self.separators)

# Initialize
styler = TextStyler()
