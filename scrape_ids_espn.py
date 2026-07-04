import sqlite3
import requests

con = sqlite3.connect("ESPN_player_ids.db")
cur = con.cursor()
sql = "CREATE TABLE IF NOT EXISTS ids(id INTEGER, name TEXT, sport TEXT, league TEXT, UNIQUE(id, sport, league))"
cur = cur.execute(sql)
con.commit()
sports_dict = {
    "nfl": "football",
    "nhl": "hockey",
    "mlb": "baseball",
    "nba": "basketball"
}
for league, sport in sports_dict.items():
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
            name = i["displayName"]
            #skip non player entries
            if name.strip().startswith("["):
                continue
            sql = "INSERT INTO ids(id, name, sport, league) VALUES (?, ?, ?, ?)"
            params = (id, name, sport, league)
            cur.execute(sql,params)
        page_count += 1
        print(page_count)
con.commit()
con.close()