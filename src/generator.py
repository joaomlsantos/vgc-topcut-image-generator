import json
from helper import reorder_pokemon, change_form_item, contains_cjk_characters
from model import TournamentType, Player, TopCut, GameType
import io
from PIL import Image, ImageDraw, ImageFont
import os
from urllib.request import urlopen
from pathlib import Path
from database import submit_data

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


def loadItemIndex():
    SOURCE_PATH = "../items_clean.txt"
    index = {}
    f = open(SOURCE_PATH, "r", encoding="utf8")
    for l in f:
        item_id_pair = l.strip().split("|")
        fixed_id = "0" * (4 - len(item_id_pair[1])) + item_id_pair[1]
        index[item_id_pair[0]] = fixed_id
    return index


def loadPokemonIndex():
    SOURCE_PATH = "../pokemon_clean.txt"
    index = {}
    f = open(SOURCE_PATH, "r", encoding="utf8")
    for l in f:
        pokemon_id_pair = l.strip().split("|")
        index[pokemon_id_pair[0]] = pokemon_id_pair[1]
    return index


itemIndex = loadItemIndex()
pokemonindex = loadPokemonIndex()

cp_distribution = {}    # tour_type -> (points, kicker)
cp_distribution["PREMIER"] = [(30, 0), (16, 0), (12, 0), (8, 17), (6, 48), (4, 80)]
cp_distribution["MSS"] = [(50, 0), (40, 0), (32, 0), (25, 17), (20, 48), (16, 80), (13, 128)]
cp_distribution["OLDREGIONAL"] = [(200, 0), (160, 0), (130, 0), (100, 0), (80, 48), (60, 80), (50, 128), (40, 256), (30, 512), (20, 1024)]
cp_distribution["OLDINTERNATIONAL"] = [(500, 0), (400, 0), (320, 0), (250, 0), (200, 48), (160, 80), (130, 128), (100, 256), (80, 512), (60, 1024), (50, 2046)]
cp_distribution["CUP"] = [(50, 0), (40, 4), (32, 8), (25, 17), (20, 48), (16, 80), (13, 128)]
cp_distribution["CHALLENGE"] = [(15, 0), (12, 4), (10, 8), (8, 14), (6, 25), (4, 48)]
cp_distribution["REGIONAL"] = [(350, 0), (325, 4), (300,8), (280, 17), (200, 33), (160, 65), (120, 129), (80, 257), (60, 513), (40, 1025), (20, 2049)]
cp_distribution["INTERNATIONAL"] = [(500, 0), (480, 4), (420,8), (380, 17), (300, 33), (240, 65), (180, 129), (140, 257), (100, 513), (80, 1025), (40, 2049)]



def generateTopcut(topcut):
    image = genTemplate(topcut)
    buf = io.BytesIO()
    image.save(buf, "PNG")
    
    # Only submit data if all players have at least 4 pokemon with non-empty names
    if all(len([p for p in player.pokemon if p.name.strip()]) >= 4 for player in topcut.players):
        submit_data(topcut)
    
    return buf.getvalue()


def draw_header(im, topcut):
    # Paste header bar background
    header_bar = Image.open(os.path.join(SOURCE_PATH, "header_bar.png"))
    im.paste(header_bar, (0, 41))

    # Determine available tour icons
    formats = [Path(tour_img).stem for tour_img in os.listdir(os.path.join(SOURCE_PATH, "tours"))]
    if topcut.tour_type.lower() in formats:
        tour_icon = Image.open(os.path.join(SOURCE_PATH, "tours", topcut.tour_type.lower() + ".png"))
        im.paste(tour_icon, (22, 25), mask=tour_icon)

    d = ImageDraw.Draw(im)

    # Tournament name & format positioning depends on whether we have a tour icon
    if topcut.tour_type.lower() in formats:
        d.text((200, 80), topcut.tour_name, fill="white", anchor="ls", font=font_bold)
        d.text((200, 115), str(topcut.format), fill="white", anchor="ls", font=font_regular)
    else:
        d.text((60, 80), topcut.tour_name, fill="white", anchor="ls", font=font_bold)
        d.text((60, 115), str(topcut.format), fill="white", anchor="ls", font=font_regular)

    # Date placement adjusts based on long tournament names
    if len(topcut.tour_name) > 38:
        d.text((860, 115), str(topcut.date), fill="white", anchor="rs", font=font_bold)
    else:
        d.text((860, 98), str(topcut.date), fill="white", anchor="rs", font=font_bold)

    # Division labels
    d.text((940, 80), "JR", fill="white", anchor="rs", font=font_bold)
    d.text((1010, 80), "SR", fill="white", anchor="rs", font=font_bold)
    d.text((1080, 80), "MA", fill="white", anchor="rs", font=font_bold)

    # Division counts
    d.text((940, 115), str(topcut.divisions.junior), fill="white", anchor="rs", font=font_bold)
    d.text((1010, 115), str(topcut.divisions.senior), fill="white", anchor="rs", font=font_bold)
    d.text((1080, 115), str(topcut.divisions.master), fill="white", anchor="rs", font=font_bold)

    return im


def genTemplate(topcut):

    template = Image.open(os.path.join(SOURCE_PATH, "fulltemplate_v2.png"))

    w = template.size[0]
    #h = template.size[1]

    total_p = len(topcut.players) - 1
    dynamic_height = 346 + (40 * (total_p % 2)) + 151*(total_p//2) + 50

    im = Image.new("RGBA", (template.size[0], dynamic_height))

    backgroundPath = "solid_background.png" if topcut.game == GameType.VGC else "solid_background_GO.png"

    background = Image.open(os.path.join(SOURCE_PATH, backgroundPath))
    background = background.convert("RGBA")
    background = background.crop((0,0,w,dynamic_height))
    im.paste(background, (0,0), mask=background)

    # Draw reusable header section
    draw_header(im, topcut)

    # Create a drawing context for subsequent player rendering
    d = ImageDraw.Draw(im)

    mult_2 = 0
    for i in range(len(topcut.players)):
        element_circles = "player_element_circles_GO.png" if topcut.game == GameType.GO else "player_element_circles.png"
        player_el = Image.open(os.path.join(SOURCE_PATH, element_circles))
        player_el_x = 35 if (i % 2 == 0) else 573
        player_el_y = 215 + (40 * (i % 2)) + 151*(i//2)
        im.paste(player_el, (player_el_x, player_el_y), mask=player_el)
        
        num_player_x = 75 if (i % 2 == 0) else 615
        num_player_y = 250 + (40 * (i % 2)) + 151*(i//2)
        d.text((num_player_x, num_player_y), str(i+1), fill="white", anchor="rs", font=num_player_font)
        
        
        if(topcut.tour_type in ["PREMIER", "MSS", "REGIONAL", "INTERNATIONAL", "CUP", "CHALLENGE", "OLDREGIONAL", "OLDINTERNATIONAL"]):
            cur_p = i+1
            cp_dist = cp_distribution[topcut.tour_type]
            cur_sel = cp_dist[mult_2]
            cur_cp = cur_sel[0] if topcut.divisions.master >= cur_sel[1] else 0
            if((cur_p & (cur_p-1) == 0) and cur_p != 0):
                mult_2 += 1

            if(cur_cp > 0):
                if(i % 2 == 0):
                    d.text((506, 253 + 150*(i//2)), str(cur_cp) + " CP", fill="white", anchor="rs", font=font_player)
                else:
                    d.text((1045, 293 + 150*(i//2)), str(cur_cp) + " CP", fill="white", anchor="rs", font=font_player)
            

        icon_pokemon_y = 0

        player_name = topcut.players[i].name

        if(len(player_name) > 30):
            p_names = player_name.split()
            if(len(p_names) > 2):   #cut middle names
                p_names = [p_names[0], p_names[-1]]
                if(len(" ".join(p_names)) <= 30):
                    player_name = " ".join(p_names)
                else:
                    p_names[-1] = p_names[-1][0] + "."
                    player_name = " ".join(p_names)
            else:
                p_names[-1] = p_names[-1][0] + "."
                player_name = " ".join(p_names)
        
        # Choose appropriate font based on character set
        player_font = font_player_JP if contains_cjk_characters(player_name) else font_player

        if(len(player_name) > 23):
            player_font = font_player_small
        

        if(topcut.tour_type in ["PREMIERBALL", "MASTERBALL", "GREATBALL", "ULTRABALL", "GRASSROOTS", "WORLDS"]):
            if(i % 2 == 0):
                d.text((108, 253 + 150*(i//2)), player_name, fill="white", anchor="ls", font=player_font)
                d.text((500, 253 + 150*(i//2)), topcut.players[i].record, fill="white", anchor="rs", font=font_player)
            else:
                d.text((646, 293 + 150*(i//2)), player_name, fill="white", anchor="ls", font=player_font)
                d.text((1038, 293 + 150*(i//2)), topcut.players[i].record, fill="white", anchor="rs", font=font_player)
        else:
            if(i % 2 == 0):
                d.text((108, 253 + 150*(i//2)), player_name, fill="white", anchor="ls", font=player_font)
                d.text((412, 253 + 150*(i//2)), topcut.players[i].record, fill="white", anchor="rs", font=font_player)
            else:
                d.text((646, 293 + 150*(i//2)), player_name, fill="white", anchor="ls", font=player_font)
                d.text((950, 293 + 150*(i//2)), topcut.players[i].record, fill="white", anchor="rs", font=font_player)

        icon_pokemon_y = 274 + (41 * (i % 2)) + 151*(i//2)
        icon_pokemon_x_base = 49 if (i % 2 == 0) else 587
        icon_item_y = 320 + (40 * (i % 2)) + 150*(i//2)
        icon_item_x_base = 94 if (i % 2 == 0) else 632
        icon_tera_y = 270 + (40 * (i % 2)) + 150*(i//2)
        icon_tera_x_base = 93 if (i % 2 == 0) else 631
        icon_gmax_x_base = 43 if (i % 2 == 0) else 587
        icon_shadow_y = 310 + (40 * (i % 2)) + 150*(i//2)
        icon_shadow_x_base = 90 if (i % 2 == 0) else 632

        newPokemon = topcut.players[i].pokemon

        with open('../data/restricted.json') as f:
            restricted_list = json.load(f)
        with open('../data/mythical.json') as f:
            mythical_list = json.load(f)
        with open('../data/pokemon_forms_items.json') as f:
            forms_list = json.load(f)

        newPokemon = reorder_pokemon(newPokemon, restricted_list, mythical_list)

        for p in range(len(newPokemon)):
            print(newPokemon[p])
            newPokemon[p].name = change_form_item(newPokemon[p].name, newPokemon[p].item, forms_list)
            icon_name = newPokemon[p].name.lower().replace(" ", "-")
            if(icon_name == ""):
                continue
            pokemon_icon_id = pokemonindex[icon_name]
            if(not os.path.isfile(LOCAL_POKEMON_ICONS_SRC + pokemon_icon_id + ".png")):
                print(POKEMON_ICONS_SRC + newPokemon[p].name.lower().replace(" ", "-") + ".png")
                icon_url = urlopen(POKEMON_ICONS_SRC + pokemon_icon_id + ".png")
                content = icon_url.read()
                with open(LOCAL_POKEMON_ICONS_SRC + pokemon_icon_id + ".png", "wb") as download:
                    download.write(content)
            
            p_icon = Image.open(LOCAL_POKEMON_ICONS_SRC + pokemon_icon_id + ".png")
            p_icon = p_icon.convert("RGBA")
            p_icon = p_icon.resize((60,60))
            im.paste(p_icon, (icon_pokemon_x_base + 80*p, icon_pokemon_y), mask=p_icon)

            if(newPokemon[p].gmax):
                gmax_icon = Image.open(os.path.join(SOURCE_PATH, "gmax.png"))
                gmax_icon = gmax_icon.convert("RGBA")
                gmax_icon = gmax_icon.resize((24,24))
                im.paste(gmax_icon, (icon_gmax_x_base + 80*p, icon_tera_y), mask=gmax_icon)

            if(newPokemon[p].item != ""):
                if(not os.path.isfile(LOCAL_ITEM_ICONS_SRC + itemIndex[newPokemon[p].item] + ".png")):
                    print(ITEM_ICONS_SRC + itemIndex[newPokemon[p].item] + ".png")
                    icon_url = urlopen(ITEM_ICONS_SRC + itemIndex[newPokemon[p].item] + ".png")
                    content = icon_url.read()
                    with open(LOCAL_ITEM_ICONS_SRC + itemIndex[newPokemon[p].item] + ".png", "wb") as download:
                        download.write(content)

                item_icon = Image.open(LOCAL_ITEM_ICONS_SRC + itemIndex[newPokemon[p].item] + ".png")
                item_icon = item_icon.convert("RGBA")
                item_icon = item_icon.resize((24,24))
                im.paste(item_icon, (icon_item_x_base + 80*p, icon_item_y), mask=item_icon)

            if(newPokemon[p].teratype.strip().lower() != ""):
                tera_icon = Image.open(LOCAL_TERA_ICONS_SRC + newPokemon[p].teratype.strip().lower() + ".png")
                tera_icon = tera_icon.convert("RGBA")
                tera_icon = tera_icon.resize((32,32))
                im.paste(tera_icon, (icon_tera_x_base + 80*p, icon_tera_y), mask=tera_icon)

            if(newPokemon[p].shadow):
                shadow_icon = Image.open(os.path.join(SOURCE_PATH, "shadow_GO.png"))
                shadow_icon = shadow_icon.convert("RGBA")
                shadow_icon = shadow_icon.resize((36,36))
                im.paste(shadow_icon, (icon_shadow_x_base + 80*p, icon_shadow_y), mask=shadow_icon)

            if(newPokemon[p].purified):
                purified_icon = Image.open(os.path.join(SOURCE_PATH, "purified_GO.png"))
                purified_icon = purified_icon.convert("RGBA")
                purified_icon = purified_icon.resize((36,36))
                im.paste(purified_icon, (icon_shadow_x_base + 80*p, icon_shadow_y), mask=purified_icon)

            if(newPokemon[p].best_friend):
                best_friend_icon = Image.open(os.path.join(SOURCE_PATH, "best_buddy_GO.png"))
                best_friend_icon = best_friend_icon.convert("RGBA")
                best_friend_icon = best_friend_icon.resize((24,24))
                im.paste(best_friend_icon, (icon_tera_x_base + 80*p, icon_tera_y), mask=best_friend_icon)


    #icon_test = Image.open(urlopen(POKEMON_ICONS_SRC + "ogerpon.png"))
    #icon_test = icon_test.resize((56,56))
    #im.paste(icon_test, (60, 280), mask=icon_test)


    #usages = computeUsage(pokepastTeams)
    

    return im


def computeUsage(teams):
    pokemon_count = {}
    total_pokemon = 0
    for t in teams:
        for p in t:
            if(p.name not in pokemon_count.keys()):
                pokemon_count[p.name] = 0
            pokemon_count[p.name] += 1
            total_pokemon += 1

    pokemon_ratio = {k: v / len(teams) for k, v in pokemon_count.items()}

    return sorted(pokemon_ratio.items(), key=lambda i: i[1], reverse=True)





def mergeImages():
    SOURCE_PATH = "C:/Users/HAWKE-PC/Pictures/dream-world"


    font_regular = ImageFont.truetype("../fonts/Montserrat/static/Montserrat-Bold.ttf", 24)
    font = ImageFont.truetype("../fonts/Montserrat/static/Montserrat-Bold.ttf", 48)

    im1 = Image.open(SOURCE_PATH + "/348.png")
    im2 = Image.open("C:/Users/HAWKE-PC/Pictures/two.png")


    w = max(im1.size[0], im2.size[0])
    h = max(im1.size[1], im2.size[1])

    im = Image.new("RGBA", (w, h))

    im.paste(im2, (0, 0))
    im.paste(im1, (0, 0), mask=im1)

    d = ImageDraw.Draw(im)
    d.text((w/2,h-10), "Pinated", fill="white", anchor="ms", font=font)

    return im
