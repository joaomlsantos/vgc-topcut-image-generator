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


class Player(BaseModel):
    name: str
    pokepast: str


class TopCut(BaseModel):
    tour_name: str
    tour_type: TournamentType
    players: List[Player]

