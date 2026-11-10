import json
from helper import reorder_pokemon, change_form_item, contains_cjk_characters, loadFlag
from model import Palette, TournamentType, Player, TopCut, GameType
import io
from PIL import Image, ImageDraw, ImageFont
import os
from urllib.request import urlopen
from pathlib import Path
from database import submit_data
import base64

# Constants
BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_PATH = str(BASE_DIR / "img")
# POKEMON_ICONS_SRC = "https://limitlesstcg.s3.us-east-2.amazonaws.com/pokemon/gen9/"
POKEMON_ICONS_SRC = "https://img.generator.joaoabel.pt/pokemon/projectpokemon/"
ITEM_ICONS_SRC = "https://img.generator.joaoabel.pt/items/item_"
LOCAL_POKEMON_ICONS_SRC = str(BASE_DIR / "img" / "pokemon" / "projectpokemon") + "/"
LOCAL_ITEM_ICONS_SRC = str(BASE_DIR / "img" / "items" / "item_")
LOCAL_TERA_ICONS_SRC = str(BASE_DIR / "img" / "teras") + "/"

# Fonts
FONTS_DIR = BASE_DIR / "fonts"
font_regular = ImageFont.truetype(str(FONTS_DIR / "Montserrat" / "static" / "Montserrat-Regular.ttf"), 24)
font_bold = ImageFont.truetype(str(FONTS_DIR / "Montserrat" / "static" / "Montserrat-Bold.ttf"), 24)
font_player = ImageFont.truetype(str(FONTS_DIR / "Montserrat" / "static" / "Montserrat-Bold.ttf"), 18)
font_player_small = ImageFont.truetype(str(FONTS_DIR / "Montserrat" / "static" / "Montserrat-Bold.ttf"), 16)
font_player_social = ImageFont.truetype(str(FONTS_DIR / "Montserrat" / "static" / "Montserrat-Regular.ttf"), 14)

font_player_JP = ImageFont.truetype(str(FONTS_DIR / "SourceHansSans" / "SourceHanSans-VF.ttf"), 18)
font_player_social_JP = ImageFont.truetype(str(FONTS_DIR / "SourceHansSans" / "SourceHanSans-VF.ttf"), 14)
font_player_JP_IG_1st = ImageFont.truetype(str(FONTS_DIR / "SourceHansSans" / "SourceHanSans-VF.ttf"), 90)
font_player_JP_IG_2nd = ImageFont.truetype(str(FONTS_DIR / "SourceHansSans" / "SourceHanSans-VF.ttf"), 84)
font_player_JP_IG_T4 = ImageFont.truetype(str(FONTS_DIR / "SourceHansSans" / "SourceHanSans-VF.ttf"), 74)
font_player_JP_IG = ImageFont.truetype(str(FONTS_DIR / "SourceHansSans" / "SourceHanSans-VF.ttf"), 54)

font_player_social_JP_IG_1st = ImageFont.truetype(str(FONTS_DIR / "SourceHansSans" / "SourceHanSans-VF.ttf"), 70)
font_player_social_JP_IG_2nd = ImageFont.truetype(str(FONTS_DIR / "SourceHansSans" / "SourceHanSans-VF.ttf"), 60)
font_player_social_JP_IG_T4 = ImageFont.truetype(str(FONTS_DIR / "SourceHansSans" / "SourceHanSans-VF.ttf"), 50)
font_player_social_JP_IG = ImageFont.truetype(str(FONTS_DIR / "SourceHansSans" / "SourceHanSans-VF.ttf"), 40)

font_title_JP = ImageFont.truetype(str(FONTS_DIR / "SourceHansSans" / "SourceHanSans-VF.ttf"), 30)
font_format_JP = ImageFont.truetype(str(FONTS_DIR / "SourceHansSans" / "SourceHanSans-VF.ttf"), 20)

font_title_JP_IG = ImageFont.truetype(str(FONTS_DIR / "SourceHansSans" / "SourceHanSans-VF.ttf"), 74)
font_format_JP_IG = ImageFont.truetype(str(FONTS_DIR / "SourceHansSans" / "SourceHanSans-VF.ttf"), 54)

font_player_JP.set_variation_by_name("Bold")
font_player_JP_IG_1st.set_variation_by_name("Bold")
font_player_JP_IG_2nd.set_variation_by_name("Bold")
font_player_JP_IG_T4.set_variation_by_name("Bold")
font_player_JP_IG.set_variation_by_name("Bold")
font_title_JP.set_variation_by_name("Bold")
font_title_JP_IG.set_variation_by_name("Bold")
font_format_JP.set_variation_by_name("Bold")
font_format_JP_IG.set_variation_by_name("Bold")
font_player_social_JP.set_variation_by_name("Bold")
font_player_social_JP_IG_1st.set_variation_by_name("Bold")
font_player_social_JP_IG_2nd.set_variation_by_name("Bold")
font_player_social_JP_IG_T4.set_variation_by_name("Bold")
font_player_social_JP_IG.set_variation_by_name("Bold")

# Instagram header fonts
font_regular_IG = ImageFont.truetype(str(FONTS_DIR / "Montserrat" / "static" / "Montserrat-Regular.ttf"), 74)
font_bold_IG = ImageFont.truetype(str(FONTS_DIR / "Montserrat" / "static" / "Montserrat-Bold.ttf"), 74)

num_player_font = ImageFont.truetype(str(FONTS_DIR / "Edo" / "edo.ttf"), 24)
num_player_font_IG = ImageFont.truetype(str(FONTS_DIR / "Edo" / "edo.ttf"), 74)
num_player_font_IG_1st = ImageFont.truetype(str(FONTS_DIR / "Edo" / "edo.ttf"), 146)
num_player_font_IG_2nd = ImageFont.truetype(str(FONTS_DIR / "Edo" / "edo.ttf"), 144)
num_player_font_IG_T4 = ImageFont.truetype(str(FONTS_DIR / "Edo" / "edo.ttf"), 114)
font_player_IG_1st = ImageFont.truetype(str(FONTS_DIR / "Montserrat" / "static" / "Montserrat-Bold.ttf"), 90)
font_player_IG_2nd = ImageFont.truetype(str(FONTS_DIR / "Montserrat" / "static" / "Montserrat-Bold.ttf"), 86)
font_player_IG_T4 = ImageFont.truetype(str(FONTS_DIR / "Montserrat" / "static" / "Montserrat-Bold.ttf"), 75)
font_player_IG = ImageFont.truetype(str(FONTS_DIR / "Montserrat" / "static" / "Montserrat-Bold.ttf"), 60)
font_player_social_IG_1st = ImageFont.truetype(str(FONTS_DIR / "Montserrat" / "static" / "Montserrat-Regular.ttf"), 80)
font_player_social_IG_2nd = ImageFont.truetype(str(FONTS_DIR / "Montserrat" / "static" / "Montserrat-Regular.ttf"), 70)
font_player_social_IG_T4 = ImageFont.truetype(str(FONTS_DIR / "Montserrat" / "static" / "Montserrat-Regular.ttf"), 60)
font_player_social_IG = ImageFont.truetype(str(FONTS_DIR / "Montserrat" / "static" / "Montserrat-Regular.ttf"), 50)


def loadItemIndex():
    SOURCE_PATH = str(BASE_DIR / "items_clean.txt")
    index = {}
    f = open(SOURCE_PATH, "r", encoding="utf8")
    for l in f:
        item_id_pair = l.strip().split("|")
        fixed_id = "0" * (4 - len(item_id_pair[1])) + item_id_pair[1]
        index[item_id_pair[0]] = fixed_id
    f.close()
    return index


def loadPokemonIndex():
    SOURCE_PATH = str(BASE_DIR / "pokemon_clean.txt")
    index = {}
    f = open(SOURCE_PATH, "r", encoding="utf8")
    for l in f:
        pokemon_id_pair = l.strip().split("|")
        index[pokemon_id_pair[0]] = pokemon_id_pair[1]
    f.close()
    return index


itemIndex = loadItemIndex()
pokemonindex = loadPokemonIndex()

with open(BASE_DIR / 'data' / 'restricted.json') as f:
    restricted_list = json.load(f)
with open(BASE_DIR / 'data' / 'mythical.json') as f:
    mythical_list = json.load(f)
with open(BASE_DIR / 'data' / 'pokemon_forms_items.json') as f:
    forms_list = json.load(f)

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

def generateTopcutInstagram(topcut):
    image = genTemplateInstagram(topcut)
    buf = io.BytesIO()
    image.save(buf, "PNG")
    
    # Only submit data if all players have at least 4 pokemon with non-empty names
    if all(len([p for p in player.pokemon if p.name.strip()]) >= 4 for player in topcut.players):
        submit_data(topcut)
    
    return buf.getvalue()

def format_player_name(player_name: str) -> str:
    """Shortens player names longer than 30 characters."""
    if len(player_name) > 30:
        p_names = player_name.split()
        if len(p_names) > 2:  # Cut middle names
            p_names = [p_names[0], p_names[-1]]
            if len(" ".join(p_names)) <= 30:
                return " ".join(p_names)
            else:
                p_names[-1] = p_names[-1][0] + "."
                return " ".join(p_names)
        else:
            p_names[-1] = p_names[-1][0] + "."
            return " ".join(p_names)
    return player_name

def calculate_player_cp(rank: int, tour_type: str, master_count: int, mult_2: int) -> tuple[int, int]:
    """Calculates CP points for a player rank and updates the mult_2 index."""
    cur_cp = 0
    cp_tour_types = [
        "PREMIER", "MSS", "REGIONAL", "INTERNATIONAL", 
        "CUP", "CHALLENGE", "OLDREGIONAL", "OLDINTERNATIONAL"
    ]
    if tour_type in cp_tour_types:
        cp_dist = cp_distribution[tour_type]
        cur_sel = cp_dist[mult_2]
        cur_cp = cur_sel[0] if master_count >= cur_sel[1] else 0
        if (rank & (rank - 1) == 0) and rank != 0:
            mult_2 += 1

    return cur_cp, mult_2

def load_pokemon_icon(name: str, size: tuple[int, int]) -> Image.Image | None:
    """Downloads Pokemon sprite if not cached and returns an image of the specified size."""
    icon_name = name.lower().replace(" ", "-")
    if not icon_name or icon_name not in pokemonindex:
        return None

    pokemon_icon_id = pokemonindex[icon_name]
    local_path = LOCAL_POKEMON_ICONS_SRC + pokemon_icon_id + ".png"
    if not os.path.isfile(local_path):
        icon_url = urlopen(POKEMON_ICONS_SRC + pokemon_icon_id + ".png")
        content = icon_url.read()
        with open(local_path, "wb") as download:
            download.write(content)

    p_icon = Image.open(local_path).convert("RGBA")
    return p_icon.resize(size)

def load_item_icon(item_name: str, size: tuple[int, int]) -> Image.Image | None:
    """Downloads item icon if not cached and returns an image of the specified size."""
    if not item_name or item_name not in itemIndex:
        return None

    local_path = LOCAL_ITEM_ICONS_SRC + itemIndex[item_name] + ".png"
    if not os.path.isfile(local_path):
        icon_url = urlopen(ITEM_ICONS_SRC + itemIndex[item_name] + ".png")
        content = icon_url.read()
        with open(local_path, "wb") as download:
            download.write(content)

    item_icon = Image.open(local_path).convert("RGBA")
    return item_icon.resize(size)

def draw_player_card(im, d, i: int, player, tour_type: str, palette: Palette, cur_cp: int = 0):
    """Draws player card background, rank number, CP, name, social, flag, and record."""
    # 1. Card background circle
    element_circles = os.path.join("colors", palette.value, "player_element_circles.png")
    player_el = Image.open(os.path.join(SOURCE_PATH, element_circles))
    player_el_x = 35 if (i % 2 == 0) else 573
    player_el_y = 215 + (40 * (i % 2)) + 151 * (i // 2)
    im.paste(player_el, (player_el_x, player_el_y), mask=player_el)

    # 2. Rank number
    num_player_x = 75 if (i % 2 == 0) else 615
    num_player_y = 250 + (40 * (i % 2)) + 151 * (i // 2)
    d.text((num_player_x, num_player_y), str(i + 1), fill="white", anchor="rs", font=num_player_font)

    # 3. Championship Points
    if cur_cp > 0:
        cp_x = 506 if (i % 2 == 0) else 1045
        cp_y = (248 if (i % 2 == 0) else 288) + 151 * (i // 2)
        d.text((cp_x, cp_y), f"{cur_cp} CP", fill="white", anchor="rs", font=font_player)

    # 4. Formatted player name & font selection
    player_name = format_player_name(player.name)
    player_font = font_player_JP if contains_cjk_characters(player_name) else font_player
    if len(player_name) > 23:
        player_font = font_player_small
    player_social_font = font_player_social_JP if contains_cjk_characters(player.social) else font_player_social

    # 5. Position calculations
    no_cp_tours = ["PREMIERBALL", "MASTERBALL", "GREATBALL", "ULTRABALL", "GRASSROOTS", "WORLDS"]
    if tour_type in no_cp_tours:
        player_x = 108 if (i % 2 == 0) else 646
        player_y = (248 if (i % 2 == 0) else 288) + 151 * (i // 2)
        record_x = 500 if (i % 2 == 0) else 1038
    else:
        player_x = 108 if (i % 2 == 0) else 646
        player_y = (248 if (i % 2 == 0) else 288) + 151 * (i // 2)
        record_x = 412 if (i % 2 == 0) else 950

    if player.flag:
        player_x += 25

    # 6. Name and social
    if player.social and player.social.strip() != "":
        d.text((player_x, player_y - 10), player_name, fill="white", anchor="ls", font=player_font)
        d.text((player_x, player_y + 10), player.social, fill="white", anchor="ls", font=player_social_font)
    else:
        d.text((player_x, player_y), player_name, fill="white", anchor="ls", font=player_font)

    # 7. Country flag
    if player.flag:
        flag_img = loadFlag(player.flag, 30)
        if flag_img:
            im.paste(flag_img, (player_x - 35, player_y - flag_img.height + 3), mask=flag_img)

    # 8. Match record
    d.text((record_x, player_y), player.record, fill="white", anchor="rs", font=font_player)

def draw_player_team(im, i: int, pokemon_list: list, reorder: bool = False):
    """Renders the 6 pokemon slots (sprites, items, teras, and badges) for a player."""
    icon_pokemon_y = 274 + (40 * (i % 2)) + 151 * (i // 2)
    icon_pokemon_x_base = 49 if (i % 2 == 0) else 587
    icon_item_y = 320 + (40 * (i % 2)) + 151 * (i // 2)
    icon_item_x_base = 94 if (i % 2 == 0) else 632
    icon_tera_y = 270 + (40 * (i % 2)) + 151 * (i // 2)
    icon_tera_x_base = 93 if (i % 2 == 0) else 631
    icon_gmax_x_base = 43 if (i % 2 == 0) else 587
    icon_shadow_y = 310 + (40 * (i % 2)) + 151 * (i // 2)
    icon_shadow_x_base = 90 if (i % 2 == 0) else 632

    newPokemon = pokemon_list
    if reorder:
        newPokemon = reorder_pokemon(newPokemon, restricted_list, mythical_list)

    for p in range(len(newPokemon)):
        mon = newPokemon[p]
        mon.name = change_form_item(mon.name, mon.item, forms_list)
        p_icon = load_pokemon_icon(mon.name, (60,60))
        if not p_icon:
            continue
        im.paste(p_icon, (icon_pokemon_x_base + 80 * p, icon_pokemon_y), mask=p_icon)

        if mon.gmax:
            gmax_icon = Image.open(os.path.join(SOURCE_PATH, "gmax.png")).convert("RGBA").resize((24, 24))
            im.paste(gmax_icon, (icon_gmax_x_base + 80 * p, icon_tera_y), mask=gmax_icon)

        if mon.item != "":
            item_icon = load_item_icon(mon.item, (24, 24))
            if item_icon:
                im.paste(item_icon, (icon_item_x_base + 80 * p, icon_item_y), mask=item_icon)

        if mon.teratype.strip().lower() != "":
            tera_path = LOCAL_TERA_ICONS_SRC + mon.teratype.strip().lower() + ".png"
            if os.path.isfile(tera_path):
                tera_icon = Image.open(tera_path).convert("RGBA").resize((32, 32))
                im.paste(tera_icon, (icon_tera_x_base + 80 * p, icon_tera_y), mask=tera_icon)

        if mon.shadow:
            shadow_icon = Image.open(os.path.join(SOURCE_PATH, "pokemonGO", "shadow_GO.png")).convert("RGBA").resize((36, 36))
            im.paste(shadow_icon, (icon_shadow_x_base + 80 * p, icon_shadow_y), mask=shadow_icon)

        if mon.purified:
            purified_icon = Image.open(os.path.join(SOURCE_PATH, "pokemonGO", "purified_GO.png")).convert("RGBA").resize((36, 36))
            im.paste(purified_icon, (icon_shadow_x_base + 80 * p, icon_shadow_y), mask=purified_icon)

        if mon.best_friend:
            best_friend_icon = Image.open(os.path.join(SOURCE_PATH, "pokemonGO", "best_buddy_GO.png")).convert("RGBA").resize((24, 24))
            im.paste(best_friend_icon, (icon_tera_x_base + 80 * p, icon_tera_y), mask=best_friend_icon)

def genTemplate(topcut):

    template = Image.open(os.path.join(SOURCE_PATH, "fulltemplate_v2.png"))

    w = template.size[0]
    #h = template.size[1]

    total_p = len(topcut.players) - 1
    dynamic_height = 346 + (40 * (total_p % 2)) + 151*(total_p//2) + 50

    im = Image.new("RGBA", (template.size[0], dynamic_height))

    backgroundPath = os.path.join("colors", topcut.palette.value, "solid_background.png")

    background = Image.open(os.path.join(SOURCE_PATH, backgroundPath))
    background = background.convert("RGBA")
    background = background.crop((0,0,w,dynamic_height))

    draw_background_image(background, topcut)

    im.paste(background, (0,0), mask=background)

    # Draw reusable header section
    draw_header(im, topcut)

    # Create a drawing context for subsequent player rendering
    d = ImageDraw.Draw(im)

    mult_2 = 0
    for i, player in enumerate(topcut.players):
        cur_cp, mult_2 = calculate_player_cp(i + 1, topcut.tour_type, topcut.divisions.master, mult_2)
        draw_player_card(im, d, i, player, topcut.tour_type, topcut.palette, cur_cp)
        draw_player_team(im, i, player.pokemon, reorder=topcut.reorder)

    return im

def genTemplateInstagram(topcut):
    backgroundPath = os.path.join("colors", topcut.palette.value, "IG", "solid_background.png")

    is_toronto = topcut.tour_name.lower().startswith("[toronto]")
    if is_toronto:
        backgroundPath = os.path.join("instagramMode", "solid_background_vgc_IG_toronto.png")
        topcut.tour_name = topcut.tour_name[9:].strip()  # Remove "[Toronto]" from the tournament name

    background = Image.open(os.path.join(SOURCE_PATH, backgroundPath))
    background = background.convert("RGBA")
    w = background.size[0]
    h = background.size[1]

    im = Image.new("RGBA", (w, h))

    draw_background_image(background, topcut, is_instagram=True)

    im.paste(background, (0,0), mask=background)
    draw_header(im, topcut, is_instagram=True)

    layout_elements = {
        1: [
            ("player_element_circles_1st.png", (340, 1185)),
        ],
        2: [
            ("player_element_circles_1st.png", (340, 1150)),
            ("player_element_circles_2nd.png", (518, 2895)),
        ],
        3: [
            ("player_element_circles_1st.png", (340, 1044)),
            ("player_element_circles_2nd.png", (518, 2073)),
            ("player_element_circles_T4.png", (694, 3004)),
        ],
        4: [
            ("player_element_circles_1st.png", (340, 591)),
            ("player_element_circles_2nd.png", (518, 1620)),
            ("player_element_circles_T4.png", (694, 2551)),
            ("player_element_circles_T4.png", (694, 3388)),
        ],
        5: [
            ("player_element_circles_1st.png", (340, 591)),
            ("player_element_circles_2nd.png", (518, 1431)),
            ("player_element_circles_T4.png", (694, 2168)),
            ("player_element_circles_T4.png", (694, 2811)),
            ("player_element_circles_T4.png", (694, 3454)),
        ],
        6: [
            ("player_element_circles_1st.png", (340, 783)),
            ("player_element_circles_2nd.png", (518, 1754)),
            ("player_element_circles.png", (94, 2591)),
            ("player_element_circles.png", (1695, 2671)),
            ("player_element_circles.png", (94, 3286)),
            ("player_element_circles.png", (1695, 3366)),
        ],
        7: [
            ("player_element_circles_1st.png", (340, 741)),
            ("player_element_circles_2nd.png", (518, 1576)),
            ("player_element_circles.png", (94, 2312)),
            ("player_element_circles.png", (1695, 2392)),
            ("player_element_circles.png", (94, 2846)),
            ("player_element_circles.png", (1695, 2926)),
            ("player_element_circles.png", (894, 3380)),
        ],
        8: [
            ("player_element_circles_1st.png", (340, 741)),
            ("player_element_circles_2nd.png", (518, 1576)),
            ("player_element_circles.png", (94, 2312)),
            ("player_element_circles.png", (1695, 2392)),
            ("player_element_circles.png", (94, 2846)),
            ("player_element_circles.png", (1695, 2926)),
            ("player_element_circles.png", (94, 3380)),
            ("player_element_circles.png", (1695, 3460)),
        ],
        9: [
            ("player_element_circles_1st.png", (340, 663)),
            ("player_element_circles_2nd.png", (518, 1423)),
            ("player_element_circles.png", (94, 2085)),
            ("player_element_circles.png", (1695, 2125)),
            ("player_element_circles.png", (94, 2545)),
            ("player_element_circles.png", (1695, 2585)),
            ("player_element_circles.png", (94, 3005)),
            ("player_element_circles.png", (1695, 3045)),
            ("player_element_circles.png", (894, 3505)),
        ],
        10: [
            ("player_element_circles_1st.png", (340, 663)),
            ("player_element_circles_2nd.png", (518, 1423)),
            ("player_element_circles.png", (94, 2085)),
            ("player_element_circles.png", (1695, 2125)),
            ("player_element_circles.png", (94, 2545)),
            ("player_element_circles.png", (1695, 2585)),
            ("player_element_circles.png", (94, 3005)),
            ("player_element_circles.png", (1695, 3045)),
            ("player_element_circles.png", (94, 3465)),
            ("player_element_circles.png", (1695, 3505)),
        ],
        11: [
            ("player_element_circles.png", (94, 743)),
            ("player_element_circles.png", (1695, 843)),
            ("player_element_circles.png", (94, 1289)),
            ("player_element_circles.png", (1695, 1389)),
            ("player_element_circles.png", (94, 1835)),
            ("player_element_circles.png", (1695, 1935)),
            ("player_element_circles.png", (94, 2381)),
            ("player_element_circles.png", (1695, 2481)),
            ("player_element_circles.png", (94, 2927)),
            ("player_element_circles.png", (1695, 3027)),
            ("player_element_circles.png", (894, 3473)),
        ],
        12: [
            ("player_element_circles.png", (94, 743)),
            ("player_element_circles.png", (1695, 843)),
            ("player_element_circles.png", (94, 1289)),
            ("player_element_circles.png", (1695, 1389)),
            ("player_element_circles.png", (94, 1835)),
            ("player_element_circles.png", (1695, 1935)),
            ("player_element_circles.png", (94, 2381)),
            ("player_element_circles.png", (1695, 2481)),
            ("player_element_circles.png", (94, 2927)),
            ("player_element_circles.png", (1695, 3027)),
            ("player_element_circles.png", (94, 3473)),
            ("player_element_circles.png", (1695, 3573))
        ],
        13: [
            ("player_element_circles.png", (94, 698)),
            ("player_element_circles.png", (1695, 748)),
            ("player_element_circles.png", (94, 1169)),
            ("player_element_circles.png", (1695, 1219)),
            ("player_element_circles.png", (94, 1641)),
            ("player_element_circles.png", (1695, 1691)),
            ("player_element_circles.png", (94, 2113)),
            ("player_element_circles.png", (1695, 2163)),
            ("player_element_circles.png", (94, 2585)),
            ("player_element_circles.png", (1695, 2635)),
            ("player_element_circles.png", (94, 3057)),
            ("player_element_circles.png", (1695, 3107)),
            ("player_element_circles.png", (894, 3579)),
        ],
        14: [
            ("player_element_circles.png", (94, 698)),
            ("player_element_circles.png", (1695, 748)),
            ("player_element_circles.png", (94, 1169)),
            ("player_element_circles.png", (1695, 1219)),
            ("player_element_circles.png", (94, 1641)),
            ("player_element_circles.png", (1695, 1691)),
            ("player_element_circles.png", (94, 2113)),
            ("player_element_circles.png", (1695, 2163)),
            ("player_element_circles.png", (94, 2585)),
            ("player_element_circles.png", (1695, 2635)),
            ("player_element_circles.png", (94, 3057)),
            ("player_element_circles.png", (1695, 3107)),
            ("player_element_circles.png", (94, 3529)),
            ("player_element_circles.png", (1695, 3579)),
        ],
        15: [
            ("player_element_circles.png", (94, 571)),
            ("player_element_circles.png", (1695, 611)),
            ("player_element_circles.png", (94, 1002)),
            ("player_element_circles.png", (1695, 1042)),
            ("player_element_circles.png", (94, 1434)),
            ("player_element_circles.png", (1695, 1474)),
            ("player_element_circles.png", (94, 1866)),
            ("player_element_circles.png", (1695, 1906)),
            ("player_element_circles.png", (94, 2298)),
            ("player_element_circles.png", (1695, 2338)),
            ("player_element_circles.png", (94, 2730)),
            ("player_element_circles.png", (1695, 2770)),
            ("player_element_circles.png", (94, 3162)),
            ("player_element_circles.png", (1695, 3202)),
            ("player_element_circles.png", (894, 3634))
        ],
        16: [
            ("player_element_circles.png", (94, 571)),
            ("player_element_circles.png", (1695, 611)),
            ("player_element_circles.png", (94, 1002)),
            ("player_element_circles.png", (1695, 1042)),
            ("player_element_circles.png", (94, 1434)),
            ("player_element_circles.png", (1695, 1474)),
            ("player_element_circles.png", (94, 1866)),
            ("player_element_circles.png", (1695, 1906)),
            ("player_element_circles.png", (94, 2298)),
            ("player_element_circles.png", (1695, 2338)),
            ("player_element_circles.png", (94, 2730)),
            ("player_element_circles.png", (1695, 2770)),
            ("player_element_circles.png", (94, 3162)),
            ("player_element_circles.png", (1695, 3202)),
            ("player_element_circles.png", (94, 3594)),
            ("player_element_circles.png", (1695, 3634))
        ],
    }

    no_cp_tours = ["PREMIERBALL", "MASTERBALL", "GREATBALL", "ULTRABALL", "GRASSROOTS", "WORLDS"]
    has_cp = topcut.tour_type not in no_cp_tours
    mult_2 = 0

    tier_styles = {
        "player_element_circles_1st.png": {
            "num_font": num_player_font_IG_1st,
            "num_offset": (200, 180),
            "flag_size": 150,
            "flag_offset": (350, 192),
            "flag_text_offset": 210,
            "font_player": font_player_IG_1st,
            "font_player_jp": font_player_JP_IG_1st,
            "font_social": font_player_social_IG_1st,
            "font_social_jp": font_player_social_JP_IG_1st,
            "cp_pos": (2500, 165),
            "cp_spacing": 231,
            "name_x": 340,
            "name_y_social": 105,
            "social_y": 225,
            "name_y_no_social": 160,
            "step_x": 424,
            "mon_size": (340, 340),
            "mon_offset": (65, 290),
            "gmax_size": (96, 96),
            "gmax_offset": (55, 280),
            "item_size": (96, 96),
            "item_offset": (330, 550),
            "tera_size": (135, 135),
            "tera_offset": (310, 280),
            "shadow_offset": (330, 550),
            "best_friend_offset": (330, 280),
            "go_badge_size": (110, 110),
        },
        "player_element_circles_2nd.png": {
            "num_font": num_player_font_IG_2nd,
            "num_offset": (180, 160),
            "flag_size": 120,
            "flag_offset": (300, 161),
            "flag_text_offset": 210,
            "font_player": font_player_IG_2nd,
            "font_player_jp": font_player_JP_IG_2nd,
            "font_social": font_player_social_IG_2nd,
            "font_social_jp": font_player_social_JP_IG_2nd,
            "cp_pos": (2150, 147),
            "cp_spacing": 164,
            "name_x": 260,
            "name_y_social": 100,
            "social_y": 190,
            "name_y_no_social": 147,
            "step_x": 364,
            "mon_size": (280, 280),
            "mon_offset": (63, 250),
            "gmax_size": (82, 82),
            "gmax_offset": (47, 240),
            "item_size": (82, 82),
            "item_offset": (292, 472),
            "tera_size": (116, 116),
            "tera_offset": (283, 240),
            "shadow_offset": (283, 472),
            "best_friend_offset": (283, 240),
            "go_badge_size": (94, 94),
        },
        "player_element_circles_T4.png": {
            "num_font": num_player_font_IG_T4,
            "num_offset": (150, 129),
            "flag_size": 105,
            "flag_offset": (260, 135),
            "flag_text_offset": 160,
            "font_player": font_player_IG_T4,
            "font_player_jp": font_player_JP_IG_T4,
            "font_social": font_player_social_IG_T4,
            "font_social_jp": font_player_social_JP_IG_T4,
            "cp_pos": (1780, 122),
            "cp_spacing": 117,
            "name_x": 260,
            "name_y_social": 80,
            "social_y": 165,
            "name_y_no_social": 122,
            "step_x": 303,
            "mon_size": (233, 233),
            "mon_offset": (50, 210),
            "gmax_size": (70, 70),
            "gmax_offset": (43, 200),
            "item_size": (69, 69),
            "item_offset": (230, 400),
            "tera_size": (96, 96),
            "tera_offset": (230, 210),
            "shadow_offset": (230, 400),
            "best_friend_offset": (230, 210),
            "go_badge_size": (69, 69),
        },
        "player_element_circles.png": {
            "num_font": num_player_font_IG,
            "num_offset": (120, 99),
            "flag_size": 80,
            "flag_offset": (200, 107),
            "flag_text_offset": 100,
            "font_player": font_player_IG,
            "font_player_jp": font_player_JP_IG,
            "font_social": font_player_social_IG,
            "font_social_jp": font_player_social_JP_IG,
            "cp_pos": (1420, 97),
            "cp_spacing": 120,
            "name_x": 220,
            "name_y_social": 65,
            "social_y": 130,
            "name_y_no_social": 97,
            "step_x": 243,
            "mon_size": (194, 194),
            "mon_offset": (36, 166),
            "gmax_size": (55, 55),
            "gmax_offset": (35, 160),
            "item_size": (55, 55),
            "item_offset": (195, 310),
            "tera_size": (77, 77),
            "tera_offset": (189, 160),
            "shadow_offset": (189, 310),
            "best_friend_offset": (189, 160),
            "go_badge_size": (63, 63),
        },
    }

    d = ImageDraw.Draw(im)

    for index, (filename, pos) in enumerate(layout_elements.get(len(topcut.players), [])):
        element_path = os.path.join(SOURCE_PATH, "colors", topcut.palette.value, "IG", filename)
        with Image.open(element_path) as player_el:
            im.paste(player_el, pos, mask=player_el)
        player = topcut.players[index]
        cur_cp = 0
        if has_cp:
            cur_cp, mult_2 = calculate_player_cp(index + 1, topcut.tour_type, topcut.divisions.master, mult_2)
        if topcut.reorder:
            player.pokemon = reorder_pokemon(player.pokemon, restricted_list, mythical_list)
        player_name = format_player_name(player.name)
        cfg = tier_styles.get(filename, tier_styles["player_element_circles.png"])

        # Player Position
        d.text((pos[0] + cfg["num_offset"][0], pos[1] + cfg["num_offset"][1]), str(index + 1), fill="white", anchor="rs", font=cfg["num_font"])

        # Player flag
        if player.flag:
            flag_img = loadFlag(player.flag, cfg["flag_size"])
            if flag_img:
                im.paste(flag_img, (pos[0] + cfg["flag_offset"][0], pos[1] + cfg["flag_offset"][1] - flag_img.height), mask=flag_img)

        # Championship Points
        cp_offset = 0
        if cur_cp > 0:
            d.text((pos[0] + cfg["cp_pos"][0], pos[1] + cfg["cp_pos"][1]), f"{cur_cp} CP", fill="white", anchor="rs", font=cfg["font_player"])
            bbox = cfg["font_player"].getbbox(f"{cur_cp} CP")
            cp_offset = bbox[2] - bbox[0] + cfg["cp_spacing"]

        # Player Name & Social
        player_font = cfg["font_player_jp"] if contains_cjk_characters(player_name) else cfg["font_player"]
        player_social_font = cfg["font_social_jp"] if contains_cjk_characters(player.social) else cfg["font_social"]
        flag_offset = cfg["flag_text_offset"] if player.flag else 0
        name_x = pos[0] + cfg["name_x"] + flag_offset
        if player.social and player.social.strip() != "":
            d.text((name_x, pos[1] + cfg["name_y_social"]), player_name, fill="white", anchor="ls", font=player_font)
            d.text((name_x, pos[1] + cfg["social_y"]), player.social, fill="white", anchor="ls", font=player_social_font)
        else:
            d.text((name_x, pos[1] + cfg["name_y_no_social"]), player_name, fill="white", anchor="ls", font=player_font)

        # Match record
        d.text((pos[0] + cfg["cp_pos"][0] - cp_offset, pos[1] + cfg["cp_pos"][1]), player.record, fill="white", anchor="rs", font=cfg["font_player"])

        # Draw the player's team (sprites, items, teras, and badges)
        step_x = cfg["step_x"]
        for p in range(len(player.pokemon)):
            mon = player.pokemon[p]
            mon.name = change_form_item(mon.name, mon.item, forms_list)
            p_icon = load_pokemon_icon(mon.name, cfg["mon_size"])
            if not p_icon:
                continue
            im.paste(p_icon, (pos[0] + cfg["mon_offset"][0] + step_x * p, pos[1] + cfg["mon_offset"][1]), mask=p_icon)

            if mon.gmax:
                gmax_icon = Image.open(os.path.join(SOURCE_PATH, "gmax.png")).convert("RGBA").resize(cfg["gmax_size"])
                im.paste(gmax_icon, (pos[0] + cfg["gmax_offset"][0] + step_x * p, pos[1] + cfg["gmax_offset"][1]), mask=gmax_icon)

            if mon.item != "":
                item_icon = load_item_icon(mon.item, cfg["item_size"])
                if item_icon:
                    im.paste(item_icon, (pos[0] + cfg["item_offset"][0] + step_x * p, pos[1] + cfg["item_offset"][1]), mask=item_icon)

            if mon.teratype.strip().lower() != "":
                tera_path = LOCAL_TERA_ICONS_SRC + mon.teratype.strip().lower() + ".png"
                if os.path.isfile(tera_path):
                    tera_icon = Image.open(tera_path).convert("RGBA").resize(cfg["tera_size"])
                    im.paste(tera_icon, (pos[0] + cfg["tera_offset"][0] + step_x * p, pos[1] + cfg["tera_offset"][1]), mask=tera_icon)

            if mon.shadow:
                shadow_icon = Image.open(os.path.join(SOURCE_PATH, "pokemonGO", "shadow_GO.png")).convert("RGBA").resize(cfg["go_badge_size"])
                im.paste(shadow_icon, (pos[0] + cfg["shadow_offset"][0] + step_x * p, pos[1] + cfg["shadow_offset"][1]), mask=shadow_icon)

            if mon.purified:
                purified_icon = Image.open(os.path.join(SOURCE_PATH, "pokemonGO", "purified_GO.png")).convert("RGBA").resize(cfg["go_badge_size"])
                im.paste(purified_icon, (pos[0] + cfg["shadow_offset"][0] + step_x * p, pos[1] + cfg["shadow_offset"][1]), mask=purified_icon)

            if mon.best_friend:
                best_friend_icon = Image.open(os.path.join(SOURCE_PATH, "pokemonGO", "best_buddy_GO.png")).convert("RGBA").resize(cfg["go_badge_size"])
                im.paste(best_friend_icon, (pos[0] + cfg["best_friend_offset"][0] + step_x * p, pos[1] + cfg["best_friend_offset"][1]), mask=best_friend_icon)


    return im

def draw_background_image(background, topcut, is_instagram: bool = False):#
    if topcut.image != "" and topcut.show_background:
        # Decode base64 string to bytes
        image_data = base64.b64decode(topcut.image)
        tour_icon = Image.open(io.BytesIO(image_data)).convert("RGBA")

        w, h = background.size

        # Calculate proportional size based on background dimensions
        width, height = tour_icon.size
        max_width = int(w * 0.8)
        max_height = int(h * 0.6)

        is_ig = is_instagram or (w == 3240)

        # Limit the height for standard template based on the 8 player height
        if not is_ig and max_height > 533:
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
        header_offset = 401 if is_ig else 136
        centered_x = (w - tour_icon.width) // 2
        centered_y = (h - tour_icon.height + header_offset) // 2

        background.paste(tour_icon, (centered_x, centered_y), mask=tour_icon)

    return background

def draw_header(im, topcut, is_instagram: bool = False):
    is_ig = is_instagram or (im.size[0] == 3240)

    if is_ig:
        header_bar_name = os.path.join("instagramMode", "header_bar.png")
        bar_y = 121
        f_bold = font_bold_IG
        f_regular = font_regular_IG
        f_title_jp = font_title_JP_IG
        f_format_jp = font_format_JP_IG
        icon_h = 471
        icon_pos = (65, 74)
        text_x = 589 if topcut.image != "" and topcut.show_logo else 177
        tour_name_y = 236
        format_y = 339
        date_multiline_y = 339
        date_centered_y = 289
        positions = [
            ((3181, 236), (3181, 339)), #Label - Count Positions
            ((2975, 236), (2975, 339)),
            ((2769, 236), (2769, 339)),
        ]
    else:
        header_bar_name = "header_bar.png"
        bar_y = 41
        f_bold = font_bold
        f_regular = font_regular
        f_title_jp = font_title_JP
        f_format_jp = font_format_JP
        icon_h = 160
        icon_pos = (22, 25)
        text_x = 200 if topcut.image != "" and topcut.show_logo else 60
        tour_name_y = 80
        format_y = 115
        date_multiline_y = 115
        date_centered_y = 98
        positions = [
            ((1080, 80), (1080, 115)), #Label - Count Positions
            ((1010, 80), (1010, 115)),
            ((940, 80), (940, 115)),
        ]

    # Paste header bar background
    header_bar = Image.open(os.path.join(SOURCE_PATH, header_bar_name))
    im.paste(header_bar, (0, bar_y))

    # Determine available tour icons - deprecated to remove TPCi copyrighted logos
    # formats = [Path(tour_img).stem for tour_img in os.listdir(os.path.join(SOURCE_PATH, "tours"))]
    # Paste tour icon if available
    if(topcut.image != "" and topcut.show_logo):
        # Decode base64 string to bytes
        image_data = base64.b64decode(topcut.image)

        tour_icon = Image.open(io.BytesIO(image_data)).convert("RGBA")
        width, height = tour_icon.size
        tour_icon = tour_icon.resize((width * icon_h // height, icon_h))
        im.paste(tour_icon, icon_pos, mask=tour_icon)
    #else:
    #    if topcut.tour_type.lower() in formats:
    #        tour_icon = Image.open(os.path.join(SOURCE_PATH, "tours", topcut.tour_type.lower() + ".png"))
    #        width, height = tour_icon.size
    #        tour_icon = tour_icon.resize((width * icon_h // height, icon_h))
    #        im.paste(tour_icon, icon_pos, mask=tour_icon)

    d = ImageDraw.Draw(im)

    # Tournament name & format positioning depends on whether we have a tour icon
    #if topcut.tour_type.lower() in formats or topcut.image != "":
    font_name = f_title_jp if contains_cjk_characters(topcut.tour_name) else f_bold
    font_format = f_format_jp if contains_cjk_characters(str(topcut.format)) else f_regular
    d.text((text_x, tour_name_y), topcut.tour_name, fill="white", anchor="ls", font=font_name)
    d.text((text_x, format_y), str(topcut.format), fill="white", anchor="ls", font=font_format)

    divisions = [
        ("MA", topcut.divisions.master),
        ("SR", topcut.divisions.senior),
        ("JR", topcut.divisions.junior),
    ]

    visible = [(label, count) for label, count in divisions if count > 0]

    if len(visible) == 3:
        date_x = 2533 if is_ig else 860
        date_y = date_multiline_y if len(topcut.tour_name) > 38 else date_centered_y
        d.text((date_x, date_y), str(topcut.date), fill="white", anchor="rs", font=f_bold)
    elif len(visible) == 2:
        date_x = 2739 if is_ig else 930
        date_y = date_multiline_y if len(topcut.tour_name) > 48 else date_centered_y
        d.text((date_x, date_y), str(topcut.date), fill="white", anchor="rs", font=f_bold)
    elif len(visible) == 1:
        date_x = 2945 if is_ig else 1000
        date_y = date_multiline_y if len(topcut.tour_name) > 53 else date_centered_y
        d.text((date_x, date_y), str(topcut.date), fill="white", anchor="rs", font=f_bold)

    if len(visible) > 0:
        last_x = positions[len(visible) - 1][0][0]
        if is_ig:
            d.rectangle([last_x - 162, 171, last_x - 156, 345], fill="white")
        else:
            d.rectangle([last_x - 55, 58, last_x - 53, 117], fill="white")

    for i, (label, count) in enumerate(visible):
        label_pos, count_pos = positions[i]

        d.text(label_pos, label, fill="white", anchor="rs", font=f_bold)
        d.text(count_pos, str(count), fill="white", anchor="rs", font=f_bold)

    return im