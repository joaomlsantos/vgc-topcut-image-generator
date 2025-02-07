def roll(im, delta):
    """Roll an image sideways."""
    xsize, ysize = im.size

    delta = delta % xsize
    if delta == 0:
        return im

    part1 = im.crop((0, 0, delta, ysize))
    part2 = im.crop((delta, 0, xsize, ysize))
    im.paste(part1, (xsize - delta, 0, xsize, ysize))
    im.paste(part2, (0, 0, xsize - delta, ysize))

    return im


def merge(im1, im2):
    w = im1.size[0] + im2.size[0]
    h = max(im1.size[1], im2.size[1])
    im = Image.new("RGBA", (w, h))

    im.paste(im1)
    im.paste(im2, (im1.size[0], 0))

    return im

# Function to reorder newPokemon
def reorder_pokemon(pokemon_list, restricted_list):
    restricted_pokemon = [p for p in pokemon_list if p.name in restricted_list]
    non_restricted_pokemon = [p for p in pokemon_list if p.name not in restricted_list]
    return restricted_pokemon + non_restricted_pokemon
