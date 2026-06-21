from telegram import Update, LinkPreviewOptions
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
from dotenv import load_dotenv
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from sports_data import get_nhl_score, get_nhl_standings
from database import insert_private_link, initalize_db, insert_group_link, query_shared_links
from espn_api import player_search, db_lookup, espn_scoreboard, player_stats

load_dotenv()
async def score(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    split = update.message.text.split()
    team = split[1].title()
    print(update.message.text)
    print(update.effective_user.first_name)
    await update.message.reply_text(espn_scoreboard(team))

async def standings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    split = update.message.text.split()
    user_input = split[1].lower()
    print(update.message.text)
    print(update.effective_user)
    result = get_nhl_standings(user_input)
    await update.message.reply_text(f"```\n{result}\n```", parse_mode='MarkdownV2')
    # await update.message.reply_text(get_nhl_standings(user_input))
async def score_board(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    split = update.message.text.split()
    user_input = split[1].lower()
    await update.message.reply_text(espn_scoreboard(league=user_input))

async def url_db(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is not None:
        if update.message.text and (update.message.text.startswith('https://') or update.message.text.startswith('http://')):
            url = update.message.text
            user = update.effective_user.username
            timestamp = update.message.date.strftime("%Y-%m-%d %H:%M:%S")
            if update.effective_chat.type == 'private':
                insert_private_link(None, url, user, timestamp)
            else:
                insert_group_link(None, url, user, timestamp)
            print(f"chat type: {update.effective_chat.type}")
        # await update.message.reply_text("submitted") removed annoying message

async def query_links(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    command = update.message.text.lower().split()
    if len(command) == 1:
        await update.message.reply_text("try /links me")
        return
    has_me = "me" in command
    has_random = "random" in command or "rand" in command
    links_list = []
    if has_me and has_random:
        user = update.effective_user.username
        if update.effective_chat.type == "private":
            links = query_shared_links(user=user, table_name="private_links", random=True)
        else:
            links = query_shared_links(user=user, random=True)
        if len(links) == 0:
            await update.message.reply_text("No links saved")
            return
        for l in links:
            id, url, title, user, timestamp = l
            utc = ZoneInfo('UTC')
            timestamp = datetime.fromisoformat(timestamp).replace(tzinfo=utc)
            timestamp = timestamp.astimezone(ZoneInfo('America/New_York'))
            timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S %Z")
            random_link = f"{user} random link:\n{url} |{timestamp}"
            await update.message.reply_text(random_link)
    elif has_random:
        if update.effective_chat.type == "private":
            links = query_shared_links(table_name="private_links", random=True)
        else:
            links = query_shared_links(random=True)
        if len(links) == 0:
            await update.message.reply_text("No links saved")
            return
        for l in links:
            id, url, title, user, timestamp = l
            utc = ZoneInfo('UTC')
            timestamp = datetime.fromisoformat(timestamp).replace(tzinfo=utc)
            timestamp = timestamp.astimezone(ZoneInfo('America/New_York'))
            timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S %Z")
            random_link = f"{url} |{timestamp}| {user}"
            await update.message.reply_text(random_link)
    elif has_me:
        user = update.effective_user.username
        if update.effective_chat.type == "private":
            links = query_shared_links(user=user, table_name="private_links")
        else:
            links = query_shared_links(user=user)
        if len(links) == 0:
            await update.message.reply_text("No links saved")
            return
        for l in links:
            id, url, title, user, timestamp = l
            utc = ZoneInfo('UTC')
            timestamp = datetime.fromisoformat(timestamp).replace(tzinfo=utc)
            timestamp = timestamp.astimezone(ZoneInfo('America/New_York'))
            timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S %Z")
            # timestamp = timestamp.
            link_item = f"{timestamp}\n{url}"
            links_list.append(link_item)
        links_list_len = len(links_list)
        links_header = f"{user}'s links ({links_list_len}):"
        users_links = links_header + "" "\n" + "\n" .join(links_list[:5])
        await update.message.reply_text(users_links, link_preview_options=LinkPreviewOptions(is_disabled=True))
    else:
        await update.message.reply_text("try /links rand")

async def bio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    split = update.message.text.split()
    valid_leagues = ["mlb", "nfl", "nhl"]
    league = None
    for word in split[1:]:
        if word.lower() in valid_leagues:
            league = word.lower()
            break
    player_words = [word for word in split[1:] if word.lower() not in valid_leagues]
    player = " ".join(player_words)
    player = player.title()
    print(player)
    if db_lookup(player) is not None:
        await update.message.reply_text(player_search(player))
    else:
        if league == None:
            await update.message.reply_text(f"player not in db. check spelling or specify league")
            return
        else:
            await update.message.reply_text(f"Searching {league} players... this may take a while")
            await update.message.reply_text(player_search(player, league=league))
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    split = update.message.text.split()
    player = split[1:]
    player = " ".join(player)
    player = player.title()
    if db_lookup(player) is not None:
        await update.message.reply_text(player_stats(player))
    else:
        await update.message.reply_text(f"{player} not found, try again")

app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
initalize_db()
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("sb", score_board))
app.add_handler(CommandHandler("score", score))
app.add_handler(CommandHandler("sc", score))
app.add_handler(CommandHandler("standings", standings))
app.add_handler(CommandHandler("bio", bio))
app.add_handler(CommandHandler("links", query_links))
app.add_handler(MessageHandler(filters.TEXT, url_db))
app.run_polling()
