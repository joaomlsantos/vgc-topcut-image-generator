import unicodedata
from PIL import Image
import os
from pathlib import Path

# Constants
BASE_DIR = Path(__file__).resolve().parent.parent
LOCAL_FLAGS_SRC = str(BASE_DIR / "img" / "flags") + "/"

# Function to reorder newPokemon
def reorder_pokemon(pokemon_list, restricted_list, mythical_list):
    restricted_pokemon = [p for p in pokemon_list if p.name in restricted_list]
    mythical_pokemon = [p for p in pokemon_list if p.name in mythical_list]
    non_restricted_pokemon = [p for p in pokemon_list if p.name not in restricted_list and p.name not in mythical_list]
    return mythical_pokemon + restricted_pokemon + non_restricted_pokemon

def change_form_item(pokemon, item, forms_list):
    for form in forms_list:
        if form['name'] == pokemon and form['item_name'] == item:
            return form['final']
    # If no form matches, return the original pokemon
    return pokemon

# Function to detect Chinese/Japanese/Korean characters
def contains_cjk_characters(text):
    for char in text:
        name = unicodedata.name(char, '')
        if any(x in name for x in ['CJK', 'HIRAGANA', 'KATAKANA', 'HANGUL']):
            return True
    return False

def loadFlag(country_code, width):
    flag_path = os.path.join(LOCAL_FLAGS_SRC, f"{country_code.lower()}.png")
    if not os.path.isfile(flag_path):
        return None
    flag_img = Image.open(flag_path).convert("RGBA")
    img_width, img_height = flag_img.size
    if img_width != width:
        new_height = int(img_height * width / img_width)
        flag_img = flag_img.resize((width, new_height))
    return flag_img
