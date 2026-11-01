
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


    font_regular = ImageFont.truetype(str(FONTS_DIR / "Montserrat" / "static" / "Montserrat-Bold.ttf"), 24)
    font = ImageFont.truetype(str(FONTS_DIR / "Montserrat" / "static" / "Montserrat-Bold.ttf"), 48)

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
