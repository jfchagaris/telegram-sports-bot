LEAGUES_AND_SPORTS = {
    "nfl": "football",
    "nhl": "hockey",
    "mlb": "baseball",
    "nba": "basketball"
}
# each value is a list of (league, cannonical name), more then one option means a division name is shared across leagues
DIVISION_TO_LEAGUE = {
    "nl east": [("mlb", "National League East")],
    "nl central": [("mlb", "National League Central")],
    "nl west": [("mlb", "National League West")],
    "al east": [("mlb", "American League East")],
    "al west": [("mlb", "American League West")],
    "al central": [("mlb", "American League Central")],
    "afc east": [("nfl", "AFC East")],
    "afc north": [("nfl", "AFC North")],
    "afc south": [("nfl", "AFC South")],
    "afc west": [("nfl", "AFC West")],
    "nfc east": [("nfl", "NFC East")],
    "nfc north": [("nfl", "NFC North")],
    "nfc south": [("nfl", "NFC South")],
    "nfc west": [("nfl", "NFC West")],
    "metro": [("nhl", "Metropolitan Division")],
    "metropolitan": [("nhl", "Metropolitan Division")],
    "atlantic": [("nhl", "Atlantic Division"),
                 ("nba", "Atlantic")],
    "central": [("nhl", "Central Division"),
                ("nba", "Central")],
    "pacific": [("nhl", "Pacific Division"),
                ("nba", "Pacific")],
    "southeast": [("nba", "Southeast")],
    "northwest": [("nba", "Northwest")],
    "southwest": [("nba", "Southwest")]

}

CONFERENCE_AND_LEAGUES = {
    "nl": ("mlb", "National League"),
    "al": ("mlb", "American League"),
}

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