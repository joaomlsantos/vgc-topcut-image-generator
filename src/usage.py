import json
from generator import draw_header
from helper import reorder_pokemon, change_form_item, contains_cjk_characters, loadFlag
from model import Usage, PokemonStats, GameType
import io
from PIL import Image, ImageDraw, ImageFont
import os
from urllib.request import urlopen
from pathlib import Path
from database import submit_data
import base64

# Constants
SOURCE_PATH = "../img"
# POKEMON_ICONS_SRC = "https://limitlesstcg.s3.us-east-2.amazonaws.com/pokemon/gen9/"
POKEMON_ICONS_SRC = "https://img.generator.joaoabel.pt/pokemon/projectpokemon/"
ITEM_ICONS_SRC = "https://img.generator.joaoabel.pt/items/item_"
LOCAL_POKEMON_ICONS_SRC = "../img/pokemon/projectpokemon/"
LOCAL_ITEM_ICONS_SRC = "../img/items/item_"
LOCAL_TERA_ICONS_SRC = "../img/teras/"

# Fonts
font_regular = ImageFont.truetype("../fonts/Montserrat/static/Montserrat-Regular.ttf", 24)
font_bold = ImageFont.truetype("../fonts/Montserrat/static/Montserrat-Bold.ttf", 24)
font_player = ImageFont.truetype("../fonts/Montserrat/static/Montserrat-Bold.ttf", 18)
font_player_small = ImageFont.truetype("../fonts/Montserrat/static/Montserrat-Bold.ttf", 16)

font_player_JP = ImageFont.truetype("../fonts/SourceHansSans/SourceHanSans-VF.ttf", 18)
font_player_JP.set_variation_by_name("Bold")

num_player_font = ImageFont.truetype("../fonts/Edo/edo.ttf", 24)

def generateUsage(usage):
    image = genTemplate(usage)
    buf = io.BytesIO()
    image.save(buf, "PNG")
    return buf.getvalue()


def genTemplate(usage):

    template = Image.open(os.path.join(SOURCE_PATH, "fulltemplate_v2.png"))

    w = template.size[0]
    #h = template.size[1]

    ##TODO: calculate the height based on number of Pokémon
    total_p = 4
    dynamic_height = 346 + (40 * (total_p % 2)) + 151*(total_p//2) + 50

    im = Image.new("RGBA", (template.size[0], dynamic_height))

    backgroundPath = "solid_background.png" if usage.game == GameType.VGC else "solid_background_GO.png"

    background = Image.open(os.path.join(SOURCE_PATH, backgroundPath))
    background = background.convert("RGBA")
    background = background.crop((0,0,w,dynamic_height))

    if usage.image != "" and usage.show_background:
        # Decode base64 string to bytes
        image_data = base64.b64decode(usage.image)
        tour_icon = Image.open(io.BytesIO(image_data)).convert("RGBA")

        # Calculate proportional size based on background dimensions
        width, height = tour_icon.size
        max_width = int(w * 0.8)
        max_height = int(dynamic_height * 0.6)

        #Limit the height to more than 8 players based on the 8 player height
        if max_height > 533:
            max_height = 533

        width_ratio = max_width / width
        height_ratio = max_height / height
        scale_factor = min(width_ratio, height_ratio)
        
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        tour_icon = tour_icon.resize((new_width, new_height))
        
        # Reduce transparency to 80%
        alpha = tour_icon.split()[3]
        alpha = alpha.point(lambda p: int(p * 0.8))
        tour_icon.putalpha(alpha)

        # Center the image horizontally and vertically
        centered_x = (w - tour_icon.width) // 2
        centered_y = (dynamic_height - tour_icon.height + 136) // 2

        background.paste(tour_icon, (centered_x, centered_y), mask=tour_icon)

    im.paste(background, (0,0), mask=background)

    # Draw reusable header section
    draw_header(im, usage)

    #TODO: draw usage stats

    return im

