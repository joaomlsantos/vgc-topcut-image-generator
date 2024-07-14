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

class TomHtmlUrl(BaseModel):
    url: str
