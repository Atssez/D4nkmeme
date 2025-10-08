import json
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
import random
import time
import time
import math
from datetime import timezone
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputFile
from telegram.ext import ContextTypes
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler
import os
import re
BEG_SUCCESS_IMAGE = "https://pbs.twimg.com/media/GPsaG2vWQAAvUi_?format=png&name=small"
from utils import (
    load_balances,
    save_balances,
    normalize,
    add_to_inventory,
    remove_from_inventory,
    get_player_coins,
    change_player_coins,
add_xp,
xp_required_for_level
)
OWNER_USERNAME = "atssez"
DAILY_COOLDOWN = 86400  # seconds (24h)
DAILY_BASE_MIN = 500
DAILY_BASE_MAX = 2000
DAILY_STREAK_BONUS_PER_DAY = 100  # extra coins per streak day
DAILY_MAX_STREAK = 30
WIN_GIFS = [
    "https://media.tenor.com/71K1Mm4YxX4AAAAM/money-make.gif",
    "https://i.pinimg.com/originals/51/18/27/511827714088e54af308b7a13a3a9f08.gif",
    "https://media.tenor.com/OMmVm87NqZgAAAAM/wine-wine-time.gif"
]

LOSE_GIFS = [
    "https://media.tenor.com/USVKtXwWCfsAAAAM/why-cry-why-pepe-why.gif",
    "https://i.pinimg.com/originals/24/79/f7/2479f765e4553a1def42231063134deb.gif",
    "https://media.tenor.com/dd6OGwgkkJoAAAAM/pepe.gif"
]
CRIME_FAIL_GIFS = [
    "https://media.tenor.com/xD5L-EvTKqIAAAAM/crying.gif",
    "https://media.tenor.com/HZClb9KQ7o0AAAAM/pepe-rain-pepe-the-frog.gif",
    "https://media.tenor.com/hMn2g7TfBpcAAAAM/pepe-sad-pepe-cry.gif",
]

CRIME_DEATH_IMAGE = "https://media-cldnry.s-nbcnews.com/image/upload/t_fit-760w,f_auto,q_auto:best/newscms/2017_19/1991976/170508-pepe-frog-mn-1015-1991976.jpg"

CRIME_SUCCESS_GIFS = [
    "https://i.pinimg.com/originals/51/18/27/511827714088e54af308b7a13a3a9f08.gif",
    "https://media.tenor.com/up3wjjJPq2IAAAAM/dankies-pepe.gif",
    "https://gifdb.com/images/high/pepe-frog-meme-happy-sleeping-good-night-fohw5p2ow8h9u6gq.gif",
    "https://media.tenor.com/zaUVBBOcX5oAAAAj/peepo-pepe.gif",
]

CRIME_CRIT_SUCCESS_GIFS = [
    "https://i.pinimg.com/originals/f1/19/44/f11944b076afbcf4a5984574032b5c21.gif",
]
LEVEL_TITLES = {
    1: "Newbie",
    5: "Re-poster",
    10: "Memer",
    15: "Original Memer",
    20: "Total Memer",
    25: "Dank Memer",
    50: "Good Meme",
    69: "69 nice",
    100: "Kek Lord",
    300: "Amazing Cute Memer",
    400: "Wow Memer",
    500: "God of Memes",
    700: "Literally Dank Memer",
    1000: "God",
    1111: "one one one"
}
CRIME_EMOJI_MAP = {
    "arson": "🔥",
    "bank robbing": "🏦",
    "bank robbing": "🏦",
    "jay walking": "🚶",
    "driving under the influence (dui)": "🚗",
    "fraud": "🕵️",
    "grand theft auto": "🚙",
    "breaking and entering": "🔓",
    "cyber bullying": "📱",
    "drug distribution": "💊",
    "hacking": "💻",
    "highway robbery": "🛣️",
    "identity theft": "🆔",
    "idle hands": "😴",
    "littering": "🗑️",
    "murder": "🔪",
    "pineapple on pizza": "🍍",
    "piracy": "🏴‍☠️",
    "poisoning": "☠️",
    "shoplifting": "🛍️",
    "stab grandma": "🪙",
    "stealing from drug lords": "🌱",
    "tax evasion": "💳",
    "treason": "⚖️",
    "trespassing": "🚫",
    "vandalism": "🖌️",
    "paying for twitter blue": "🔵"
}
FAIL_IMAGE_PATH = r"C:\Users\Administrator\Desktop\TelegramBot\pepe-lying-on-floor-crying-over-whatever-you-want-v0-s8x71lwq6vpd1.png"
# Slots config
SLOT_SYMBOLS = ["🍒", "🍋", "🔔", "⭐", "7️⃣", "💎"]
# payout multipliers when 3 of a kind
SLOT_PAYOUTS = {
    "🍒": 8,
    "🍋": 6,
    "🔔": 10,
    "⭐": 12,
    "7️⃣": 25,
    "💎": 40
}
SLOT_MAX_BET = 50_000  # adjust as you like
SLOT_COOLDOWN_SECONDS = 3  # optional per-user minimal gap (seconds)

SLOT_SPIN_GIFS = [
    "https://media.tenor.com/71K1Mm4YxX4AAAAM/money-make.gif",
]
SLOT_WIN_GIFS = [
    "https://i.pinimg.com/originals/51/18/27/511827714088e54af308b7a13a3a9f08.gif",
    "https://media.tenor.com/up3wjjJPq2IAAAAM/dankies-pepe.gif",
    "https://gifdb.com/images/high/pepe-frog-meme-happy-sleeping-good-night-fohw5p2ow8h9u6gq.gif",
    "https://media.tenor.com/zaUVBBOcX5oAAAAj/peepo-pepe.gif",
]
SLOT_LOSE_GIFS = [
    "https://media.tenor.com/xD5L-EvTKqIAAAAM/crying.gif",
    "https://media.tenor.com/HZClb9KQ7o0AAAAM/pepe-rain-pepe-the-frog.gif",
    "https://media.tenor.com/hMn2g7TfBpcAAAAM/pepe-sad-pepe-cry.gif",
]
# --- Message collector for heist minigames (use a Future per waiting player) ---
import asyncio

def _ensure_heist_waits(chat_data):
    if "heist_waits" not in chat_data:
        chat_data["heist_waits"] = {}  # uid_str -> Future
    return chat_data["heist_waits"]

async def await_player_response(context, chat_id: int, player_uid: str, timeout: int = 20):
    """
    Wait for a message from player_uid in chat_id for up to timeout seconds.
    Returns the telegram.Message object or None on timeout.
    """
    waits = _ensure_heist_waits(context.chat_data)
    # don't overwrite an existing future for this uid
    if player_uid in waits and not waits[player_uid].done():
        return None
    loop = asyncio.get_running_loop()
    fut = loop.create_future()
    waits[player_uid] = fut
    try:
        msg = await asyncio.wait_for(fut, timeout=timeout)
        return msg
    except asyncio.TimeoutError:
        return None
    finally:
        # cleanup
        waits.pop(player_uid, None)
# This function should be registered as a MessageHandler that runs early (non-command text)
async def heist_message_collector(update, context):
    if not update.message or not update.effective_chat:
        return
    chat_id = str(update.effective_chat.id)
    user_id = str(update.effective_user.id)
    text = (update.message.text or "<no-text>")
    # debug log
    print(f"[HEIST-COLLECTOR] chat={chat_id} user={user_id} text={text}")
    try:
        with open("heist_debug.log", "a", encoding="utf-8") as f:
            f.write(f"{datetime.utcnow().isoformat()}Z\tchat={chat_id}\tuser={user_id}\ttext={text}\n")
    except Exception:
        pass

    waits = (context.chat_data.get("heist_waits") or {})
    fut = waits.get(user_id)
    if fut and not fut.done():
        try:
            fut.set_result(update.message)
            print(f"[HEIST-COLLECTOR] delivered to future for user={user_id}")
        except Exception as e:
            print(f"[HEIST-COLLECTOR] set_result failed: {e}")

# per-user last slot spin time (in-memory)
_last_slot_ts = {}
GAMBLE_CHOICE, GAMBLE_AMOUNT, GAMBLE_ROULETTE, GAMBLE_BLACKJACK, GAMBLE_DICE = range(5)
def cooldown_get(balances, uid, key):
    user = balances.setdefault(uid, {})
    cd = user.setdefault("cooldowns", {})
    return cd.get(key, 0)

def cooldown_set(balances, uid, key, ts):
    user = balances.setdefault(uid, {})
    cd = user.setdefault("cooldowns", {})
    cd[key] = int(ts)

def load_bot_data(app):
    with open("data/shop_items.json", "r", encoding="utf-8") as f:
        app.bot_data["shop_items"] = json.load(f)
    with open("data/fish_baits.json", "r", encoding="utf-8") as f:
        app.bot_data["fish_baits"] = json.load(f)
    with open("data/fishing_tools.json", "r", encoding="utf-8") as f:
        app.bot_data["tools"] = json.load(f)
DIG_REWARDS = [
    ("ammo",      5, r"C:\Users\Administrator\Desktop\TelegramBot\power-up.json"),
    ("banknote",  5, r"C:\Users\Administrator\Desktop\TelegramBot\power-up.json"),
    ("candycorn", 1, r"C:\Users\Administrator\Desktop\TelegramBot\power-up.json"),
    ("lifesaver", 1, r"C:\Users\Administrator\Desktop\TelegramBot\power-up.json"),
    ("ant",      15, r"C:\Users\Administrator\Desktop\TelegramBot\sellable.json"),
    ("bean",     10, r"C:\Users\Administrator\Desktop\TelegramBot\sellable.json"),
    ("diamond",   3, r"C:\Users\Administrator\Desktop\TelegramBot\sellable.json"),
    ("fossil",   10, r"C:\Users\Administrator\Desktop\TelegramBot\sellable.json"),
    ("garbage",  10, r"C:\Users\Administrator\Desktop\TelegramBot\sellable.json"),
    ("fail",     40, None)
]

HUNT_REWARDS = [
    ("fail", 40),
    ("boar", 10),
    ("deer", 10),
    ("duck", 25),
    ("tree", 1),
    ("potato", 5),
    ("rabbit", 4),
    ("skunk", 5),
]
# Define your fish odds per location
FISH_ODDS = {
    "Abstraction Bay": {
        "Blue Tang":  0.05,
        "Boxfish":     0.10,
        "Shrimp":      0.10,
        "Jellyfish":   0.15,
        "Lionfish":    0.05,
        "Starfish":    0.15,
        "fail":        0.40,
    },
    "Camp Guillermo": {
        "Bass":         0.20,
        "Bluegill":     0.05,
        "Bullfrog":     0.05,
        "Crappie":      0.10,
        "White Perch":  0.10,
        "Yellow Perch": 0.10,
        "fail":         0.40,
    },
    "Vertigo Beach": {
        "Butterfly Fish": 0.05,
        "Jellyfish":      0.10,
        "Ocean Sunfish":  0.05,
        "Shrimp":         0.15,
        "Starfish":       0.15,
        "Boxfish":        0.10,
        "fail":           0.40,
    }
}

WATER_EMOJI = {
    "Freshwater": "💧",
    "Saltwater":  "🌊"
}
GAMBLE_DAILY_WIN_LIMIT = 10
GAMBLE_DAILY_TAX_RATE = 0.20  # 20%
FISH_EMOJI = "🐠"
def _utc_date_str(ts=None):
    return datetime.utcfromtimestamp(ts or time.time()).strftime("%Y-%m-%d")
def _ensure_gamble_daily(balances, uid):
    user = balances.setdefault(uid, {})
    g = user.setdefault("gambling_daily", {"date": _utc_date_str(), "wins": 0, "winnings": 0, "banned": False})
    if g.get("date") != _utc_date_str():
        g.update({"date": _utc_date_str(), "wins": 0, "winnings": 0, "banned": False})
    return g

def is_gamble_banned(balances, uid):
    g = _ensure_gamble_daily(balances, uid)
    return bool(g.get("banned", False))
def record_gamble_win(balances, uid, win_amount):
    g = _ensure_gamble_daily(balances, uid)
    g["wins"] = int(g.get("wins", 0)) + 1
    g["winnings"] = int(g.get("winnings", 0)) + int(win_amount)
    banned_now = False
    tax = 0
    if g["wins"] >= GAMBLE_DAILY_WIN_LIMIT:
        g["banned"] = True
        banned_now = True
        tax = int(g["winnings"] * GAMBLE_DAILY_TAX_RATE)
        balances.setdefault(uid, {}).setdefault("coin", 0)
        balances[uid]["coin"] = max(0, balances[uid]["coin"] - tax)
    return banned_now, tax
def get_title_for_level(level: int) -> str:
    """Return the highest title the user qualifies for at given level."""
    title = None
    best_thresh = -1
    for thresh, t in LEVEL_TITLES.items():
        if level >= thresh and thresh > best_thresh:
            best_thresh = thresh
            title = t
    return title or "Unranked"
def normalize(text):
    import re
    return re.sub(r'\W+', '', text).lower()

async def handle_fish_location_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = []
    fish_locations = context.bot_data["fish_locations"]

    for i, loc in enumerate(fish_locations):
        emoji = WATER_EMOJI.get(loc["type"], "🌊")
        keyboard.append([
            InlineKeyboardButton(f"{emoji} {loc['name']}", callback_data=f"fish_confirm_{i}")
        ])

    await query.edit_message_text(
        "🌍 Choose your fishing location:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
# ─────────── DIG HANDLER ─────────────────────────────
async def handle_hunt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)

    # 1. Load balances once
    balances = load_balances()
    if user_id not in balances:
        return await query.edit_message_text("Use /start to begin!")

    inv = balances[user_id].setdefault("inventory", {})

    # 2. Ensure player has a Hunting Rifle
    if inv.get("huntingrifle", 0) < 1:
        return await query.edit_message_text("🚫 You need a Hunting Rifle to hunt.")

    # 3. Roll for reward
    hunt_protection = context.user_data.get("hunt_protection", 0)

    hunt_protection = context.user_data.get("hunt_protection", 0)

    if time.time() < hunt_protection:
        non_fail_rewards = [r for r in HUNT_REWARDS if r[0] != "fail"]
        picked = random.choices([r[0] for r in non_fail_rewards], weights=[r[1] for r in non_fail_rewards])[0]
    else:
        roll = random.uniform(0, 100)
        cum = 0
        picked = None
        for key, pct in HUNT_REWARDS:
            cum += pct
            if roll <= cum:
                picked = key
                break

    # 4. Handle fail case
    if not picked or picked == "fail":
        fail_lines = [
            "🔫 You aimed... but only your pride took a hit.",
            "🌲 The forest laughed at you. No game today.",
            "🦝 You scared a raccoon. It called its friends.",
            "💨 You shot... and caught a breeze.",
            "📜 You unearthed a hunting permit. Too late now.",
            "🦉 An owl hooted. Even it judged your aim.",
        ]
        balances[user_id]["status"] = None
        save_balances(balances)
        await query.message.reply_photo(
            photo=FAIL_IMAGE_PATH,
            caption=random.choice(fail_lines)
        )
        return

    # 5. Lookup display name in sellable.json
    try:
        with open(r"C:\Users\Administrator\Desktop\TelegramBot\sellable.json", "r", encoding="utf-8") as f:
            all_items = json.load(f)
        item = next(i for i in all_items if normalize(i["itemKey"]) == normalize(picked))
    except StopIteration:
        print(f"❌ No match found for picked itemKey: {picked}")
        return await query.edit_message_text("⚠️ Couldn’t find hunt item in sellables.")

    # 6. Add to inventory *on this balances dict*, then save once
    inv[picked] = inv.get(picked, 0) + 1
    balances[user_id]["status"] = None
    save_balances(balances)

    # 7. Debug print (optional)
    print("✅ Inventory after hunt:", balances[user_id]["inventory"])

    # 8. Send success message
    return await query.edit_message_text(
        f"🔫 You hunted a *{item['name']}*!",
        parse_mode="Markdown"
    )

async def handle_dig(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)

    balances = load_balances()
    if user_id not in balances:
        return await query.edit_message_text("Use /start to begin!")
    inv = balances[user_id].setdefault("inventory", {})

    # require shovel
    if inv.get("shovel", 0) < 1:
        return await query.edit_message_text("🚫 You need a Shovel to dig.")

    # roll reward
    roll = random.uniform(0, 100)
    cum = 0
    picked = None
    for key, pct, path in DIG_REWARDS:
        cum += pct
        if roll <= cum:
            picked = (key, path)
            break

    # fail case
    if not picked or picked[0] == "fail":
        fail_lines = [
            "⛏️ You dug… and found your hopes and dreams. They're still buried.",
            "🪨 You hit solid rock. It whispered 'L' before crumbling.",
            "🦗 You found a cricket. It judged you silently.",
            "📜 You unearthed a scroll. It says: 'Try again, peasant.'",
            "💨 You dug up air. Premium oxygen. Congrats.",
            "🧠 You found a brain cell. It left immediately.",
            "🕳️ You fell into the hole you dug. Classic.",
            "🧻 You found toilet paper. Used. Ew.",
            "🪦 You found a grave. It was labeled 'Your luck'.",
            "🧲 You found a magnet. It repelled success.",
            "🕳️ You dug... and found nothing but regret."
        ]
        fail_msg = random.choice(fail_lines)
        try:
            with open(FAIL_IMAGE_PATH, "rb") as img:
                await query.message.reply_photo(photo=InputFile(img), caption=fail_msg)
        except Exception as e:
            print("❌ Failed to send fail image:", e)
            await query.edit_message_text(fail_msg)
        return

    key, path = picked

    # load that file, find the item entry
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        item = next(i for i in data if i.get("itemKey") == key)
    except Exception as e:
        print("❌ digging-load error:", e)
        return await query.edit_message_text("⚠️ Couldn’t load item data.")

    # add to inventory
    add_to_inventory(user_id, key)

    # report success
    return await query.edit_message_text(f"⛏️ You dug up a {item['name']}!")
async def show_fishing_location(query, context, index):
    fish_locations = context.bot_data["fish_locations"]
    index %= len(fish_locations)
    context.user_data["last_index"] = index

    loc = fish_locations[index]
    name = loc["name"]
    water_type = loc.get("type", "Unknown")
    image_path = loc.get("link", "data/fallback.png")
    creatures = loc.get("prize", [])

    creature_lines = [f"- {c['name']} {FISH_EMOJI}" for c in creatures]
    creature_text = "\n".join(creature_lines) if creature_lines else "None"

    caption = (
        f"📍 Location: {name}\n"
        f"🌊 Type: {water_type}\n\n"
        f"🐠 Creatures:\n{creature_text}"
    )

    keyboard = [
        [
            InlineKeyboardButton("⬅️ Previous", callback_data=f"fish_prev_{index}"),
            InlineKeyboardButton("✅ Confirm",  callback_data=f"fish_confirm_{index}"),
            InlineKeyboardButton("➡️ Next",    callback_data=f"fish_next_{index}")
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    try:
        if not os.path.exists(image_path) or os.path.getsize(image_path) == 0:
            raise FileNotFoundError(f"Location image missing or empty: {image_path}")

        with open(image_path, "rb") as img:
            if query.message.photo:
                await query.edit_message_media(
                    InputMediaPhoto(img, caption=caption),
                    reply_markup=markup
                )
            else:
                await context.bot.send_photo(
                    chat_id=query.message.chat.id,
                    photo=img,
                    caption=caption,
                    reply_markup=markup
                )
                await query.message.delete()

    except Exception as e:
        print(f"❌ show_fishing_location error: {e}")
        try:
            await query.edit_message_text(caption, reply_markup=markup)
        except:
            await context.bot.send_message(
                chat_id=query.message.chat.id,
                text=caption,
                reply_markup=markup
            )

async def handle_cast_fish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, _, idx = query.data.split("_")
    index = int(idx)
    fish_locations = context.bot_data["fish_locations"]
    loc_name = fish_locations[index]["name"]
    odds = FISH_ODDS[loc_name]

    choice = random.random()
    cumulative = 0.0
    caught = "fail"
    for fish_name, prob in odds.items():
        cumulative += prob
        if choice <= cumulative:
            caught = fish_name
            break

    context.user_data["last_fish"] = normalize(caught)
    context.user_data["last_index"] = index

    if caught != "fail":
        user_id = str(query.from_user.id)
        add_to_inventory(user_id, normalize(caught))

    if caught == "fail":
        fail_lines = [
            "🐟 You cast your line… and reeled in nothing.",
            "🌫 The waters stirred… but no creature dared emerge.",
            "🎣 Your bait was so bad, even the fish swam away laughing.",
            "🪱 You dropped your bait, and a crab stole it.",
            "🐠 A fish looked at your hook and said 'nah'.",
            "🧂 You caught a wave. It splashed you and left.",
            "🐡 You almost caught something… but it caught you instead.",
            "🪸 You reeled in a soggy boot. Stylish, but not edible.",
            "🐬 A dolphin swam by and mocked your technique.",
            "🧃 You caught a juice box. It was empty."
        ]
        await query.edit_message_caption(random.choice(fail_lines))
        return

    text = f"🐠 You caught a {caught} 🐟!"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Continue ▶️", callback_data="end_fishing")]
    ])

    await query.edit_message_caption(text, reply_markup=kb)
async def handle_end_fishing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.message.delete()
    except:
        await query.edit_message_caption("✅ Fishing session ended.")

async def work_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎣 Fish", callback_data="work_fish")],
        [InlineKeyboardButton("⛏️ Dig",  callback_data="work_dig")],
        [InlineKeyboardButton("🏹 Hunt", callback_data="work_hunt")]
    ])
    await update.message.reply_text("Choose your work:", reply_markup=keyboard)

async def handle_work_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    balances = load_balances()
    if user_id not in balances:
        return await query.edit_message_text("Use /start to begin!")
    inv = balances[user_id].get("inventory", {})

    if query.data == "work_dig":
        return await handle_dig(update, context)
    print("Inventory keys:", inv.keys())
    if "Fishing Pole" in inv:
        inv["fishingpole"] = inv.get("fishingpole", 0) + inv["Fishing Pole"]
        del inv["Fishing Pole"]
    if query.data == "work_fish":
        # require fishing pole
        if inv.get(normalize("fishing pole"), 0) < 1:
            return await query.edit_message_text("🚫 You need a Fishing Pole to fish.")
        return await show_fishing_location(query, context, 0)

    if query.data == "work_hunt":
        balances[user_id]["status"] = "hunt"
        save_balances(balances)
        return await handle_hunt(update, context)


async def beg_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Beg for coins. Sends one reply (photo+caption or text)."""
    BEG_SUCCESS_IMAGE = "https://pbs.twimg.com/media/GPsaG2vWQAAvUi_?format=png&name=small"

    user_id = str(update.effective_user.id)
    balances = load_balances()
    if user_id not in balances:
        return await update.message.reply_text("Use /start to begin!")

    # XP
    balances[user_id]["xp"] = balances[user_id].get("xp", 0) + 3

    # Load messages
    with open("data/beg_people.json", "r", encoding="utf-8") as f:
        people = json.load(f)
    with open("data/beg_success.json", "r", encoding="utf-8") as f:
        success_msgs = json.load(f)
    with open("data/beg_failure.json", "r", encoding="utf-8") as f:
        failure_msgs = json.load(f)

    person = random.choice(people)
    roll = random.random()
    inventory = balances[user_id].setdefault("inventory", {})
    coin = balances[user_id].get("coin", 0)
    beg_boost = context.user_data.get("beg_boost", {})
    xp_boost = context.user_data.get("xp_boost", {})

    beg_multiplier = 1.0
    xp_multiplier = 1.0

    if beg_boost and time.time() < beg_boost.get("expires", 0):
        beg_multiplier = beg_boost.get("multiplier", 1.0)

    if xp_boost and time.time() < xp_boost.get("expires", 0):
        xp_multiplier = xp_boost.get("multiplier", 1.0)

    balances[user_id]["xp"] += int(3 * xp_multiplier)

    # Prepare defaults
    msg = None
    sent = False

    # Rare huge win
    if roll <= 0.001:
        amount = random.randint(1300, 1560)
        item = random.choice(["bank_note", "pizza_slice", "rare_pepe", "alcohol"])
        balances[user_id]["coin"] = coin + amount
        inventory[item] = inventory.get(item, 0) + 1
        save_balances(balances)
        msg = (
            f"{person} saw you begging and said "
            f"{random.choice(success_msgs).format(amount=amount)}\n"
            f"🎁 Bonus item: {item.replace('_', ' ').title()}"
        )
        try:
            await update.message.reply_photo(photo=BEG_SUCCESS_IMAGE, caption=msg)
            sent = True
        except Exception:
            await update.message.reply_text(msg)
            sent = True

    # Major success
    elif roll <= 0.05:
        amount = int(random.randint(780, 1040) * beg_multiplier)
        balances[user_id]["coin"] = coin + amount
        save_balances(balances)
        msg = f"{person} saw you begging and said {random.choice(success_msgs).format(amount=amount)}"
        try:
            await update.message.reply_photo(photo=BEG_SUCCESS_IMAGE, caption=msg)
            sent = True
        except Exception:
            await update.message.reply_text(msg)
            sent = True

    # Moderate success
    elif roll <= 0.17:
        amount = int(random.randint(260, 780) * beg_multiplier)
        balances[user_id]["coin"] = coin + amount
        save_balances(balances)
        msg = f"{person} saw you begging and said {random.choice(success_msgs).format(amount=amount)}"
        try:
            await update.message.reply_photo(photo=BEG_SUCCESS_IMAGE, caption=msg)
            sent = True
        except Exception:
            await update.message.reply_text(msg)
            sent = True

    # Small success
    elif roll <= 0.55:
        amount = int(random.randint(65, 260) * beg_multiplier)
        balances[user_id]["coin"] = coin + amount
        save_balances(balances)
        msg = f"{person} saw you begging and said {random.choice(success_msgs).format(amount=amount)}"
        try:
            await update.message.reply_photo(photo=BEG_SUCCESS_IMAGE, caption=msg)
            sent = True
        except Exception:
            await update.message.reply_text(msg)
            sent = True

    # Fail
    else:
        msg = f"{person} saw you begging and said {random.choice(failure_msgs)}"
        try:
            with open(FAIL_IMAGE_PATH, "rb") as img:
                await update.message.reply_photo(photo=InputFile(img), caption=msg)
                sent = True
        except Exception:
            await update.message.reply_text(msg)
            sent = True

    # Safety final check (shouldn't be needed but ensures single reply)
    if not sent and msg is not None:
        await update.message.reply_text(msg)

async def sell_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    balances = load_balances()
    if user_id not in balances:
        return await update.message.reply_text("Use /start to begin!")

    inventory = balances[user_id].get("inventory", {})
    args = context.args
    if not args:
        return await update.message.reply_text("Usage: /sell <item name> [quantity]")

    item_name = normalize(args[0])
    with open(r"C:\Users\Administrator\Desktop\TelegramBot\sellable.json", "r", encoding="utf-8") as f:
        sellables = json.load(f)
    with open(r"C:\Users\Administrator\Desktop\TelegramBot\power-up.json", "r", encoding="utf-8") as f:
        powerups = json.load(f)

    dig_items = sellables + powerups
    dig_lookup = {normalize(i["name"]): i for i in dig_items}

    quantity = int(args[1]) if len(args) > 1 and args[1].isdigit() else 1
    if quantity < 1:
        return await update.message.reply_text("❌ Quantity must be at least 1.")

    fish_keys = context.bot_data.get("fish_keys", set())
    fish_values = context.bot_data.get("fish_values", {})
    shop_items = context.bot_data.get("shop_items", [])
    item_prices = {normalize(i["name"]): i.get("value", 0) for i in shop_items}

    # Fish sale flow
    if item_name in fish_keys:
        fish_folder = "data/fish_fishes"
        fish_file = os.path.join(
            fish_folder,
            f"{item_name.title().replace(' ', '_')}.json"
        )
        try:
            with open(fish_file, "r", encoding="utf-8") as f:
                fish_data = json.load(f)
        except:
            return await update.message.reply_text("❌ Could not load fish data.")

        if inventory.get(item_name, 0) < quantity:
            return await update.message.reply_text("❌ You don't have enough of that fish.")

        price = fish_data.get("price", 0)
        total = price * quantity
        caption = (
            f"🐟 *{fish_data['name']}*\n"
            f"🎯 Rarity: {fish_data.get('rarity', 'Unknown')}\n"
            f"📝 Note: {fish_data.get('note', '—')}\n"
            f"📖 Description: {fish_data.get('description', '—')}\n"
            f"💰 Price: {price} ⏣\n"
            f"💵 Total: {total} ⏣"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_sell:{item_name}:{quantity}")],
            [InlineKeyboardButton("❌ Cancel",  callback_data="cancel_sell")]
        ])
        try:
            with open(fish_data["link"], "rb") as img:
                await update.message.reply_photo(photo=InputFile(img),
                                                 caption=caption,
                                                 reply_markup=keyboard,
                                                 parse_mode="Markdown")
        except:
            await update.message.reply_text(caption,
                                            reply_markup=keyboard,
                                            parse_mode="Markdown")
        return

    # Regular item sale
    if item_name in item_prices:
        if inventory.get(item_name, 0) < quantity:
            return await update.message.reply_text("❌ You don't have enough of that item.")

        price = item_prices[item_name]
        total = int(price * 0.8) * quantity
        caption = (
            f"🧰 *{item_name.title()}*\n"
            f"💰 Shop Price: {price} ⏣\n"
            f"💵 Sell Price: {int(price * 0.8)} ⏣\n"
            f"📦 Quantity: {quantity}\n"
            f"💵 Total: {total} ⏣"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_sell:{item_name}:{quantity}")],
            [InlineKeyboardButton("❌ Cancel",  callback_data="cancel_sell")]
        ])
        await update.message.reply_text(caption,
                                        reply_markup=keyboard,
                                        parse_mode="Markdown")
        return
    # ⛏️ Dig item sale
    if item_name in dig_lookup:
        item = dig_lookup[item_name]
        if inventory.get(item_name, 0) < quantity:
            return await update.message.reply_text("❌ You don't have enough of that item.")

        price = item.get("value", 0)
        total = price * quantity
        caption = (
            f"⛏️ *{item['name']}*\n"
            f"🧬 Rarity: {item.get('rarity', 'Unknown')}\n"
            f"📜 Description: {item.get('description', '—')}\n"
            f"💰 Price: {price} ⏣\n"
            f"💵 Total: {total} ⏣"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_sell:{item_name}:{quantity}")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_sell")]
        ])
        image_path = item.get("imageURL")
        if image_path and os.path.isfile(image_path):
            try:
                with open(image_path, "rb") as img_file:
                    await update.message.reply_photo(
                        photo=InputFile(img_file),
                        caption=caption,
                        reply_markup=keyboard,
                        parse_mode="Markdown"
                    )
                return  # ✅ Prevent double sending
            except Exception as e:
                print(f"❌ Error sending image for {item_name}: {e}")

        # fallback if image fails or doesn't exist
        await update.message.reply_text(caption, reply_markup=keyboard, parse_mode="Markdown")
        return


async def confirm_sell_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    balances = load_balances()
    inventory = balances[user_id].get("inventory", {})

    _, item_name, quantity = query.data.split(":")
    item_name = normalize(item_name)
    with open(r"C:\Users\Administrator\Desktop\TelegramBot\sellable.json", "r", encoding="utf-8") as f:
        sellables = json.load(f)
    with open(r"C:\Users\Administrator\Desktop\TelegramBot\power-up.json", "r", encoding="utf-8") as f:
        powerups = json.load(f)

    dig_items = sellables + powerups
    dig_lookup = {normalize(i["name"]): i for i in dig_items}

    quantity = int(quantity)

    fish_keys = context.bot_data.get("fish_keys", set())
    fish_values = context.bot_data.get("fish_values", {})
    shop_items = context.bot_data.get("shop_items", [])
    item_prices = {normalize(i["name"]): i.get("value", 0) for i in shop_items}

    if inventory.get(item_name, 0) < quantity:
        return await query.edit_message_caption("❌ You don't have enough of that item.")

    if item_name in fish_keys:
        price = fish_values.get(item_name, 0)
    elif item_name in item_prices:
        price = int(item_prices.get(item_name, 0) * 0.8)
    elif item_name in dig_lookup:
        price = dig_lookup[item_name].get("value", 0)
    else:
        price = 0

    inventory[item_name] -= quantity
    balances[user_id]["coin"] += price * quantity
    save_balances(balances)
    await query.edit_message_caption(f"✅ Sold {quantity}x {item_name.title()} for {price * quantity} ⏣.")

async def cancel_sell_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    try:
        await update.callback_query.edit_message_caption("❌ Sale cancelled.")
    except:
        await update.callback_query.edit_message_text("❌ Sale cancelled.")


async def handle_fish_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # ← Navigate between locations
    if data.startswith("fish_next_"):
        index = int(data.split("_")[2]) + 1
        return await show_fishing_location(query, context, index)

    if data.startswith("fish_prev_"):
        index = int(data.split("_")[2]) - 1
        return await show_fishing_location(query, context, index)

    # ← Confirm spot, then prompt to cast
    if data.startswith("fish_confirm_"):
        index = int(data.split("_")[2])
        cast_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Cast Line 🎣", callback_data=f"cast_fish_{index}")]
        ])
        return await query.edit_message_caption(
            "🔄 Ready to cast your line?",
            reply_markup=cast_kb
        )
    if query.data == "end_fishing":
        return await handle_end_fishing(update, context)
async def gamble_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    balances = load_balances()
    # ensure user record exists
    balances.setdefault(user_id, {})
    g = balances[user_id].setdefault(
        "gambling_daily",
        {"date": datetime.utcfromtimestamp(time.time()).strftime("%Y-%m-%d"), "wins": 0, "winnings": 0, "banned": False}
    )
    # reset daily bucket if date changed
    today = datetime.utcfromtimestamp(time.time()).strftime("%Y-%m-%d")
    if g.get("date") != today:
        g.update({"date": today, "wins": 0, "winnings": 0, "banned": False})
        save_balances(balances)

    if g.get("banned", False):
        # user is banned from casino for the rest of the UTC day
        await update.message.reply_text(
            "🚫 Casino ban: you have won too much today and are banned from the casino. Come back tomorrow."
        )
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton("🎰 Roulette", callback_data="gamble_roulette")],
        [InlineKeyboardButton("🃏 Blackjack", callback_data="gamble_blackjack")],
        [InlineKeyboardButton("🎲 Dice", callback_data="gamble_dice")],
        [InlineKeyboardButton("🎰 Slots", callback_data="gamble_slots")]
    ]
    await update.message.reply_text("Choose your game:", reply_markup=InlineKeyboardMarkup(keyboard))
    return GAMBLE_CHOICE

async def handle_gamble_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # replace or augment your existing handle_gamble_choice so it includes Slots
    query = update.callback_query
    await query.answer()
    game_type = query.data.split("_")[1]
    context.user_data["gamble_game"] = game_type

    # If this is the existing function you had, keep its rest; but ensure "slots" is a game_type option
    # before: await query.edit_message_text(...)
    await query.edit_message_text(
        "💰 How much do you want to gamble?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel", callback_data="gamble_cancel")]
        ])
    )

    # store the prompt message so we can remove it when the user replies with the amount
    context.user_data["gamble_prompt_message"] = (query.message.chat.id, query.message.message_id)

    return GAMBLE_AMOUNT


async def handle_gamble_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    balances = load_balances()
    coin = balances.get(user_id, {}).get("coin", 0)

    try:
        amount = int(update.message.text.strip())
        if amount <= 0:
            raise ValueError()
    except:
        await update.message.reply_text("❌ Please enter a valid number.")
        return GAMBLE_AMOUNT

    if coin < amount:
        await update.message.reply_text("🚫 You don't have enough coins.")
        return ConversationHandler.END

    context.user_data["gamble_amount"] = amount
    # remove the original "How much do you want to gamble?" prompt to keep chat clean
    prompt = context.user_data.pop("gamble_prompt_message", None)
    if prompt:
        try:
            chat_id, msg_id = prompt
            await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except Exception:
            # ignore errors (message may already be deleted or expired)
            pass

    game = context.user_data["gamble_game"]


    if game == "roulette":
        keyboard = [
            [InlineKeyboardButton("🔴 Red", callback_data="roulette_color_red"),
             InlineKeyboardButton("⚫ Black", callback_data="roulette_color_black")],
            [InlineKeyboardButton("Pick Number", callback_data="roulette_number")],
            [InlineKeyboardButton("❌ Cancel", callback_data="gamble_cancel")]
        ]
        await update.message.reply_text("🎰 Choose your bet:", reply_markup=InlineKeyboardMarkup(keyboard))
        return GAMBLE_ROULETTE
    elif game == "slots" or game == "gamble_slots" or game == "slots_game":
        keyboard = [
            [InlineKeyboardButton("🎰 Spin", callback_data="slots_spin")],
            [InlineKeyboardButton("❌ Cancel", callback_data="gamble_cancel")]
        ]
        await update.message.reply_text("🎰 Press Spin to play Slots:", reply_markup=InlineKeyboardMarkup(keyboard))
        return GAMBLE_DICE  # reuse GAMBLE_DICE or a new appropriate state; handlers below listen for pattern "^slots_"

    elif game == "blackjack":
        deck = [f"{rank}{suit}" for rank in ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
                for suit in ['♠', '♥', '♦', '♣']]
        random.shuffle(deck)

        player_hand = [deck.pop()]
        dealer_hand = [deck.pop()]

        context.user_data["blackjack_deck"] = deck
        context.user_data["blackjack_player"] = player_hand
        context.user_data["blackjack_dealer"] = dealer_hand

        def card_value(card):
            rank = card[:-1]
            return 11 if rank == 'A' else 10 if rank in ['J', 'Q', 'K'] else int(rank)

        player_total = sum(card_value(c) for c in player_hand)
        dealer_total = card_value(dealer_hand[0])

        keyboard = [
            [InlineKeyboardButton("Hit", callback_data="blackjack_hit"),
             InlineKeyboardButton("Stand", callback_data="blackjack_stand"),
             InlineKeyboardButton("Double Down", callback_data="blackjack_double")],
            [InlineKeyboardButton("❌ Cancel", callback_data="gamble_cancel")]
        ]

        await update.message.reply_text(
            f"🧍 Your hand: {', '.join(f'{c} ({card_value(c)})' for c in player_hand)}\n"
            f"🧍 Total: *{player_total}*\n"
            f"🤖 Dealer shows: {dealer_hand[0]} ({dealer_total})\n\n"
            f"Choose your move:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return GAMBLE_BLACKJACK

    elif game == "dice":
        keyboard = [
            [InlineKeyboardButton("Odd", callback_data="dice_odd"),
            InlineKeyboardButton("Even", callback_data="dice_even")],
            [InlineKeyboardButton("Pick Number 🎯", callback_data="dice_pick")],
            [InlineKeyboardButton("❌ Cancel", callback_data="gamble_cancel")]
        ]
        await update.message.reply_text("🎲 Choose your bet:", reply_markup=InlineKeyboardMarkup(keyboard))
        return GAMBLE_DICE
async def handle_roulette_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    balances = load_balances()
    # anti-abuse ban check
    if is_gamble_banned(balances, user_id):
        await query.edit_message_text("🚫 Casino ban: you won too much today. Come back tomorrow.")
        try:
            await query.message.delete()
        except:
            pass
        return ConversationHandler.END

    amount = context.user_data.get("gamble_amount", 0)

    # Cancel button
    if query.data == "gamble_cancel":
        await query.edit_message_text("❌ Gambling cancelled.")
        # cleanup stored prompt if any
        prompt = context.user_data.pop("gamble_prompt_message", None)
        if prompt:
            try:
                chat_id, msg_id = prompt
                await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
            except Exception:
                pass

        return ConversationHandler.END

    # Show number grid
    if query.data == "roulette_number":
        red_numbers = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
        black_numbers = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}

        number_buttons = []
        for i in range(0, 37):
            color = "🟢" if i == 0 else "🔴" if i in red_numbers else "⚫"
            number_buttons.append(InlineKeyboardButton(f"{i} {color}", callback_data=f"roulette_number_{i}"))

        rows = [number_buttons[i:i + 6] for i in range(0, len(number_buttons), 6)]
        rows.append([InlineKeyboardButton("⬅️ Back to Color Betting", callback_data="roulette_back")])

        await query.edit_message_text(
            "🎰 Pick a number to bet on:",
            reply_markup=InlineKeyboardMarkup(rows)
        )
        return GAMBLE_ROULETTE

    # Back to color betting
    if query.data == "roulette_back":
        keyboard = [
            [InlineKeyboardButton("🔴 Red", callback_data="roulette_color_red"),
             InlineKeyboardButton("⚫ Black", callback_data="roulette_color_black")],
            [InlineKeyboardButton("Pick Number", callback_data="roulette_number")],
            [InlineKeyboardButton("❌ Cancel", callback_data="gamble_cancel")]
        ]
        await query.edit_message_text("🎰 Choose your bet:", reply_markup=InlineKeyboardMarkup(keyboard))
        return GAMBLE_ROULETTE

    # Number bet
    if query.data.startswith("roulette_number_"):
        picked = int(query.data.split("_")[-1])
        result = random.randint(0, 36)
        win = (picked == result)

        if win:
            payout = amount * 35
            # award first
            balances[user_id]["coin"] = balances[user_id].get("coin", 0) + payout
            # record gambler stats and possibly tax+ban
            banned_now, tax = record_gamble_win(balances, user_id, payout)
            save_balances(balances)
            msg = f"🎯 The ball landed on {result}! You guessed right and won {payout:,} coins!"
            if banned_now:
                msg += f"\n\n🚨 You have won too many times today and are banned from the casino for the rest of the day. A tax of ⏣ {tax:,} (20%) was taken from your winnings."

        else:
            balances[user_id]["coin"] -= amount
            msg = f"💀 The ball landed on {result}. You lost {amount} coins."

        save_balances(balances)
        gif_url = random.choice(WIN_GIFS if win else LOSE_GIFS)
        await context.bot.send_animation(chat_id=query.message.chat.id, animation=gif_url, caption=msg)
        await query.message.delete()
        return ConversationHandler.END

    # Color bet
    if query.data.startswith("roulette_color_"):
        user_choice = query.data.split("_")[-1]
        result_color = random.choice(["red", "black"])
        win = (user_choice == result_color)

        if win:
            payout = amount
            balances[user_id]["coin"] = balances[user_id].get("coin", 0) + payout
            banned_now, tax = record_gamble_win(balances, user_id, payout)
            save_balances(balances)
            msg = f"🎉 The ball landed on {result_color.upper()}! You won {payout:,} coins!"
            if banned_now:
                msg += f"\n\n🚨 You have won too many times today and are banned from the casino for the rest of the day. A tax of ⏣ {tax:,} (20%) was taken from your winnings."

        else:
            balances[user_id]["coin"] -= amount
            msg = f"💀 The ball landed on {result_color.upper()}. You lost {amount} coins."

        save_balances(balances)
        gif_url = random.choice(WIN_GIFS if win else LOSE_GIFS)
        await context.bot.send_animation(chat_id=query.message.chat.id, animation=gif_url, caption=msg)
        await query.message.delete()
        return ConversationHandler.END

async def start_blackjack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    deck = [f"{rank}{suit}" for rank in ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
            for suit in ['♠', '♥', '♦', '♣']]
    random.shuffle(deck)

    player_hand = [deck.pop()]
    dealer_hand = [deck.pop()]

    context.user_data["blackjack_deck"] = deck
    context.user_data["blackjack_player"] = player_hand
    context.user_data["blackjack_dealer"] = dealer_hand

    keyboard = [
        [InlineKeyboardButton("Hit", callback_data="blackjack_hit"),
         InlineKeyboardButton("Stand", callback_data="blackjack_stand")]
    ]

    await update.message.reply_text(
        f"🧍 Your hand: {', '.join(player_hand)}\n"
        f"🤖 Dealer shows: {dealer_hand[0]}\n\n"
        f"Choose your move:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return GAMBLE_BLACKJACK

async def handle_blackjack_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    move = query.data.split("_")[-1]
    user_id = str(query.from_user.id)
    balances = load_balances()
    # anti-abuse ban check
    if is_gamble_banned(balances, user_id):
        await query.edit_message_text("🚫 Casino ban: you won too much today. Come back tomorrow.")
        try:
            await query.message.delete()
        except:
            pass
        return ConversationHandler.END

    amount = context.user_data.get("gamble_amount", 0)
    if query.data == "gamble_cancel":
        await query.edit_message_text("❌ Gambling cancelled.")
        return ConversationHandler.END

    # Simulate deck and hands
    deck = [f"{rank}{suit}" for rank in ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
            for suit in ['♠', '♥', '♦', '♣']]
    random.shuffle(deck)

    def card_value(card):
        rank = card[:-1]
        if rank in ['J', 'Q', 'K']:
            return 10
        elif rank == 'A':
            return 11
        else:
            return int(rank)

    def hand_total(hand):
        total = sum(card_value(c) for c in hand)
        # Adjust for Aces
        aces = sum(1 for c in hand if c.startswith('A'))
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]

    player_total = hand_total(player_hand)
    dealer_total = hand_total(dealer_hand)

    result_text = (
        f"🃏 You chose *{move.title()}*\n\n"
        f"🧍 Your hand: {', '.join(player_hand)} → *{player_total}*\n"
        f"🤖 Dealer hand: {', '.join(dealer_hand)} → *{dealer_total}*\n\n"
    )

    if player_total > 21:
        result_text += f"💥 You busted and lost *{amount}* coins."
        balances[user_id]["coin"] -= amount
        if player_total == 21 and len(player_hand) == 2:
            payout = int(amount * 1.5)
            balances[user_id]["coin"] += payout
            result_text += f"🎉 Blackjack! You hit 21 and earned *{ payout}* coins."
        elif dealer_total > 21 or player_total > dealer_total:
            payout = amount
            balances[user_id]["coin"] += payout
            result_text += f"🎉 You win! You earned *{payout}* coins."

        balances[user_id]["coin"] += payout
    elif player_total == dealer_total:
        result_text += f"🤝 It's a tie. You keep your *{amount}* coins."
    else:
        result_text += f"😢 Dealer wins. You lost *{amount}* coins."
        balances[user_id]["coin"] -= amount

    save_balances(balances)
    gif_url = random.choice(WIN_GIFS if "You win" in result_text or "Blackjack" in result_text else LOSE_GIFS)
    await context.bot.send_animation(chat_id=query.message.chat.id, animation=gif_url, caption=result_text,
                                     parse_mode="Markdown")
    await query.message.delete()

    return ConversationHandler.END
async def start_blackjack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    deck = [f"{rank}{suit}" for rank in ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
            for suit in ['♠', '♥', '♦', '♣']]
    random.shuffle(deck)

    player_hand = [deck.pop()]
    dealer_hand = [deck.pop()]

    context.user_data["blackjack_deck"] = deck
    context.user_data["blackjack_player"] = player_hand
    context.user_data["blackjack_dealer"] = dealer_hand

    keyboard = [
        [InlineKeyboardButton("Hit", callback_data="blackjack_hit"),
         InlineKeyboardButton("Stand", callback_data="blackjack_stand")]
    ]

    await update.message.reply_text(
        f"🧍 Your hand: {', '.join(player_hand)}\n"
        f"🤖 Dealer shows: {dealer_hand[0]}\n\n"
        f"Choose your move:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return GAMBLE_BLACKJACK
async def handle_blackjack_hit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    deck = context.user_data["blackjack_deck"]
    player_hand = context.user_data["blackjack_player"]
    dealer_hand = context.user_data["blackjack_dealer"]

    player_hand.append(deck.pop())

    def card_value(card):
        rank = card[:-1]
        return 11 if rank == 'A' else 10 if rank in ['J', 'Q', 'K'] else int(rank)

    def hand_total(hand):
        total = sum(card_value(c) for c in hand)
        aces = sum(1 for c in hand if c.startswith('A'))
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    total = hand_total(player_hand)

    if total > 21:
        amount = context.user_data["gamble_amount"]
        user_id = str(query.from_user.id)
        balances = load_balances()
        balances[user_id]["coin"] -= amount
        save_balances(balances)

        await query.edit_message_text(
            f"🧍 Your hand: {', '.join(player_hand)} → *{total}*\n"
            f"💥 You busted and lost *{amount}* coins.",
            parse_mode="Markdown"
        )
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton("Hit", callback_data="blackjack_hit"),
         InlineKeyboardButton("Stand", callback_data="blackjack_stand")]
    ]
    await query.edit_message_text(
        f"🧍 Your hand: {', '.join(player_hand)} → *{total}*\n"
        f"🤖 Dealer shows: {dealer_hand[0]}\n\n"
        f"Choose your move:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return GAMBLE_BLACKJACK
async def handle_blackjack_stand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    deck = context.user_data["blackjack_deck"]
    player_hand = context.user_data["blackjack_player"]
    dealer_hand = context.user_data["blackjack_dealer"]
    amount = context.user_data["gamble_amount"]
    user_id = str(query.from_user.id)
    balances = load_balances()

    def card_value(card):
        rank = card[:-1]
        return 11 if rank == 'A' else 10 if rank in ['J', 'Q', 'K'] else int(rank)

    def hand_total(hand):
        total = sum(card_value(c) for c in hand)
        aces = sum(1 for c in hand if c.startswith('A'))
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    player_total = hand_total(player_hand)
    dealer_total = hand_total(dealer_hand)

    while dealer_total < 17:
        dealer_hand.append(deck.pop())
        dealer_total = hand_total(dealer_hand)

    result_text = (
        f"🧍 Your hand: {', '.join(player_hand)} → *{player_total}*\n"
        f"🤖 Dealer hand: {', '.join(dealer_hand)} → *{dealer_total}*\n\n"
    )

    if dealer_total > 21 or player_total > dealer_total:
        payout = amount
        balances[user_id]["coin"] += payout
        result_text += f"🎉 You win! You earned *{payout}* coins."
    elif player_total == dealer_total:
        result_text += f"🤝 It's a tie. You keep your *{amount}* coins."
    else:
        balances[user_id]["coin"] -= amount
        result_text += f"😢 Dealer wins. You lost *{amount}* coins."

    save_balances(balances)
    gif_url = random.choice(WIN_GIFS if "You win" in result_text or "Blackjack" in result_text else LOSE_GIFS)
    await context.bot.send_animation(chat_id=query.message.chat.id, animation=gif_url, caption=result_text,
                                     parse_mode="Markdown")
    await query.message.delete()

    return ConversationHandler.END

async def handle_dice_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    balances = load_balances()
    # anti-abuse ban check
    if is_gamble_banned(balances, user_id):
        await query.edit_message_text("🚫 Casino ban: you won too much today. Come back tomorrow.")
        try:
            await query.message.delete()
        except:
            pass
        return ConversationHandler.END

    amount = context.user_data.get("gamble_amount", 0)

    # Cancel
    if query.data == "gamble_cancel":
        await query.edit_message_text("❌ Gambling cancelled.")
        return ConversationHandler.END

    # Show number buttons (1-6)
    if query.data == "dice_pick":
        number_buttons = [InlineKeyboardButton(str(i), callback_data=f"dice_number_{i}") for i in range(1, 7)]
        rows = [number_buttons[i:i+3] for i in range(0, 6, 3)]
        rows.append([InlineKeyboardButton("⬅️ Back", callback_data="dice_back")])
        await query.edit_message_text("🎯 Pick a number (1–6):", reply_markup=InlineKeyboardMarkup(rows))
        return GAMBLE_DICE

    # Back to main dice options
    if query.data == "dice_back":
        keyboard = [
            [InlineKeyboardButton("Odd", callback_data="dice_odd"),
             InlineKeyboardButton("Even", callback_data="dice_even")],
            [InlineKeyboardButton("Pick Number 🎯", callback_data="dice_pick")],
            [InlineKeyboardButton("❌ Cancel", callback_data="gamble_cancel")]
        ]
        await query.edit_message_text("🎲 Choose your bet:", reply_markup=InlineKeyboardMarkup(keyboard))
        return GAMBLE_DICE

    # Now handle actual bets: odd/even or number picks
    # Roll only after user selected an actual bet (odd/even or dice_number_X)
    roll = random.randint(1, 6)
    win = False
    payout = 0
    result_text = f"🎲 The dice rolled: *{roll}*\n"

    # Odd / Even
    if query.data in ("dice_odd", "dice_even"):
        choice = query.data.split("_")[1]
        if (roll % 2 == 0 and choice == "even") or (roll % 2 == 1 and choice == "odd"):
            win = True
            payout = amount
            result_text += f"✅ You guessed {choice} and won *{payout}* coins!"
        else:
            result_text += f"❌ You guessed {choice} and lost *{amount}* coins."

    # Number pick (1-6)
    elif query.data.startswith("dice_number_"):
        picked = int(query.data.split("_")[2])
        if picked == roll:
            win = True
            balances[user_id]["coin"] = balances[user_id].get("coin", 0) + payout
            banned_now, tax = record_gamble_win(balances, user_id, payout)
            save_balances(balances)
            result_text += f"\n\n🚨" if banned_now else ""
            if banned_now:
                result_text += f"You have won too many times today and are banned from the casino. A tax of ⏣ {tax:,} was taken."

        else:
            result_text += f"❌ You guessed {picked} and lost *{amount}* coins."

    else:
        # unexpected callback on this handler — treat as cancelled/invalid
        await query.edit_message_text("❌ Invalid option. Gambling cancelled.")
        return ConversationHandler.END

    # Apply result
    balances.setdefault(user_id, {"coin": 0})
    if win:
        balances[user_id]["coin"] = balances[user_id].get("coin", 0) + payout
        banned_now, tax = record_gamble_win(balances, user_id, payout)
        save_balances(balances)
        result_text += f"\n\n🚨" if banned_now else ""
        if banned_now:
            result_text += f"You have won too many times today and are banned from the casino. A tax of ⏣ {tax:,} was taken."

    else:
        balances[user_id]["coin"] = balances[user_id].get("coin", 0) - amount

    save_balances(balances)
    gif_url = random.choice(WIN_GIFS if win else LOSE_GIFS)

    try:
        await context.bot.send_animation(chat_id=query.message.chat.id, animation=gif_url, caption=result_text, parse_mode="Markdown")
    except Exception:
        await context.bot.send_message(chat_id=query.message.chat.id, text=result_text, parse_mode="Markdown")

    # remove the original inline message to avoid double actions
    try:
        await query.message.delete()
    except:
        pass

    return ConversationHandler.END

async def handle_blackjack_double(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    balances = load_balances()
    amount = context.user_data.get("gamble_amount", 0)

    # Double the bet
    if balances[user_id]["coin"] < amount:
        await query.edit_message_text("🚫 You don't have enough coins to double down.")
        return ConversationHandler.END

    balances[user_id]["coin"] -= amount
    doubled_amount = amount * 2
    context.user_data["gamble_amount"] = doubled_amount

    deck = context.user_data["blackjack_deck"]
    player_hand = context.user_data["blackjack_player"]
    dealer_hand = context.user_data["blackjack_dealer"]

    player_hand.append(deck.pop())  # One final card

    def card_value(card):
        rank = card[:-1]
        return 11 if rank == 'A' else 10 if rank in ['J', 'Q', 'K'] else int(rank)

    def hand_total(hand):
        total = sum(card_value(c) for c in hand)
        aces = sum(1 for c in hand if c.startswith('A'))
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    player_total = hand_total(player_hand)
    dealer_total = hand_total(dealer_hand)

    while dealer_total < 17:
        dealer_hand.append(deck.pop())
        dealer_total = hand_total(dealer_hand)

    result_text = (
        f"🧍 Your hand: {', '.join(player_hand)} → *{player_total}*\n"
        f"🤖 Dealer hand: {', '.join(dealer_hand)} → *{dealer_total}*\n\n"
    )

    if player_total > 21:
        result_text += f"💥 You busted and lost *{doubled_amount}* coins."
    elif dealer_total > 21 or player_total > dealer_total:
        payout = doubled_amount
        balances[user_id]["coin"] += payout
        result_text += f"🎉 You win! You earned *{payout}* coins."
    elif player_total == dealer_total:
        balances[user_id]["coin"] += doubled_amount
        result_text += f"🤝 It's a tie. You keep your *{doubled_amount}* coins."
    else:
        result_text += f"😢 Dealer wins. You lost *{doubled_amount}* coins."

    save_balances(balances)
    await query.edit_message_text(result_text, parse_mode="Markdown")
    return ConversationHandler.END
# ----- /crime command and handlers -----
CRIME_SELECT, CRIME_RESOLVE = range(2)

CRIMES_FILE = r"C:\Users\Administrator\Desktop\TelegramBot\data\crimes.json"

def _load_crimes():
    try:
        with open(CRIMES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("crimes", []) if isinstance(data, dict) else data
    except Exception as e:
        print("❌ Failed to load crimes.json:", e)
        return []
def _crime_emoji_for(name):
    if not name:
        return "🧾"
    key = re.sub(r"\W+", " ", name).strip().lower()
    return CRIME_EMOJI_MAP.get(key, "🧾")
def _format_crime_button_text(crime_obj):
    # short label for button
    name = crime_obj.get("crime") or "Unknown"
    return name if len(name) <= 30 else name[:27] + "..."

async def crime_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    crimes = _load_crimes()
    if not crimes:
        await update.message.reply_text("❌ No crimes data available.")
        return

    choices = random.sample(crimes, k=min(3, len(crimes)))
    context.user_data["crime_choices"] = choices

    kb = []
    for i, c in enumerate(choices):
        name = c.get("crime", "Unknown")
        emoji = _crime_emoji_for(name)
        label = f"{emoji} {name}"
        kb.append([InlineKeyboardButton(label, callback_data=f"crime_pick_{i}")])
    kb.append([InlineKeyboardButton("❌ Cancel", callback_data="crime_cancel")])

    await update.message.reply_text(
        "🔪 Choose a crime to attempt",
        reply_markup=InlineKeyboardMarkup(kb)
    )
    return CRIME_SELECT
async def crime_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = str(query.from_user.id)
    balances = load_balances()
    balances.setdefault(user_id, {"coin": 0, "bank": 0, "xp": 0, "level": 1, "inventory": {}})

    if data == "crime_cancel":
        try:
            await query.edit_message_text("❌ Crime cancelled.")
        except:
            await query.message.reply_text("❌ Crime cancelled.")
        return ConversationHandler.END

    if not data.startswith("crime_pick_"):
        await query.edit_message_text("❌ Invalid crime selection.")
        return ConversationHandler.END

    try:
        idx = int(data.split("_")[-1])
    except:
        await query.edit_message_text("❌ Invalid choice.")
        return ConversationHandler.END

    choices = context.user_data.get("crime_choices") or []
    if idx < 0 or idx >= len(choices):
        await query.edit_message_text("❌ Choice out of range.")
        return ConversationHandler.END

    crime = choices[idx]
    name = crime.get("crime", "Crime")
    emoji = _crime_emoji_for(name)
    successful_msg = crime.get("successful", "You succeeded.")
    unsuccessful_msg = crime.get("unsuccessful", "You failed.")
    death_msg = crime.get("death", "You died.")
    item = crime.get("item")
    if isinstance(item, str) and item.strip().lower() == "none":
        item = None

    def _rand_reward():
        return random.randint(500, 4000)

    r = random.random() * 100  # 0..100

    # CRITICAL FAIL (death) 2.5%
    if r < 2.5:
        user_bal = balances.get(user_id, {}).get("coin", 0)
        loss = int(user_bal * 0.15)
        balances[user_id]["coin"] = max(0, user_bal - loss)
        save_balances(balances)

        text = f"{emoji} 💀 CRITICAL FAIL!\n{death_msg}\nYou lost ⏣ {loss:,} coins (15% of your wallet)."
        # send death image
        try:
            await context.bot.send_photo(chat_id=query.message.chat.id, photo=CRIME_DEATH_IMAGE, caption=text)
        except:
            await query.edit_message_text(text)
        try:
            await query.message.delete()
        except:
            pass
        return ConversationHandler.END

    # CRITICAL SUCCESS 2.5%
    if r < 5.0:
        if item is None:
            # specified behavior: critical success -> fail if no item
            text = f"{emoji} ❌ Critical success attempted but no item available — it backfired.\n{unsuccessful_msg}"
            gif = random.choice(CRIME_FAIL_GIFS)
            try:
                await context.bot.send_animation(chat_id=query.message.chat.id, animation=gif, caption=text)
            except:
                await query.edit_message_text(text)
            try:
                await query.message.delete()
            except:
                pass
            return ConversationHandler.END
        reward = _rand_reward()
        balances[user_id]["coin"] = balances[user_id].get("coin", 0) + reward
        inv = balances[user_id].setdefault("inventory", {})
        key = normalize(item)
        inv[key] = inv.get(key, 0) + 1
        save_balances(balances)
        successful_text = successful_msg.replace("[xyz]", f"⏣ {reward:,}")
        text = f"{emoji} ✨ CRITICAL SUCCESS!\n{successful_text}\nYou earned ⏣ {reward:,} coins and also got an item: {item}."
        gif = random.choice(CRIME_CRIT_SUCCESS_GIFS)
        try:
            await context.bot.send_animation(chat_id=query.message.chat.id, animation=gif, caption=text)
        except:
            await query.edit_message_text(text)
        try:
            await query.message.delete()
        except:
            pass
        return ConversationHandler.END

    # FAIL (50% total per spec). Note ranges: we used <5 for crits; now fail if r < 50
    if r < 50.0:
        text = f"{emoji} ❌ Failed\n{unsuccessful_msg}"
        gif = random.choice(CRIME_FAIL_GIFS)
        try:
            await context.bot.send_animation(chat_id=query.message.chat.id, animation=gif, caption=text)
        except:
            await query.edit_message_text(text)
        try:
            await query.message.delete()
        except:
            pass
        return ConversationHandler.END

    # SUCCESS (~45%)
    reward = _rand_reward()
    balances[user_id]["coin"] = balances[user_id].get("coin", 0) + reward
    save_balances(balances)
    successful_text = successful_msg.replace("[xyz]", f"⏣ {reward:,}")
    text = f"{emoji} ✅ Success!\n{successful_text}\nYou earned ⏣ {reward:,} coins."
    gif = random.choice(CRIME_SUCCESS_GIFS)
    try:
        await context.bot.send_animation(chat_id=query.message.chat.id, animation=gif, caption=text)
    except:
        await query.edit_message_text(text)
    try:
        await query.message.delete()
    except:
        pass
    return ConversationHandler.END
async def handle_slots_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    balances = load_balances()
    balances.setdefault(user_id, {"coin": 0, "bank": 0, "xp": 0, "level": 1, "inventory": {}})

    # cancel
    if query.data == "gamble_cancel":
        try:
            await query.edit_message_text("❌ Gambling cancelled.")
        except:
            await query.message.reply_text("❌ Gambling cancelled.")
        return ConversationHandler.END

    # only handle the spin action here
    if query.data != "slots_spin":
        await query.edit_message_text("❌ Invalid option. Gambling cancelled.")
        return ConversationHandler.END

    # read bet
    amount = context.user_data.get("gamble_amount", 0)
    if amount <= 0:
        await query.edit_message_text("❌ Bet amount missing or invalid.")
        return ConversationHandler.END

    # balance checks
    user_coin = balances[user_id].get("coin", 0)
    if amount > user_coin:
        await query.edit_message_text("🚫 You don't have enough coins.")
        return ConversationHandler.END
    if amount > SLOT_MAX_BET:
        await query.edit_message_text(f"🚫 Max slots bet is {SLOT_MAX_BET:,} coins.")
        return ConversationHandler.END

    # deduct bet immediately
    balances[user_id]["coin"] = max(0, user_coin - amount)
    save_balances(balances)

    # edit to show spinning
    try:
        await query.edit_message_text("🎰 Spinning... good luck!")
    except:
        pass

    # compute reels
    reel = [random.choice(SLOT_SYMBOLS) for _ in range(3)]
    reel_text = " | ".join(reel)

    payout = 0
    # three of a kind
    if reel[0] == reel[1] == reel[2]:
        payout = amount * SLOT_PAYOUTS.get(reel[0], 0)
    # two of a kind consolation
    elif reel[0] == reel[1] or reel[1] == reel[2] or reel[0] == reel[2]:
        payout = int(amount * 0.25)

    # apply payout
    if payout > 0:
        balances[user_id]["coin"] = balances[user_id].get("coin", 0) + payout
        save_balances(balances)
        if reel[0] == reel[1] == reel[2]:
            text = f"🎰 {reel_text}\n\n🎉 Jackpot! You won ⏣ {payout:,} (x{SLOT_PAYOUTS.get(reel[0],0)})"
            gif = random.choice([
                "https://i.pinimg.com/originals/51/18/27/511827714088e54af308b7a13a3a9f08.gif",
                "https://media.tenor.com/up3wjjJPq2IAAAAM/dankies-pepe.gif"
            ])
            try:
                await context.bot.send_animation(chat_id=query.message.chat.id, animation=gif, caption=text)
            except:
                await query.message.reply_text(text)
        else:
            text = f"🎰 {reel_text}\n\n✅ You recovered ⏣ {payout:,} (two of a kind)."
            try:
                await context.bot.send_animation(chat_id=query.message.chat.id, animation="https://media.tenor.com/71K1Mm4YxX4AAAAM/money-make.gif", caption=text)
            except:
                await query.message.reply_text(text)
    else:
        # lost — already deducted
        text = f"🎰 {reel_text}\n\n💀 No win. You lost ⏣ {amount:,}."
        gif = random.choice([
            "https://media.tenor.com/xD5L-EvTKqIAAAAM/crying.gif",
            "https://media.tenor.com/HZClb9KQ7o0AAAAM/pepe-rain-pepe-the-frog.gif",
            "https://media.tenor.com/hMn2g7TfBpcAAAAM/pepe-sad-pepe-cry.gif"
        ])
        try:
            await context.bot.send_animation(chat_id=query.message.chat.id, animation=gif, caption=text)
        except:
            await query.message.reply_text(text)

    # cleanup original inline message to prevent re-clicking
    try:
        await query.message.delete()
    except:
        pass

    return ConversationHandler.END

def _now_ts():
    return int(time.time())

def _ensure_user_fields(balances, uid):
    u = balances.setdefault(uid, {})
    u.setdefault("coin", 0)
    u.setdefault("bank", 0)
    u.setdefault("xp", 0)
    u.setdefault("level", 1)
    u.setdefault("inventory", {})
    u.setdefault("titles", [])
    # daily fields
    u.setdefault("last_daily", 0)
    u.setdefault("daily_streak", 0)
    u.setdefault("last_daily_claim_date", "")  # iso date string for easy streak logic
    return u

def _iso_date(ts=None):
    return datetime.utcfromtimestamp(ts or _now_ts()).strftime("%Y-%m-%d")

async def daily_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Claim daily reward. 24h cooldown, streaks persist in balances.json."""
    user_id = str(update.effective_user.id)
    balances = load_balances()
    balances.setdefault(user_id, {})
    user = _ensure_user_fields(balances, user_id)

    now = _now_ts()
    last = int(user.get("last_daily", 0) or 0)
    elapsed = now - last

    if elapsed < DAILY_COOLDOWN:
        remaining = DAILY_COOLDOWN - elapsed
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        seconds = remaining % 60
        return await update.message.reply_text(
            f"⏳ You already claimed daily. Come back in {hours}h {minutes}m {seconds}s."
        )

    # Determine streak: if last claim was exactly yesterday (UTC date), increment; else reset.
    last_date = user.get("last_daily_claim_date", "")
    today = _iso_date(now)
    yesterday = _iso_date(now - DAILY_COOLDOWN)

    if last_date == yesterday:
        user["daily_streak"] = min(DAILY_MAX_STREAK, int(user.get("daily_streak", 0)) + 1)
    else:
        user["daily_streak"] = 1

    # compute reward
    base = random.randint(DAILY_BASE_MIN, DAILY_BASE_MAX)
    streak_bonus = user["daily_streak"] * DAILY_STREAK_BONUS_PER_DAY
    total = base + streak_bonus

    # XP reward scaling (small)
    xp_gain = 25 + user["daily_streak"] // 2

    # apply
    user["coin"] = user.get("coin", 0) + total
    user["xp"] = user.get("xp", 0) + xp_gain
    user["last_daily"] = now
    user["last_daily_claim_date"] = today

    save_balances(balances)

    # Message
    streak = user["daily_streak"]
    await update.message.reply_text(
        f"🌞 Daily claimed!\n\n"
        f"⏣ You got {total:,} coins (base {base:,} + streak bonus {streak_bonus:,})\n"
        f"⭐ Streak: {streak} day{'s' if streak != 1 else ''}\n"
        f"📈 XP gained: {xp_gain}\n\n"
        f"Come back in 24 hours to claim again!"
    )

    # give XP level check (non-blocking)
    try:
        await add_xp(user_id, "Daily", update, context)
    except Exception:
        pass


async def _inventory_summary(inv, limit=6):
    """Return short inventory summary string (top items) with emojis."""
    if not inv:
        return "None"

    # small emoji map for common items (extend as needed)
    emoji_map = {
        "axolotl": "🦎",
        "birb": "🐦",
        "bunny": "🐰",
        "cat": "🐱",
        "catgirl": "😺",
        "crab": "🦀",
        "dog": "🐶",
        "duck": "🦆",
        "fox": "🦊",
        "hamster": "🐹",
        "kraken": "🦑",
        "monkey": "🐒",
        "pepe": "🐸",
        "rock": "🪨",
        "turtle": "🐢",

        "padlock": "🔐", "shovel": "⛏️", "cutters": "✂️", "newplayerpack": "🎁",
        "huntingrifle": "🏹", "fishingpole": "🎣",
        "starfish": "⭐🐠", "boxfish": "📦🐠", "shrimp": "🍤", "jellyfish": "🪼",
        "butterflyfish": "🦋🐠", "whiteperch": "⚪🐟", "bluetang": "🔵🐠",
        "bluegill": "🔷🐟", "yellowperch": "🟡🐟",
        "boar": "🐗", "skunk": "🦨", "deer": "🦌",
        "ant": "🐜", "fossil": "🦴", "banknote": "💵", "garbage": "🗑️",
        "ammo": "🔫", "pepe": "🐸", "cat": "🐱", "eyeballbait": "👁️🪱",
        "luckybait": "🍀🪱", "magnetbait": "🧲🪱", "xpbait": "📚🪱",
        "dynamite": "🧨", "weightedbait": "⚖️🪱", "adventurecompass": "🧭",
    }

    def norm_key(k):
        return re.sub(r'\W+', '', k).lower()

    items = sorted(inv.items(), key=lambda kv: kv[1], reverse=True)
    lines = []
    for k, v in items[:limit]:
        key = norm_key(k)
        emoji = emoji_map.get(key, None)
        # if not in map, try some heuristics: if key contains known words
        if not emoji:
            if "fish" in key:
                emoji = "🐟"
            elif "bait" in key:
                emoji = "🪱"
            elif "pet" in key or key in ("cat", "dog", "pepe"):
                emoji = "🐾"
            else:
                emoji = "📦"
        lines.append(f"{emoji} {k.title()} x{v}")

    if len(items) > limit:
        lines.append(f"...and {len(items)-limit} more")
    return "\n".join(lines)

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user profile: coins, bank, xp, level, streak, titles, top inventory."""
    user_id = str(update.effective_user.id)
    balances = load_balances()
    if user_id not in balances:
        return await update.message.reply_text("Use /start to begin!")

    user = balances[user_id]
    coin = user.get("coin", 0)
    bank = user.get("bank", 0)
    level = user.get("level", 1)
    xp = user.get("xp", 0)
    xp_needed = xp_required_for_level(level)
    streak = user.get("daily_streak", 0)
    titles = user.get("titles", [])
    inv = user.get("inventory", {})

    bar_len = 20
    filled = int((xp / xp_needed) * bar_len) if xp_needed > 0 else bar_len
    bar = "█" * filled + "░" * (bar_len - filled)

    # compute highest title for display based on level
    earned_title = get_title_for_level(level)
    # include both automatic level title and any special titles in user record
    record_titles = user.get("titles", []) or []
    # prefer recorded titles if any, otherwise show auto-earned title
    display_title = ", ".join(record_titles) if record_titles else earned_title

    inv_text = await _inventory_summary(inv, limit=6)

    msg = (
        f"👤 Profile: {update.effective_user.full_name}\n\n"
        f"⏣ Wallet: {coin:,}\n"
        f"🏦 Bank: {bank:,}\n\n"
        f"📈 Level: {level}    XP: {xp:,} / {xp_needed:,}\n"
        f"[{bar}]\n\n"
        f"🔥 Daily streak: {streak} day{'s' if streak != 1 else ''}\n"
        f"🏷️ Title: {display_title}\n\n"
        f"📦 Inventory (top):\n{inv_text}"
    )


    await update.message.reply_text(msg)
async def _is_owner(user):
    return (user and (user.username or "").lower() == OWNER_USERNAME.lower())

async def setbalance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = update.effective_user
    if not await _is_owner(sender):
        return await update.message.reply_text("❌ Not authorized.")
    try:
        target = update.message.reply_to_message.from_user if update.message.reply_to_message else None
        if not target:
            return await update.message.reply_text("Reply to a user to set their balance.")
        amount = int(context.args[0])
    except Exception:
        return await update.message.reply_text("Usage: reply to a user then /setbalance <amount>")
    uid = str(target.id)
    balances = load_balances()
    before = balances.setdefault(uid, {}).get("coin", 0)
    balances.setdefault(uid, {})["coin"] = amount
    save_balances(balances)
    with open("admin_give_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.utcnow().isoformat()}Z\tsetbalance\towner:@{sender.username}\tuser:{uid}\tfrom:{before}\tto:{amount}\n")
    await update.message.reply_text(f"✅ Set {target.full_name} balance to {amount:,} (was {before:,}).")

async def take_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = update.effective_user
    if not await _is_owner(sender):
        return await update.message.reply_text("❌ Not authorized.")
    try:
        target = update.message.reply_to_message.from_user if update.message.reply_to_message else None
        if not target:
            return await update.message.reply_text("Reply to a user to take balance from.")
        amount = int(context.args[0])
    except Exception:
        return await update.message.reply_text("Usage: reply to a user then /take <amount>")
    uid = str(target.id)
    balances = load_balances()
    before = balances.setdefault(uid, {}).get("coin", 0)
    balances[uid]["coin"] = max(0, before - amount)
    save_balances(balances)
    with open("admin_give_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.utcnow().isoformat()}Z\ttake\towner:@{sender.username}\tuser:{uid}\tfrom:{before}\tto:{balances[uid]['coin']}\n")
    await update.message.reply_text(f"✅ Took {amount:,} from {target.full_name}. New balance {balances[uid]['coin']:,}.")

# Simple rollback helper: restore balances.json from a backup file path argument (owner only)
async def rollback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = update.effective_user
    if not await _is_owner(sender):
        return await update.message.reply_text("❌ Not authorized.")
    try:
        backup_path = context.args[0]
        if not os.path.exists(backup_path):
            return await update.message.reply_text("Backup file not found.")
        with open(backup_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        save_balances(data)
        await update.message.reply_text("✅ Restored balances from backup.")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to rollback: {e}")

def _now_ts():
    return int(time.time())

# --- per-player cooldown helpers