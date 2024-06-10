import requests
from bs4 import BeautifulSoup
import bs4


class PokepastMon:
    def __init__(self):
        self.name = ""
        self.gender = ""
        self.ability = ""
        self.level = 50
        self.tera = ""
        self.evs = {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}
        self.moves = []
        self.item = ""
        self.nature = ""

    def __str__(self):
        return "%s @ %s\nAbility: %s\nLevel: %d\nTera Type: %s\nEVs: %s\n%s Nature\n%s" % (self.name, self.item, self.ability, self.level, self.tera, self.getEVsString(), self.nature, self.getMovesString())

        
    def __repr__(self):
        return str({"name": self.name, "gender": self.gender, "tera": self.tera, "item": self.item, "ability": self.ability, "nature": self.nature, "evs": self.evs, "level": self.level, "moves": self.getMovesString()})

    def getEVsString(self):
        res = []
        for s in ["HP", "Atk", "Def", "SpA", "SpD", "Spe"]:
            if(self.evs[s.lower()] > 0):
                res.append("%d %s" % (self.evs[s.lower()], s))
        return " / ".join(res)

    def getMovesString(self):
        res = ""
        for m in self.moves:
            res += "- %s\n" % m
        return res

    def getMonOptions(self):
        return {"item": self.item, "ability": self.ability, "nature": self.nature, "evs": self.evs, "level": self.level}

    

def parsePokepast(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    articles = soup.find_all("article")
    pokepast_team = []
    for a in articles:
        paste_mon = PokepastMon()
        p_soup = a.contents[3].contents
        name_soup = p_soup[0]
        if(type(name_soup) == bs4.element.Tag):
            paste_mon.name = name_soup.text
        elif(type(name_soup) == bs4.element.NavigableString and "@" in str(name_soup)):
            paste_mon.name = str(name_soup).split("(")[0].split("@")[0].strip()
        elif(type(name_soup) == bs4.element.NavigableString):
            paste_mon.name = p_soup[1].text
        for i in range(len(p_soup)):
            if(type(p_soup[i]) == bs4.element.Tag):
                if("class" in p_soup[i].attrs and "gender" in p_soup[i]["class"][0]):
                    paste_mon.gender = p_soup[i].text
                if("Ability:" in p_soup[i].text):
                    paste_mon.ability = str(p_soup[i+1]).strip()
                if("Level:" in p_soup[i].text):
                    paste_mon.level = int(p_soup[i+1])
                if("Tera Type:" in p_soup[i].text):
                    # paste_mon.tera = str(p_soup[i+1]).strip()
                    paste_mon.tera = p_soup[i+1].text
                if("class" in p_soup[i].attrs and "stat" in p_soup[i]["class"][0]):
                    stat = p_soup[i]["class"][0].split("-")[1]
                    paste_mon.evs[stat] = int(p_soup[i].text.split(" ")[0])
                if("class" in p_soup[i].attrs and "type-" in p_soup[i]["class"][0] and p_soup[i].text == "-"):
                    paste_mon.moves.append(str(p_soup[i+1]).split("\n")[0].strip())                
            if(type(p_soup[i]) == bs4.element.NavigableString):
                str_parts = str(p_soup[i]).split("\n")
                for temp_str in str_parts:
                    if("@" in temp_str):
                        paste_mon.item = temp_str.split("@")[1].strip()
                        if(paste_mon.item == "" and type(p_soup[i+1]) == bs4.element.Tag):   # hack to look for next span
                            paste_mon.item = p_soup[i+1].text
                    if(" Nature  " in temp_str):
                        paste_mon.nature = temp_str.strip().split(" ")[0]
                    if("-" == temp_str[0:1]):
                        paste_mon.moves.append(temp_str[1:].strip())
        pokepast_team.append(paste_mon)
    return pokepast_team
