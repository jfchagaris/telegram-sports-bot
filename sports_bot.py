from telegram import Update, LinkPreviewOptions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from dotenv import load_dotenv
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from database import insert_private_link, initalize_db, insert_group_link, query_shared_links
from espn_api import player_search, db_lookup, espn_scoreboard, player_stats, division_standings, wildcard_standings
from leagues import LEAGUES_AND_SPORTS

load_dotenv()
async def score(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    split = update.message.text.split()
    team = split[1].title()
    print(update.message.text)
    print(update.effective_user.first_name)
    await update.message.reply_text(espn_scoreboard(team))

async def standings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    split = update.message.text.split()
    user_input = " ".join(split[1:])
    print(update.message.text)
    print(update.effective_user)
    result = division_standings(user_input)
    if isinstance(result, list):
        button_list = []
        for r in result:
            button_list.append(InlineKeyboardButton(r, callback_data=f"{r}:{user_input}"))
        await update.message.reply_text("which league?", reply_markup=InlineKeyboardMarkup([button_list]))
    else:
        await update.message.reply_text(result)

async def standings_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()
    league, division = update.callback_query.data.split(":")
    result = division_standings(division, league=league)
    await update.callback_query.edit_message_text(result)

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
    valid_leagues = LEAGUES_AND_SPORTS.keys()
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
    await update.message.reply_text(player_stats(player))

async def wildcard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    split = update.message.text.split()
    user_input = " ".join(split[1:])
    await update.message.reply_text(wildcard_standings(user_input))

app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
initalize_db()
app.add_handler(CommandHandler("wildcard", wildcard))
app.add_handler(CommandHandler("wc", wildcard))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("sb", score_board))
app.add_handler(CommandHandler("score", score))
app.add_handler(CommandHandler("sc", score))
app.add_handler(CommandHandler("standings", standings))
app.add_handler(CommandHandler("bio", bio))
app.add_handler(CommandHandler("links", query_links))
app.add_handler(MessageHandler(filters.TEXT, url_db))
app.add_handler(CallbackQueryHandler(standings_button))
app.run_polling()
