import requests
import sqlite3
from leagues import LEAGUES_AND_SPORTS, DIVISION_TO_LEAGUE, team_alt_name, CONFERENCE_AND_LEAGUES

def player_stats(player, league=None, sport=None):
    player = player.title()
    ids = db_lookup_all_ids(player)
    if not ids:
        return "player not in db"
    stats_list = []
    for row in ids:
        player_id, player_name, player_sport, player_league = row
        url = f"https://site.web.api.espn.com/apis/common/v3/sports/{player_sport}/{player_league}/athletes/{player_id}/"
        response = requests.get(url).json()
        display_name = response["athlete"]["displayName"]
        stats_summary = response["athlete"].get("statsSummary", {})
        if not stats_summary:
            stats_list.append(f"{display_name} has no stats")
            continue
        stats = stats_summary.get("statistics", [])
        if not stats:
            stats_list.append(f"{display_name} has no stats")
            continue
        year = stats_summary["displayName"]
        stats_list.append(f"{display_name}\n{year}")
        for s in stats:
            stat_name = s["shortDisplayName"]
            display_value = s["displayValue"]
            rank = s.get("rankDisplayValue", "n/a")
            stats_list.append(f"{stat_name} {display_value} Rank: {rank}")
    return "\n".join(stats_list)

def player_search(player, league=None, sport=None):
    id = db_lookup(player)
    #print(id)
    if id is not None:
        player_id, player_sport, player_league = id #id contains 3 elements from the db_lookup()
    else: #bot asks to enter a legue to build the link
        if league in LEAGUES_AND_SPORTS:
            sport = LEAGUES_AND_SPORTS[league]
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
    if team in team_alt_name:
        team = team_alt_name[team]
    if league is not None:
        day_score_board = ""
        final_games = ""
        if league not in LEAGUES_AND_SPORTS:
            return f"unknown league: {league}"
        sport = LEAGUES_AND_SPORTS[league]
        url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard"
        response = requests.get(url)
        data = response.json()
        league_data = data['leagues']
        events_data = data['events']
        try: #try for week number, for NFL. NFL groups schedule by weeks 
            week = data['week']['number']
            week = f"week {week}"
        except:
            week = data['day']['date']
            #pass
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
        for league, sport in LEAGUES_AND_SPORTS.items():
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
        
def division_standings(division=None, league=None):
    if not division:
        return f"Enter a division"
    division = division.strip().lower()
    if division not in DIVISION_TO_LEAGUE:
        return f"unknown division: {division}"
    options = DIVISION_TO_LEAGUE[division]
    if len(options) > 1 and league is None:
        leagues = []
        for league, canonical in options:
            leagues.append(league)
        return leagues
    if league is None:
        league, canonical = options[0]
    else:
        canonical = None
        for opt_league, opt_canonical in options:
            if opt_league == league:
                canonical = opt_canonical
                break
        if canonical is None:
            return f"{league} not found"
    sport = LEAGUES_AND_SPORTS[league]
    base_url = f"https://site.api.espn.com/apis/v2/sports/{sport}/{league}/standings?level=3"
    response = requests.get(base_url).json()
    standing_list = []
    def walk_standings(node):
        if node.get("name") == canonical:
            standing_list.append(f"{canonical} standings")
            for entry in node.get("standings", {}).get("entries", []):
                team = entry.get("team", {}).get("shortDisplayName")
                record = None
                gb = None
                wins = None
                losses = None
                for s in entry["stats"]:
                    if s["name"] == "overall": #overall record
                        record = s["displayValue"]
                    elif s["name"] == "gamesBehind":
                        gb = s["displayValue"]
                    elif s["name"] == "wins":
                        wins = s["displayValue"]
                    elif s["name"] == "losses":
                        losses = s["displayValue"]
                if record is None: #for NBA
                    record = f"{wins}-{losses}"
                if sport == "hockey": #hockey doesnt typically use games back
                    standing_list.append(f"{team} {record}")
                else:
                    standing_list.append(f"{team} {record} GB: {gb}")
        for child in node.get("children", []):
            walk_standings(child)
    walk_standings(response)
    return "\n".join(standing_list)

def wildcard_standings(conference=None):
    if not conference:
        return f"enter a conference"
    conference = conference.strip().lower()
    if conference not in CONFERENCE_AND_LEAGUES:
        return f"unknown conference: {conference}"
    league, canonical = CONFERENCE_AND_LEAGUES[conference]
    sport = LEAGUES_AND_SPORTS[league]
    base_url = f"https://site.api.espn.com/apis/v2/sports/{sport}/{league}/standings?level=2"
    response = requests.get(base_url).json()
    wc_standings_list = []
    playoff_seed_sort = []
    for s in response["children"]:
        if s["name"] == canonical:
            wc_standings_list.append(f"{canonical} Wildcard standings:")
            for t in s["standings"]["entries"]:
                team = t["team"]["shortDisplayName"]
                wins = None
                losses = None
                playoff_seed = None
                for e in t["stats"]:
                    if e["name"] == "wins":
                        wins = e["value"]
                    elif e["name"] == "losses":
                        losses = e["value"]
                    elif e["name"] == "playoffSeed":
                        playoff_seed = e["value"]
                playoff_seed_sort.append((playoff_seed, team, wins, losses))
    if not playoff_seed_sort:
        return f"no wild card data for that conference"
    seed_sort = sorted(playoff_seed_sort)
    seed_sort = seed_sort[3:]
    cut_seed, cut_team, cut_wins, cut_losses = seed_sort[2]
    for i, wc_teams in enumerate(seed_sort):
        seed, team, wins, losses = wc_teams
        gb = ((cut_wins - wins) + (losses - cut_losses)) / 2
        if gb < 0:
            gb = f"+{-gb}"
        wc_standings_list.append(f"{i + 1} {team} {int(wins)}-{int(losses)} {gb}")
        if i == 2:
            wc_standings_list.append("---")
    return "\n".join(wc_standings_list)