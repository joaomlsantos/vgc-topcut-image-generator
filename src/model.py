from pydantic import BaseModel
from enum import Enum
from typing import List


class TournamentType(str, Enum):
    WEEKLY = "WEEKLY"
    GRASSROOTS = "GRASSROOTS"
    PREMIER = "PREMIER"
    MSS = "MSS"
    REGIONAL = "REGIONAL"
    INTERNATIONAL = "INTERNATIONAL"
    WORLDS = "WORLDS"
    CUP = "CUP"
    CHALLENGE = "CHALLENGE"
    OLDREGIONAL = "OLDREGIONAL"
    OLDINTERNATIONAL = "OLDINTERNATIONAL"
    GREATBALL = "GREATBALL"
    ULTRABALL = "ULTRABALL"
    PREMIERBALL = "PREMIERBALL"
    MASTERBALL = "MASTERBALL"
    PLAYERSCUPKR = "PLAYERSCUPKR"
    JAPANCHAMPIONSHIP = "JAPANCHAMPIONSHIP"

'''
set up to 
class TournamentType(BaseModel):
    name: str = ""
    img_path: str = ""
    hasChampionshipPoints: bool = False
'''


class Pokemon(BaseModel):
    name: str = ""
    teratype: str = ""
    item: str = ""
    gmax: bool = False
    shadow: bool = False
    best_friend: bool = False
    purified: bool = False

class Player(BaseModel):
    name: str = ""
    social: str = ""
    pokemon: List[Pokemon] = []
    record: str = ""
    flag: str = ""

class Division(BaseModel):
    junior: int = 0
    senior: int = 0
    master: int = 0

class GameType(str, Enum):
    VGC = "VGC"
    GO = "GO"

class TopCut(BaseModel):
    tour_name: str = ""
    tour_type: TournamentType
    divisions: Division
    players: List[Player]
    date: str = ""
    format: str = ""
    game: GameType = GameType.VGC
    image: str = ""
    show_logo: bool = False
    show_background: bool = False
    reorder: bool = False

class TomHtmlUrl(BaseModel):
    url: str

class PokemonStats(BaseModel):
    name: str = ""
    usage_count: int = 0

class Usage(BaseModel):
    tour_name: str = ""
    tour_type: TournamentType
    divisions: Division
    date: str = ""
    format: str = ""
    game: GameType = GameType.VGC
    image: str = ""
    show_logo: bool = False
    show_background: bool = False
    reorder: bool = False
    pokemon: List[PokemonStats] = []
