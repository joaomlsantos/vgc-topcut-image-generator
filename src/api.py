from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import generator
from model import TournamentType, Player, TopCut, TomHtmlUrl
import base64
from typing import Union
import tom_html_parser
import uvicorn





app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

allowed_formats = ["base64", "png"]


@app.post("/topcut/{format}")
async def postTopcut(topcut: TopCut, format: Union[str, None] = None):
    if((format != None) and (format not in allowed_formats)):
        raise HTTPException(status_code=400, detail="Format not allowed; please omit the parameter or use one of the following formats: " + ",".join(allowed_formats))
    
    image_bytes = generator.generateTopcut(topcut)
    
    if(format == "png"):
        return Response(content=image_bytes, media_type="image/png")
    if(format == "base64"):
        encoded_img = base64.b64encode(image_bytes)
        # return Response(content=encoded_img, media_type="image/png")
        return "data:image/png;base64," + encoded_img.decode("utf-8")
    return Response(content=image_bytes, media_type="image/png")


@app.post("/pairings")
async def postPairings(url: TomHtmlUrl):
    pairings = tom_html_parser.parseTomHtml(url)
    return pairings

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)