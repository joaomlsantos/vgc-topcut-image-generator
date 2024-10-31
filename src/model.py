from pydantic import BaseModel
from enum import Enum
from typing import List, Optional


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


class Player(BaseModel):
    name: str
    pokepast: str
    record: str

class Division(BaseModel):
    junior: int
    senior: int
    master: int


class TopCut(BaseModel):
    tour_name: str
    tour_type: TournamentType
    divisions: Division
    players: List[Player]
    date: str
    format: str
    image_url: Optional[str] = None

class TomHtmlUrl(BaseModel):
    url: str
