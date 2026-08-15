import json
from generator import draw_header, loadPokemonIndex
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
    # Create a drawing context for subsequent player rendering
    d = ImageDraw.Draw(im)

    #implementar forma de escolher usage entre masters, seniors e juniors futuramente
    
    total_players=usage.divisions.master

    #Começar com a ordenação dos Pokemon e fazer total 

    sorted_pokemon = sorted(
        [pokemon for pokemon in usage.pokemon if pokemon.name.strip() != ""],
        key=lambda pokemon: pokemon.usage_count,
        reverse=True
    )

    percentages=[] #percentagens de uso por ordem
    for i in range(len(sorted_pokemon)):
        pokemon=sorted_pokemon[i]
        usage_count=pokemon.usage_count
        percentages[i] = (usage_count / total_players ) * 100
   

    d = ImageDraw.Draw(im)
    
    #Escolher fonts a usar - vou colocar font_regular em tudo como placeholder

    #colocar infos de Pokémon
    pokemon_spacing_x= (im.width - 70) // 6
    pokemon_start_y= 215 # Start roughly where first player_el starts in generator.py
    pokemon_row_height = 190  # Height between rows

    pokemon_per_row=6
    path_circles="img/usage_circles.png"
    image_circles = Image.open(os.path.join(SOURCE_PATH, path_circles))
    for i in range(len(sorted_pokemon)):
        row=i
        col=i % pokemon_per_row

        #Calculate positions
        pokemon_el_x=42+(col*pokemon_spacing_x)
        pokemon_el_y=pokemon_start_y+(row*pokemon_row_height)

        #Place where each Pokémon data will be 
        im.paste(image_circles, (pokemon_el_x, pokemon_el_y), image_circles)

        #Pokémon names
        text_x = pokemon_el_x + (pokemon_spacing_x // 2) - 28
        text_y = pokemon_el_y + 133

        # Measure text size
        bbox = d.textbbox((text_x, text_y), sorted_pokemon[i].name, font=font_regular)
        text_width = bbox[2] - bbox[0]

        if text_width <= 80:
            d.text((text_x, text_y), sorted_pokemon[i].name, fill="white", anchor="mm", font=font_regular)
        else:
            sorted_name = sorted_pokemon[i].name.split(" ")
            if len(sorted_name) == 2:
                d.text((text_x, text_y - 6), sorted_name[0], fill="white", anchor="mm", font=font_regular)
                d.text((text_x, text_y + 6), sorted_name[1], fill="white", anchor="mm", font=font_regular)
            if len(sorted_name) == 3:
                bbox2 = d.textbbox((text_x, text_y), sorted_name[0] + " " + sorted_name[1], font=font_regular)
                text_width2 = bbox2[2] - bbox2[0]
                if text_width2 <= 80:
                    d.text((text_x, text_y - 6), sorted_name[0] + " " + sorted_name[1], fill="white", anchor="mm", font=font_regular)
                    d.text((text_x, text_y + 6), sorted_name[2], fill="white", anchor="mm", font=font_regular)
                else:
                    bbox3 = d.textbbox((text_x, text_y), sorted_name[1] + " " + sorted_name[2], font=font_regular)
                    text_width3 = bbox3[2] - bbox3[0]
                    if text_width3 <= 80:
                        d.text((text_x, text_y - 6), sorted_name[0], fill="white", anchor="mm", font=font_regular)
                        d.text((text_x, text_y + 6), sorted_name[1] + " " + sorted_name[2], fill="white", anchor="mm", font=font_regular)
                    else:
                        d.text((text_x, text_y - 10), sorted_name[0], fill="white", anchor="mm", font=font_regular)
                        d.text((text_x, text_y), sorted_name[1], fill="white", anchor="mm", font=font_regular)
                        d.text((text_x, text_y + 10), sorted_name[2], fill="white", anchor="mm", font=font_regular)

        #percentagens
        distance_name_percentage=10 #a definir
        pokemon_percentage_x=text_x+distance_name_percentage
        pokemon_percentage_y=text_y

        d.text((pokemon_percentage_x, pokemon_percentage_y), str(percentages[i])+"%", fill="white", anchor="mm", font=font_regular)

        #sprite
        pokemon_sprite_x=pokemon_el_x + 5 #a definir
        pokemon_sprite_y=pokemon_el_y + 5 #a definir
        
        icon_name = sorted_pokemon[i].name.lower().replace(" ", "-")
        if(icon_name == ""):
            continue
        pokemon_icon_id = pokemonindex[icon_name]

        if(not os.path.isfile(LOCAL_POKEMON_ICONS_SRC + pokemon_icon_id + ".png")):
            #print(POKEMON_ICONS_SRC + newPokemon[p].name.lower().replace(" ", "-") + ".png")
            icon_url = urlopen(POKEMON_ICONS_SRC + pokemon_icon_id + ".png")
            content = icon_url.read()
            with open(LOCAL_POKEMON_ICONS_SRC + pokemon_icon_id + ".png", "wb") as download:
                download.write(content)
        
        p_icon = Image.open(LOCAL_POKEMON_ICONS_SRC + pokemon_icon_id + ".png")
        p_icon = p_icon.convert("RGBA")
        p_icon = p_icon.resize((60,60))
        im.paste(p_icon, (pokemon_sprite_y, pokemon_sprite_y), mask=p_icon)


    return im

