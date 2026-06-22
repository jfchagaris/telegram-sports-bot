import json
import requests

url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/standings?region=us&lang=en&enable=standings"
response = requests.get(url, headers="JSON")
data = response.json()
print(json.dumps(data, indent=2))