from generator import draw_header
from model import GameType
import io
from PIL import Image, ImageDraw, ImageFont
import os
from urllib.request import urlopen
import base64

# Constants
SOURCE_PATH = "../img"
# POKEMON_ICONS_SRC = "https://limitlesstcg.s3.us-east-2.amazonaws.com/pokemon/gen9/"
POKEMON_ICONS_SRC = "https://img.generator.joaoabel.pt/pokemon/projectpokemon/"
ITEM_ICONS_SRC = "https://img.generator.joaoabel.pt/items/item_"
LOCAL_POKEMON_ICONS_SRC = "../img/pokemon/projectpokemon/"
LOCAL_ITEM_ICONS_SRC = "../img/items/item_"
LOCAL_TERA_ICONS_SRC = "../img/teras/"

# Fonts=font_pokemon_name = ImageFont.truetype("../fonts/Montserrat/static/Montserrat-Regular.ttf", 24)
font_bold = ImageFont.truetype("../fonts/Montserrat/static/Montserrat-Bold.ttf", 24)
font_player = ImageFont.truetype("../fonts/Montserrat/static/Montserrat-Bold.ttf", 18)
font_player_small = ImageFont.truetype("../fonts/Montserrat/static/Montserrat-Bold.ttf", 16)
font_pokemon_name = ImageFont.truetype("../fonts/Montserrat/static/Montserrat-Bold.ttf", 16)
font_pokemon_name_small = ImageFont.truetype("../fonts/Montserrat/static/Montserrat-Bold.ttf", 12)
font_percentage = ImageFont.truetype("../fonts/Montserrat/static/Montserrat-Bold.ttf", 16)

font_player_JP = ImageFont.truetype("../fonts/SourceHansSans/SourceHanSans-VF.ttf", 18)
font_player_JP.set_variation_by_name("Bold")

num_player_font = ImageFont.truetype("../fonts/Edo/edo.ttf", 24)

def loadPokemonIndex():
    SOURCE_PATH = "../pokemon_clean.txt"
    index = {}
    with open(SOURCE_PATH, "r", encoding="utf8") as f:
        for line in f:
            parts = line.strip().split("|")
            if len(parts) < 4:
                continue
            name, pokemon_id, type1, type2 = parts
            index[name] = {
                "id": pokemon_id,
                "type1": type1,
                "type2": type2
            }
    return index

pokemonindex = loadPokemonIndex()

def generateUsage(usage):
    image = genTemplate(usage)
    buf = io.BytesIO()
    image.save(buf, "PNG")
    return buf.getvalue()


def genTemplate(usage):

    template = Image.open(os.path.join(SOURCE_PATH, "fulltemplate_v2.png"))

    w = template.size[0]
    #h = template.size[1]

    total_p = len(usage.pokemon)
    is_full_row=0 if total_p%6 == 0 else 1
    dynamic_height = 190 + (total_p//6 + is_full_row) * 190 + 50

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

    d = ImageDraw.Draw(im)

    sorted_pokemon = sorted(
        [pokemon for pokemon in usage.pokemon if pokemon.name.strip() != ""],
        key=lambda pokemon: pokemon.usage_count,
        reverse=True
    )

    percentages=[]
    for i in range(len(sorted_pokemon)):
        pokemon=sorted_pokemon[i]
        usage_count=pokemon.usage_count
        percentages.append(f"{(usage_count / usage.total) * 100:.1f}".removesuffix(".0"))
   

    d = ImageDraw.Draw(im)
    
    #Add Pokémon info
    pokemon_per_row=6
    pokemon_spacing_x= (im.width - 30) // pokemon_per_row
    pokemon_start_y= 215 # Start roughly where first player_el starts in generator.py
    pokemon_row_height = 190  # Height between rows

    path_element="usage_element.png"
    image_element = Image.open(os.path.join(SOURCE_PATH, path_element))
    for i in range(len(sorted_pokemon)):
        row=i // pokemon_per_row
        col=i % pokemon_per_row

        #Calculate positions
        pokemon_el_x=21+(col*pokemon_spacing_x)
        pokemon_el_y=pokemon_start_y+(row*pokemon_row_height)

        #Place where each square will be 
        im.paste(image_element, (pokemon_el_x, pokemon_el_y), mask=image_element)

        #Pokémon names
        text_x = pokemon_el_x + (pokemon_spacing_x // 2) - 5
        text_y = pokemon_el_y + 141

        #sorted_pokemon[i].name=sorted_pokemon[i].name.replace("-", " ")

        # Measure text size
        bbox = d.textbbox((text_x, text_y), sorted_pokemon[i].name, font=font_pokemon_name)
        text_width = bbox[2] - bbox[0]

        if text_width <= 130:
            d.text((text_x, text_y), sorted_pokemon[i].name, fill="white", anchor="mm", font=font_pokemon_name)
        else:
            sorted_name = sorted_pokemon[i].name.split(" ")
            if len(sorted_name) == 2:
                d.text((text_x, text_y - 10), sorted_name[0], fill="white", anchor="mm", font=font_pokemon_name)
                d.text((text_x, text_y + 6), sorted_name[1], fill="white", anchor="mm", font=font_pokemon_name)
            if len(sorted_name) == 3:
                bbox2 = d.textbbox((text_x, text_y), sorted_name[0] + " " + sorted_name[1], font=font_pokemon_name)
                text_width2 = bbox2[2] - bbox2[0]
                if text_width2 <= 130:
                    d.text((text_x, text_y - 10), sorted_name[0] + " " + sorted_name[1], fill="white", anchor="mm", font=font_pokemon_name)
                    d.text((text_x, text_y + 6), sorted_name[2], fill="white", anchor="mm", font=font_pokemon_name)
                else:
                    bbox3 = d.textbbox((text_x, text_y), sorted_name[1] + " " + sorted_name[2], font=font_pokemon_name)
                    text_width3 = bbox3[2] - bbox3[0]
                    if text_width3 <= 130:
                        d.text((text_x, text_y - 10), sorted_name[0], fill="white", anchor="mm", font=font_pokemon_name)
                        d.text((text_x, text_y + 6), sorted_name[1] + " " + sorted_name[2], fill="white", anchor="mm", font=font_pokemon_name)
                    else:
                        d.text((text_x, text_y - 10), sorted_name[0], fill="white", anchor="mm", font=font_pokemon_name_small)
                        d.text((text_x, text_y), sorted_name[1], fill="white", anchor="mm", font=font_pokemon_name_small)
                        d.text((text_x, text_y + 10), sorted_name[2], fill="white", anchor="mm", font=font_pokemon_name_small)
            if len(sorted_name) >= 4:
                d.text((text_x, text_y - 10), sorted_name[0], fill="white", anchor="mm", font=font_pokemon_name)
                d.text((text_x, text_y + 6), sorted_name[1] + " " + sorted_name[2] + " " + sorted_name[3], fill="white", anchor="mm", font=font_pokemon_name)

        #percentages
        pokemon_percentage_x=text_x+57
        pokemon_percentage_y=pokemon_el_y + 23
        
        d.text((pokemon_percentage_x, pokemon_percentage_y), str(percentages[i])+"%", fill="white", anchor="mm", font=font_percentage)

        #sprite
        icon_name = sorted_pokemon[i].name.lower().replace(" ", "-")
        if(icon_name == ""):
            continue
        pokemon_icon_id = pokemonindex[icon_name]["id"]

        if(not os.path.isfile(LOCAL_POKEMON_ICONS_SRC + pokemon_icon_id + ".png")):
            icon_url = urlopen(POKEMON_ICONS_SRC + pokemon_icon_id + ".png")
            content = icon_url.read()
            with open(LOCAL_POKEMON_ICONS_SRC + pokemon_icon_id + ".png", "wb") as download:
                download.write(content)
        
        p_icon = Image.open(LOCAL_POKEMON_ICONS_SRC + pokemon_icon_id + ".png")
        p_icon = p_icon.convert("RGBA")

        alpha=p_icon.getchannel("A")
        transparency_box=alpha.getbbox()

        sprite=p_icon.crop(transparency_box)

        scale=min(100/sprite.height, 100/sprite.width)

        new_width=int(sprite.width*scale)
        new_height=int(sprite.height*scale)

        final_sprite = sprite.resize((new_width, new_height))

        pokemon_sprite_x=pokemon_el_x + (pokemon_spacing_x // 2) + (128-new_width)//2 - 90
        pokemon_sprite_y=pokemon_el_y + (128-new_height)//2 - 6

        type1=pokemonindex[icon_name]["type1"].lower()
        type2=pokemonindex[icon_name]["type2"].lower()

        #Type 1
        type1_icon = Image.open(os.path.join(SOURCE_PATH, f"types/{type1}.png")).convert("RGBA")
        type1_icon = type1_icon.resize((26, 26))
        im.paste(type1_icon, (pokemon_el_x + 128, pokemon_el_y + 50), mask=type1_icon)

        #Type 2 se existe
        if (type2 != "null"):
            type2_icon = Image.open(os.path.join(SOURCE_PATH, f"types/{type2}.png")).convert("RGBA")
            type2_icon = type2_icon.resize((26, 26))
            im.paste(type2_icon, (pokemon_el_x + 128, pokemon_el_y + 84), mask=type2_icon)

        im.paste(final_sprite, (pokemon_sprite_x, pokemon_sprite_y), mask=final_sprite)


    return im

