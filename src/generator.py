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

cp_distribution = {}    # tour_type -> (points, kicker)
cp_distribution["PREMIER"] = [(30, 0), (16, 0), (12, 0), (8, 17), (6, 48), (4, 80)]
cp_distribution["MSS"] = [(50, 0), (40, 0), (32, 0), (25, 17), (20, 48), (16, 80), (13, 128)]
cp_distribution["OLDREGIONAL"] = [(200, 0), (160, 0), (130, 0), (100, 0), (80, 48), (60, 80), (50, 128), (40, 256), (30, 512), (20, 1024)]
cp_distribution["OLDINTERNATIONAL"] = [(500, 0), (400, 0), (320, 0), (250, 0), (200, 48), (160, 80), (130, 128), (100, 256), (80, 512), (60, 1024), (50, 2046)]
cp_distribution["CUP"] = [(50, 0), (40, 4), (32, 8), (25, 17), (20, 48), (16, 80), (13, 128)]
cp_distribution["CHALLENGE"] = [(15, 0), (12, 4), (10, 8), (8, 17), (6, 48), (4, 80)]
cp_distribution["REGIONAL"] = [(350, 0), (325, 4), (300,8), (280, 17), (160, 33), (125, 65), (100, 129), (80, 257), (60, 513), (40, 1025), (20, 2049)]
cp_distribution["INTERNATIONAL"] = [(750, 0), (700, 4), (650,8), (600, 17), (400, 33), (350, 65), (250, 129), (150, 257), (120, 513), (80, 1025), (40, 2049)]



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
    font_player = ImageFont.truetype("../fonts/Montserrat/static/Montserrat-Bold.ttf", 18)

    num_player_font = ImageFont.truetype("../fonts/Edo/edo.ttf", 24)



    template = Image.open(os.path.join(SOURCE_PATH, "fulltemplate_v2.png"))

    w = template.size[0]
    #h = template.size[1]

    total_p = len(topcut.players) - 1
    dynamic_height = 346 + (40 * (total_p % 2)) + 151*(total_p//2) + 50

    im = Image.new("RGBA", (template.size[0], dynamic_height))

    background = Image.open(os.path.join(SOURCE_PATH, "solid_background.png"))
    background = background.convert("RGBA")
    background = background.crop((0,0,w,dynamic_height))
    im.paste(background, (0,0), mask=background)

    header_bar = Image.open(os.path.join(SOURCE_PATH, "header_bar.png"))
    im.paste(header_bar, (0, 41))

    #im.paste(template, (0, 0), mask=template)


    if(topcut.tour_type in ["PREMIER", "MSS", "REGIONAL", "INTERNATIONAL", "CUP", "CHALLENGE", "OLDREGIONAL", "OLDINTERNATIONAL", "PREMIERBALL", "MASTERBALL"]):
        tour_icon = Image.open(os.path.join(SOURCE_PATH, "tours/" + topcut.tour_type.lower() + ".png"))
        im.paste(tour_icon, (22, 25), mask=tour_icon)

    d = ImageDraw.Draw(im)

    if(topcut.tour_type in ["PREMIER", "MSS", "REGIONAL", "INTERNATIONAL", "CUP", "CHALLENGE", "OLDREGIONAL", "OLDINTERNATIONAL", "PREMIERBALL", "MASTERBALL"]):
        #d.text((200,100), topcut.tour_name, fill="white", anchor="ls", font=font_bold)
        d.text((200,80), topcut.tour_name, fill="white", anchor="ls", font=font_bold)
        d.text((200,115), str(topcut.format), fill="white", anchor="ls", font=font_regular)
    else:
        #d.text((60,100), topcut.tour_name, fill="white", anchor="ls", font=font_bold)
        d.text((60,80), topcut.tour_name, fill="white", anchor="ls", font=font_bold)
        d.text((60,115), str(topcut.format), fill="white", anchor="ls", font=font_regular)


    #d.text((860,80), str(topcut.date), fill="white", anchor="rs", font=font_bold)
    #d.text((860,115), str(topcut.format), fill="white", anchor="rs", font=font_bold)
    d.text((860,98), str(topcut.date), fill="white", anchor="rs", font=font_bold)

    d.text((940,80), "JR", fill="white", anchor="rs", font=font_bold)
    d.text((1010,80), "SR", fill="white", anchor="rs", font=font_bold)
    d.text((1080,80), "MA", fill="white", anchor="rs", font=font_bold)

    d.text((940,115), str(topcut.divisions.junior), fill="white", anchor="rs", font=font_bold)
    d.text((1010,115), str(topcut.divisions.senior), fill="white", anchor="rs", font=font_bold)
    d.text((1080,115), str(topcut.divisions.master), fill="white", anchor="rs", font=font_bold)


    pokepastTeams = []      # this is a hack; i'm too sleepy to change the Player class in the proper way rn


    mult_2 = 0
    for i in range(len(topcut.players)):
        player_el = Image.open(os.path.join(SOURCE_PATH, "player_element_circles.png"))
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
        if(len(player_name) > 23):
            p_names = player_name.split()
            if(len(p_names) > 2):   #cut middle names
                p_names = [p_names[0], p_names[-1]]
                if(len(" ".join(p_names)) <= 23):
                    player_name = " ".join(p_names)
                else:
                    p_names[-1] = p_names[-1][0] + "."
                    player_name = " ".join(p_names)
            else:
                p_names[-1] = p_names[-1][0] + "."
                player_name = " ".join(p_names)

        if(topcut.tour_type in ["PREMIERBALL", "MASTERBALL", "GRASSROOTS", "WORLDS"]):
            if(i % 2 == 0):
                d.text((108, 253 + 150*(i//2)), player_name, fill="white", anchor="ls", font=font_player)
                d.text((500, 253 + 150*(i//2)), topcut.players[i].record, fill="white", anchor="rs", font=font_player)
            else:
                d.text((646, 293 + 150*(i//2)), player_name, fill="white", anchor="ls", font=font_player)
                d.text((1038, 293 + 150*(i//2)), topcut.players[i].record, fill="white", anchor="rs", font=font_player)
        else:
            if(i % 2 == 0):
                d.text((108, 253 + 150*(i//2)), player_name, fill="white", anchor="ls", font=font_player)
                d.text((412, 253 + 150*(i//2)), topcut.players[i].record, fill="white", anchor="rs", font=font_player)
            else:
                d.text((646, 293 + 150*(i//2)), player_name, fill="white", anchor="ls", font=font_player)
                d.text((950, 293 + 150*(i//2)), topcut.players[i].record, fill="white", anchor="rs", font=font_player)

        icon_pokemon_y = 274 + (41 * (i % 2)) + 151*(i//2)
        icon_pokemon_x_base = 49 if (i % 2 == 0) else 587
        icon_item_y = 320 + (40 * (i % 2)) + 150*(i//2)
        icon_item_x_base = 94 if (i % 2 == 0) else 632
        icon_tera_y = 270 + (40 * (i % 2)) + 150*(i//2)
        icon_tera_x_base = 93 if (i % 2 == 0) else 631

        pokepast = parsePokepast(topcut.players[i].pokepast)
        
        pokepastTeams.append(pokepast)  # change this in the future to be in the Player class
        

        for p in range(len(pokepast)):
            print(pokepast[p])
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
            p_icon = p_icon.resize((60,60))
            im.paste(p_icon, (icon_pokemon_x_base + 80*p, icon_pokemon_y), mask=p_icon)

            if(pokepast[p].item != ""):
                item_icon = Image.open(LOCAL_ITEM_ICONS_SRC + itemIndex[pokepast[p].item] + ".png")
                item_icon = item_icon.convert("RGBA")
                item_icon = item_icon.resize((24,24))
                im.paste(item_icon, (icon_item_x_base + 80*p, icon_item_y), mask=item_icon)

            if(pokepast[p].tera.strip().lower() != ""):
                tera_icon = Image.open(LOCAL_TERA_ICONS_SRC + pokepast[p].tera.strip().lower() + ".png")
                tera_icon = tera_icon.convert("RGBA")
                tera_icon = tera_icon.resize((32,32))
                im.paste(tera_icon, (icon_tera_x_base + 80*p, icon_tera_y), mask=tera_icon)



    #icon_test = Image.open(urlopen(POKEMON_ICONS_SRC + "ogerpon.png"))
    #icon_test = icon_test.resize((56,56))
    #im.paste(icon_test, (60, 280), mask=icon_test)


    usages = computeUsage(pokepastTeams)
    

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
