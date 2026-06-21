import requests
import sqlite3

def player_stats(player, league=None, sport=None):
    id = db_lookup(player)
    if id is not None:
        if len(db_lookup_all_ids(player)) == 1:
            player_id, player_sport, player_league = id
        else:
            ids = db_lookup_all_ids(player)
            stats_summary_output = ""
            for p in ids:
                player_id = p[0]
                player_sport = p[2]
                player_league= p[3]
                url = f"https://site.web.api.espn.com/apis/common/v3/sports/{player_sport}/{player_league}/athletes/{player_id}/"
                response = requests.get(url).json()
                display_name = response['athlete']['displayName']
                player_stat_block = ""
                year = response['athlete']['statsSummary']['displayName']
                player_stat_block += f"{display_name}\n{year}\n"
                try:
                    stats_summary = response['athlete']['statsSummary']
                    stats = stats_summary['statistics']
                    #year = stats_summary['displayName']
                    for s in stats:
                        #year = stats_summary["displayName"]
                        stat_name = s['shortDisplayName']
                        display_value = s['displayValue']
                        rank = s['rankDisplayValue']
                        stats_formating = f"{stat_name} {display_value} Rank: {rank}\n"
                        player_stat_block += stats_formating
                    #stats_summary_output = f"{display_name}\n{stats_summary_output}"

                except:
                    player_stat_block = f"{display_name} has no stats\n"
                #stats_summary_output += year
                stats_summary_output += player_stat_block
                #stats_summary_output = f"{display_name}\n" + stats_summary_output
            print(stats_summary_output)
            return stats_summary_output
            
    else:
        return "not ready yet"
    url = f"https://site.web.api.espn.com/apis/common/v3/sports/{player_sport}/{player_league}/athletes/{player_id}/"
    response = requests.get(url)
    data = response.json()
    athlete_display_name = data['athlete']['displayName']
    stats_summary = data['athlete']['statsSummary']
    display_name = stats_summary['displayName']
    stats = stats_summary['statistics']
    year = data['athlete']['statsSummary']['displayName']
    stats_summary_output = f"{athlete_display_name}\n{display_name}\n"
    for s in stats:
        stat_name = s['shortDisplayName']
        display_value = s['displayValue']
        try:
            rank = s["rankDisplayValue"]
        except:
            rank = "n/a"
        stats_formating = f"{stat_name} {display_value} Rank: {rank}\n"
        stats_summary_output += stats_formating
    #print(stats_summary_output)
    return stats_summary_output

def player_search(player, league=None, sport=None):
    id = db_lookup(player)
    #print(id)
    if id is not None:
        player_id, player_sport, player_league = id #id contains 3 elements from the db_lookup()
    else: #bot asks to enter a legue
        sports_map = {
            "mlb": "baseball",
            "nfl": "football",
            "nhl": "hockey",
        }
        if league in sports_map:
            sport = sports_map[league]
        print(f"Searching {league}")
        url = f"https://sports.core.api.espn.com/v3/sports/{sport}/{league}/athletes/"
        page_count = 1
        response = requests.get(url)
        data = response.json()
        pages = data["pageCount"]
        found = False
        #print(data)
        while page_count <= pages and not found:
            url = f"https://sports.core.api.espn.com/v3/sports/{sport}/{league}/athletes?page={page_count}"
            response = requests.get(url)
            data = response.json()
            for i in data["items"]:
                if player == i["displayName"]:
                    found = True
                    id = i["id"]
                    name = i["displayName"]
                    print(id, name)
                    con = sqlite3.connect("ESPN_player_ids.db")
                    cur = con.cursor()
                    sql = "INSERT INTO ids(id, name, sport, league) VALUES (?, ?, ?, ?)"
                    params = (id, name, sport, league)
                    cur.execute(sql, params)
                    con.commit()
                    con.close()
                    player_id = id 
                    player_sport = sport
                    player_league = league
                    break
            page_count += 1
        if not found:
            return f"Player not found"
    # getting the bio elements
    response = requests.get(f"https://sports.core.api.espn.com/v3/sports/{player_sport}/{player_league}/athletes/{player_id}/")
    data = response.json()
    display_name = data["displayName"]
    weight = data["displayWeight"]
    height = data["displayHeight"]
    age = data["age"]
    birth_city = data["birthPlace"]["city"]
    try:
        birth_state = data["birthPlace"]["state"]
    except:
        birth_state = data["birthPlace"]["country"]
    try:
        hand = data["hand"]["abbreviation"]
    except:
        hand = None
    response = requests.get(f"https://site.web.api.espn.com/apis/common/v3/sports/{player_sport}/{player_league}/athletes/{player_id}/")
    data = response.json()
    #print(data)
    experience = data["athlete"]["displayExperience"]
    try:
        draft = data["athlete"]["displayDraft"]
    except:
        draft = None
        debut_year = data["athlete"]["debutYear"]
    try:
        team = data["athlete"]["team"]["displayName"]
    except:
        team = "N/A"
    try:
        position = data["athlete"]["position"]["abbreviation"]
    except:
        position = "N/A"
    try:
        bat_throw = data["athlete"]["displayBatsThrows"]
    except:
        bat_throw = None

    player_bio = (
        f"Name: {display_name}\n"
        f"Age: {age}\n"
        f"Team: {team}\n"
        f"Position: {position}\n"
    )
    if bat_throw is not None:
        player_bio += f"Bats/throws: {bat_throw}\n"
    if hand is not None:
        player_bio += f"Shoots: {hand}\n"
    player_bio += (
        f"Experience: {experience}\n"
        f"Height: {height}, Weight: {weight}\n"
        f"Birthplace: {birth_city}, {birth_state}\n"
    )
    if draft is not None:
        player_bio += f"Draft: {draft}"
    else:
        player_bio += f"Debut: {debut_year}"
    print(display_name, weight, height, age, experience, draft)
    return player_bio

def db_lookup(player):
    con = sqlite3.connect("ESPN_player_ids.db")
    cur = con.cursor()
    sql = "SELECT * FROM ids WHERE name = ?"
    params = (player,)
    query = cur.execute(sql,params)
    query = query.fetchone()
    if query is None:
        return print(type(query))
    id = query[0]
    sport = query[2]
    league = query[3]
    con.close()
    print(id,sport,league)
    return id,sport,league

def db_lookup_all_ids(player):
    con = sqlite3.connect('ESPN_player_ids.db')
    cur = con.cursor()
    sql = "SELECT * FROM ids WHERE name = ?"
    params = (player,)
    query = cur.execute(sql, params)
    query = query.fetchall()
    #id = query[0]
    #sport = query[2]
    #league = query[3]
    con.close()
    print(query)
    return query

def espn_scoreboard(team=None, league=None):
    team_alt_name = {
        "Leafs": "Maple Leafs",
        "Habs": "Canadiens",
        "Rags": "Rangers",
        "Devs": "Devils",
        "Isles": "Islanders",
        "Avs": "Avalanche",
        "Pens": "Penguins",
        "Caps": "Capitals",
        "Pats": "Patriots"
    }
    leagues_and_sports = {
        "nfl": "football",
        "nhl": "hockey",
        "mlb": "baseball",
        "nba": "basketball"
    }
    if team in team_alt_name:
        team = team_alt_name[team]
    if league is not None:
        day_score_board = ""
        final_games = ""
        if league in leagues_and_sports:
            sport = leagues_and_sports[league]
            url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard"
            response = requests.get(url)
            data = response.json()
            league_data = data['leagues']
            events_data = data['events']
            try:
                week = data['week']['number']
                week = f"week {week}"
            except:
                week = data['day']['date']
                pass
            day_score_board += f"scoreboard for: {week}"
            #print(week)
            for event in events_data:
                for c in event['competitions']:
                    team_one = c['competitors'][0]
                    team_two = c['competitors'][1]
                    if team_one['homeAway'] == 'home':
                        home_team = team_one
                        away_team = team_two
                    else:
                        away_team = team_one
                        home_team = team_two
                    home_team_name = home_team['team']['shortDisplayName']
                    away_team_name = away_team['team']['shortDisplayName']
                    home_team_abbrev = home_team['team']['abbreviation']
                    away_team_abbrev = away_team['team']['abbreviation']
                    broadcast = c['broadcast']
                    home_score = home_team['score']
                    away_score = away_team['score']
                    status = c["status"]["type"]["shortDetail"]
                    score_board = (f"{away_team_abbrev} {away_score} @ {home_team_abbrev} {home_score} - {status} ")
                    if status == 'Final' or status == 'Final/OT' or status == 'Final/SO':
                        #score_board = score_board
                        final_games += f"\n{score_board}"
                    else:
                        score_board += f"{broadcast}"
                        day_score_board += f"\n{score_board}"
                    #day_score_board += f"\n{score_board}" #team_two)
        day_score_board += final_games
            #day_score_board += final_games
        #print (day_score_board)
        return day_score_board
                
        # call leagues scoreboard
    if team is not None:
        team_scoreboard = ""
        for league, sport in leagues_and_sports.items():
            url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard"
            print(url)
            response = requests.get(url)
            data = response.json()
            league_data = data['leagues']
            #print(league_data['season'])
            for s in league_data:
                league_season = s['season']['year']
                # for t in league_data['season']
                season_type = s['season']['type']['name']
            for event in data["events"]:
                for t in event['competitions']:
                    team_one = t['competitors'][0]
                    team_two = t['competitors'][1]
                    for teams in t["competitors"]:
                        team_name = teams["team"]["shortDisplayName"]
                        if team == team_name:
                            #print(team_one, team_two)
                            event_name = event["name"]
                            if team_one['homeAway'] == "home":
                                home_team = team_one
                                away_team = team_two
                            else:
                                away_team = team_one
                                home_team = team_two
                            #season_year = league_data["season"]["year"]
                            home_team_name = home_team['team']['shortDisplayName']
                            away_team_name = away_team['team']['shortDisplayName']
                            home_team_score = home_team["score"]
                            away_team_score = away_team["score"]
                            status = t["status"]["type"]["shortDetail"]
                            score_board = (
                                #f"{league_season} {season_type}\n"
                                f"{away_team_name} {away_team_score}\n"
                                f"{home_team_name} {home_team_score}\n"
                                f"{status}\n"
                            )
                            team_scoreboard += f"\n{score_board}"
                            #team_scoreboard = score_board
        if team_scoreboard == "":
            return "no games"
        else:
            return team_scoreboard
        
def espn_standings(conference=None, division=None):
    base_url = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2025/types/2/groups"
    response = requests.get(base_url).json()
    for i in response['items']:
        conf = requests.get(i['$ref']).json()
        if conference == conf['abbreviation']:
            standings_url = conf['standings']['$ref']
            print(standings_url)
            standings_call = requests.get(standings_url).json()
            items = standings_call['items']
            for i in items:
                if i['name'] == "playoff":
                    overall_standings_url = i['$ref']
                    conf_standings = requests.get(overall_standings_url).json()
                    for t in conf_standings['standings']:
                        team_list = t['team']
                        team_url = team_list['$ref']
                        record = t['records']
                        for r in record:
                            if r['name'] == 'overall':
                                record_value = r['displayValue']
                                stats = r['stats']
                                print(stats[0])




if __name__ == "__main__":
    espn_standings("NFC")
# my_dict = {"nfl": "football", "nhl": "hockey"}
# for item, sport in my_dict.items():
#     print(item, sport)