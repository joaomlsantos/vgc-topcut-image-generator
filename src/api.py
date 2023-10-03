from fastapi import FastAPI
import generator
from fastapi.responses import Response
from model import TournamentType, Player, TopCut



app = FastAPI()

@app.post("/topcut")
async def postTopcut(topcut: TopCut):
    image_bytes = generator.generateTopcut(topcut)
    return Response(content=image_bytes, media_type="image/png")