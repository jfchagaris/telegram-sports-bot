# design
## Player ID Caching:
Each sport has over 500 pages of players in the ESPN API. Instead of making an API call per page until finding the player, the database stores the components of the URL needed to look up a specific player.
## Timezone Handling:
Timestamps are stored in UTC (as received from Telegram) and converted to Eastern Time for display. Uses Python's built-in ZoneInfo module rather than pytz to avoid an external dependency. Eastern is hardcoded since the bot serves a specific user group.
## Duplicate URL Prevention: 
The links table enforces URL uniqueness to prevent both clutter and skewed random selection. Without this constraint, a spammed or repeatedly-shared URL would appear multiple times in the database, and the /links random query would be weighted toward those duplicates rather than providing a truly random selection.
## Context-Aware Link Storage: 
Links are stored in separate tables (group_links and private_links) based on chat context. This prevents cross-contamination where users could access links from groups they're not members of via their DMs with the bot. Each context maintains its own link collection.