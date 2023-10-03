from model import TournamentType, Player, TopCut
import io
from PIL import Image, ImageDraw, ImageFont
import os
from model import TournamentType, Player, TopCut
from urllib.request import urlopen
from pokepast import parsePokepast



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

def generateTopcut(topcut):
    image = genTemplate(topcut)
    buf = io.BytesIO()
    image.save(buf, "PNG")
    return buf.getvalue()



def genTemplate(topcut):
    SOURCE_PATH = "../img"
    #POKEMON_ICONS_SRC = "https://limitlesstcg.s3.us-east-2.amazonaws.com/pokemon/gen9/"
    POKEMON_ICONS_SRC = "https://projectpokemon.org/images/sprites-models/sv-sprites-home/"
    LOCAL_POKEMON_ICONS_SRC = "../img/pokemon/projectpokemon/"
    LOCAL_ITEM_ICONS_SRC = "../img/items/item_"
    LOCAL_TERA_ICONS_SRC = "../img/teras/"

    font_regular = ImageFont.truetype("../fonts/Montserrat/static/Montserrat-Regular.ttf", 24)
    font_bold = ImageFont.truetype("../fonts/Montserrat/static/Montserrat-Bold.ttf", 24)



    tour_icon = Image.open(os.path.join(SOURCE_PATH, "tours/" + topcut.tour_type.lower() + ".png"))

    template = Image.open(os.path.join(SOURCE_PATH, "template.png"))

    w = template.size[0]
    h = template.size[1]

    im = Image.new("RGBA", (template.size[0], template.size[1]))

    background = Image.open(os.path.join(SOURCE_PATH, "background.png"))
    background = background.convert("RGBA")
    background = background.crop((0,0,w,h))
    im.paste(background, (0,0), mask=background)

    im.paste(template, (0, 0), mask=template)
    im.paste(tour_icon, (22, 40), mask=tour_icon)

    d = ImageDraw.Draw(im)
    d.text((280,140), topcut.tour_name, fill="black", anchor="ms", font=font_regular)
    for i in range(len(topcut.players)):
        icon_pokemon_y = 0
        if(i % 2 == 0):
            d.text((180, 253 + 150*(i//2)), topcut.players[i].name, fill="white", anchor="ls", font=font_bold)
        else:
            d.text((720, 293 + 150*(i//2)), topcut.players[i].name, fill="white", anchor="ls", font=font_bold)

        icon_pokemon_y = 280 + (40 * (i % 2)) + 150*(i//2)
        icon_pokemon_x_base = 50 if (i % 2 == 0) else 590
        icon_item_y = 320 + (40 * (i % 2)) + 150*(i//2)
        icon_item_x_base = 90 if (i % 2 == 0) else 625
        icon_tera_y = 270 + (40 * (i % 2)) + 150*(i//2)
        icon_tera_x_base = 86 if (i % 2 == 0) else 621

        pokepast = parsePokepast(topcut.players[i].pokepast)
        for p in range(len(pokepast)):
            icon_name = pokepast[p].name.lower().replace(" ", "-")
            pokemon_icon_id = pokemonindex[icon_name]
            if(not os.path.isfile(LOCAL_POKEMON_ICONS_SRC + pokemon_icon_id + ".png")):
                print(POKEMON_ICONS_SRC + pokepast[p].name.lower().replace(" ", "-") + ".png")
                icon_url = urlopen(POKEMON_ICONS_SRC + pokemon_icon_id + ".png")
                content = icon_url.read()
                with open(LOCAL_POKEMON_ICONS_SRC + pokemon_icon_id + ".png", "wb") as download:
                    download.write(content)
            
            p_icon = Image.open(LOCAL_POKEMON_ICONS_SRC + pokemon_icon_id + ".png")
            p_icon = p_icon.convert("RGBA")
            p_icon = p_icon.resize((64,64))
            im.paste(p_icon, (icon_pokemon_x_base + 80*p, icon_pokemon_y), mask=p_icon)

            item_icon = Image.open(LOCAL_ITEM_ICONS_SRC + itemIndex[pokepast[p].item] + ".png")
            item_icon = item_icon.convert("RGBA")
            item_icon = item_icon.resize((24,24))
            im.paste(item_icon, (icon_item_x_base + 80*p, icon_item_y), mask=item_icon)

            tera_icon = Image.open(LOCAL_TERA_ICONS_SRC + pokepast[p].tera.lower() + ".png")
            tera_icon = tera_icon.convert("RGBA")
            tera_icon = tera_icon.resize((32,32))
            im.paste(tera_icon, (icon_tera_x_base + 80*p, icon_tera_y), mask=tera_icon)



    #icon_test = Image.open(urlopen(POKEMON_ICONS_SRC + "ogerpon.png"))
    #icon_test = icon_test.resize((56,56))
    #im.paste(icon_test, (60, 280), mask=icon_test)



    

    return im




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