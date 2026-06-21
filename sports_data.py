import requests
from datetime import datetime
import pytz

def get_nhl_score(team_name):
    team_alt_name = {
        "leafs": "maple leafs",
        "habs": "canadiens",
    }
    url = 'https://api-web.nhle.com/v1/schedule/now'
    response = requests.get(url)
    data = response.json()
    games = data["gameWeek"][0]['games']
    if team_name in team_alt_name:
        team_name = team_alt_name[team_name]
    for d in data["gameWeek"]:
        for g in d["games"]:
        #print(type(g))
        #print(g)
            away_team_lower = g["awayTeam"]["commonName"]["default"].lower()
            home_team_lower = g["homeTeam"]["commonName"]["default"].lower()
            if away_team_lower == team_name or home_team_lower == team_name:
                away_team = g["awayTeam"]["commonName"]["default"]
                home_team = g["homeTeam"]["commonName"]["default"]
                if "score" in g["awayTeam"]:
                    away_score = g["awayTeam"]["score"]
                    home_score = g["homeTeam"]["score"]
                    period = g["periodDescriptor"]["number"]
                    game_state = g["gameState"]
                    game = f"{away_team} {away_score}\n{home_team} {home_score}\nPeriod: {period}"
                    print(game)
                    return game
                else:
                    game_start = g["startTimeUTC"]
                    game_start = datetime.fromisoformat(game_start.replace('Z', '+00:00'))
                    eastern_tz = pytz.timezone('US/Eastern')
                    game_start = game_start.astimezone(eastern_tz)
                    game_start = game_start.strftime("%b %d, %Y, %I:%M %p %Z")
                    future_game = f"{away_team}\n{home_team}\n{game_start}"
                    print(future_game)
                    return future_game
    #print("no such team")
    return f"no such team"
                
                #game = g

    # first_week = data["gameWeek"][0]
    # print(first_week["games"])
    # print(data["gameWeek"][0]["games"])
    # call nhl api
    # search for input from user
    #pass
def get_nhl_standings(division_name):
    alt_names = {
        "metro": "metropolitan"
    }
    division_leaderboard = []
    # division_header = f"{'TEAM'} {'GP'} {'W'} {'L'} {'OTL'} {'PTS'}"
    url = 'https://api-web.nhle.com/v1/standings/now'
    response = requests.get(url)
    data = response.json()
    time_stamp = data["standingsDateTimeUtc"]
    time_stamp = datetime.fromisoformat(time_stamp.replace("Z", "+00:00"))
    eastern_tz = pytz.timezone('US/Eastern')
    time_stamp = time_stamp.astimezone(eastern_tz)
    time_stamp = time_stamp.strftime("%b %d, %Y, %I:%M %p %Z")
    # division_header = f"{division_name} Standings\nas of: {time_stamp}\n{'TEAM':7} {'GP':4} {'W':3} {'L':2} {'OTL':3} {'PTS':3}"
    teams = data['standings']
    if division_name in alt_names:
        division_name = alt_names[division_name]
    # division_header = f"{division_name} Standings\nas of: {time_stamp}\n{'TEAM':7} {'GP':4} {'W':3} {'L':2} {'OTL':3} {'PTS':3}"
    proper_divison = None
    for d in data['standings']:
        division_lower = d['divisionName'].lower()
        if division_name == division_lower:
            if proper_divison == None:
                proper_divison = d['divisionName']
            team = d["teamAbbrev"]["default"]
            games_played = d["gamesPlayed"]
            wins = d["wins"]
            losses = d["losses"]
            ot_losses = d["otLosses"]
            points = d["points"]
            division_standing = d["divisionSequence"]
            # team_stats = f"{team} {games_played} {wins} {losses} {ot_losses} {points}"
            team_stats = f"{team:6} {games_played:3} {wins:3} {losses:3} {ot_losses:3} {points:3}"
            division_leaderboard.append(team_stats)
    division_header = f"{proper_divison} Standings\nas of: {time_stamp}\n{'TEAM':7} {'GP':4} {'W':3} {'L':2} {'OTL':3} {'PTS':3}"
    standings_division = division_header + "\n" + "\n" .join(division_leaderboard)
    print(standings_division)
    return standings_division
    #print(f"team GP W L OTL PTS")
    #for t in division_leaderboard:
    #    print(t)
    #print(division_leaderboard)
            #division_leaderboard = f"{team} {games_played} {wins} {losses} {ot_losses} {points}"
            #print(f"team GP W L OTL PTS\n{division_leaderboard}")

def get_nfl_score():
    pass

if __name__ == "__main__":
    get_nhl_standings("metro")