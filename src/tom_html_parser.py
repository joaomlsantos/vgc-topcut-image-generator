import urllib
import urllib.request
from bs4 import BeautifulSoup
import bs4
import json



def parseTomHtml(url):
    url = 'https://victoryroadvgc.com/wp-content/uploads/2023/12/Midseason-Showdown-Dreamhackpairings.html'
    r = urllib.request.urlopen(url)
    r_html = r.read()
    soup = BeautifulSoup(r_html, "html.parser")

    tour_title = soup.body.b.string

    pairings = []

    tables = soup.find_all("table", {"class":"report"})
    trs = tables[0].find_all("tr")
    for tr in trs:
        try:
            tds = tr.find_all("td")
            if(len(tds) > 0):
                table_number = tr.find("td", {"class": "full"}).text
                first_player = tr.find("td", {"class": "left"}).text.replace(u'\xa0', u' ').split("(")
                first_player_parcel2 = first_player[2].split(")")
                
                fp_name = first_player[0].strip()
                fp_wl = first_player[1].strip()
                fp_score = first_player_parcel2[0]
                fp_division = first_player_parcel2[1].split("-")[1].strip()

                if(table_number == "Bye"):
                    pairings.append({
                        "player1": fp_name,
                        "wlratio1": fp_wl,
                        "score1": fp_score,
                        "division1": fp_division,
                        "player2": "BYE",
                        "wlratio2": "",
                        "score2": "",
                        "division2": ""
                    })
                    continue


                second_player = tr.find("td", {"class": "right"}).text.replace(u'\xa0', u' ').split("(")
                second_player_parcel2 = second_player[2].split(")")

                sp_name = second_player[0].strip()
                sp_wl = second_player[1].strip()
                sp_score = second_player_parcel2[0]
                sp_division = second_player_parcel2[1].split("-")[1].strip()

                pairings.append({
                    "player1": fp_name,
                    "wlratio1": fp_wl,
                    "score1": fp_score,
                    "division1": fp_division,
                    "player2": sp_name,
                    "wlratio2": sp_wl,
                    "score2": sp_score,
                    "division2": sp_division
                })
        except Exception as e:
            print(tr)
            print(e)

    return{"tour_name": tour_title, "pairings": pairings}
