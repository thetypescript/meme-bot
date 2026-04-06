from PIL import Image, ImageDraw, ImageFont, ImageOps
import textwrap
import os

class MemeGenerator:
    def __init__(self):
        self.font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if not os.path.exists(self.font_path):
            self.font_path = None

    def create_meme(self, template_path: str, top_text: str = "", bottom_text: str = "", output_path: str = "output.jpg"):
        img = Image.open(template_path)
        draw = ImageDraw.Draw(img)
        
        # Use bigger font for memes
        try:
            font_size = 60
            font = ImageFont.truetype(self.font_path, font_size) if self.font_path else ImageFont.load_default()
        except:
            font = ImageFont.load_default()

        # Draw top text
        if top_text:
            top_text = top_text.upper()
            self.draw_outlined_text(draw, top_text, (img.width//2, 80), font, font_size)

        # Draw bottom text
        if bottom_text:
            bottom_text = bottom_text.upper()
            self.draw_outlined_text(draw, bottom_text, (img.width//2, img.height - 100), font, font_size)

        img.save(output_path, quality=95)
        return output_path

    def draw_outlined_text(self, draw, text, position, font, font_size):
        x, y = position
        # Black outline
        for adj in range(-4, 5):
            for adj2 in range(-4, 5):
                draw.text((x + adj, y + adj2), text, font=font, fill=(0, 0, 0), anchor="mm")
        # White text
        draw.text((x, y), text, font=font, fill=(255, 255, 255), anchor="mm")
