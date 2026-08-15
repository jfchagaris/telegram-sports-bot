import sqlite3
import requests
from leagues import LEAGUES_AND_SPORTS

con = sqlite3.connect("ESPN_player_ids.db")
cur = con.cursor()
sql = "CREATE TABLE IF NOT EXISTS ids(id INTEGER, name TEXT, sport TEXT, league TEXT, UNIQUE(id, sport, league))"
cur = cur.execute(sql)
con.commit()
for league, sport in LEAGUES_AND_SPORTS.items():
    print(f"Scraping {league} now")
    url = f"https://sports.core.api.espn.com/v3/sports/{sport}/{league}/athletes/"
    page_count = 1
    response = requests.get(url)
    data = response.json()
    pages = data["pageCount"]
    while page_count <= pages: # is not found:
        response = requests.get(f"https://sports.core.api.espn.com/v3/sports/{sport}/{league}/athletes?page={page_count}")
        data = response.json()
        for i in data["items"]:
            id = i["id"]
            try:
                name = i["displayName"]
            except KeyError:
                name = f"{i["firstName"]} {i["lastName"]}"
            if name.strip().startswith("["): #skip non player entries
                continue
            sql = "INSERT OR IGNORE INTO ids(id, name, sport, league) VALUES (?, ?, ?, ?)"
            params = (id, name, sport, league)
            cur.execute(sql,params)
        page_count += 1
        print(page_count)
con.commit()
con.close()