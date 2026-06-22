# sports-bot
A Telegram bot for live sports scores, player bios/stats, and shared link tracking. 
Running 24/7 on Oracle Cloud Free Tier.

## Features
- Live scores and standings for NFL/NHL/MLB/NBA via ESPN API
- Player search with multi-league bio + statistics  
- URL tracking and retrieval (per-user, random, filtered)
- SQLite caching of ESPN player IDs to reduce API calls

## Tech stack
- Python 3 with python-telegram-bot
- SQLite (two databases: player ID cache, link storage)
- ESPN API (multiple endpoints: scoreboard, athlete details, standings)
- async/await for Telegram event handling
- Deployed on Oracle Cloud Free Tier ARM instance

## Architecture
[bot.py] → [sports_data.py / espn_api.py] → [ESPN APIs]
                  ↓
            [database.py] → [SQLite]

## Example commands
/score lakers           - get current Lakers score
/sb nfl                 - full NFL scoreboard for the day
/standings metro        - NHL Metropolitan division standings
/bio Josh Allen         - player bio with auto-search across leagues
/stats Mike Trout       - player stats with multi-position handling
/links me               - your recent links
/links rand             - random link from history
