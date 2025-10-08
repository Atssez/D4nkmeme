import os
import json
import re
import tempfile
import shutil
from telegram.error import RetryAfter
from telegram.ext import CallbackContext
from utils import load_balances, save_balances, user_data
from commands2 import work_command,sell_command, handle_work_choice, handle_fish_navigation,handle_hunt
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from commands2 import heist_message_collector
from datetime import datetime
OWNER_USERNAME = "atssez"
from commands2 import crime_command, crime_callback, CRIME_SELECT , setbalance_command,take_command,rollback_command
from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)
GAMBLE_CHOICE, GAMBLE_AMOUNT, GAMBLE_ROULETTE, GAMBLE_BLACKJACK, GAMBLE_DICE = range(5)

from commands2 import (
    gamble_command,
    handle_gamble_choice,
    handle_gamble_amount,
    handle_roulette_logic,
    handle_blackjack_logic,
    handle_dice_logic,
    GAMBLE_CHOICE,
    GAMBLE_AMOUNT,
    GAMBLE_ROULETTE,
    GAMBLE_BLACKJACK,
    GAMBLE_DICE,
    handle_blackjack_hit,
    handle_blackjack_stand,
handle_blackjack_double,
    daily_command,
    profile_command,
handle_slots_callback
)
import time
import asyncio
from telegram import InputMediaPhoto
from telegram.ext import ApplicationHandlerStop
FAIL_IMAGE_PATH = r"C:\Users\Administrator\Desktop\TelegramBot\pepe-lying-on-floor-crying-over-whatever-you-want-v0-s8x71lwq6vpd1.png"
# Cooldown tracking
last_deposit_time = {}
last_withdraw_time = {}
COOLDOWN_SECONDS = 300  # 5 minutes
from commands2 import (
    handle_cast_fish,
    confirm_sell_callback,
    cancel_sell_callback
)
from telegram.ext import Application
import requests
from io import BytesIO
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
import random

# ==========================
# 🔧 Configuration
# ==========================
def normalize(text):
    return re.sub(r'\W+', '', text).lower()
def _parse_coins(text: str) -> int:
    if not text:
        return 0
    s = text.lower().replace(",", "").strip()
    m = re.search(r"(\d+(?:\.\d+)?)(k)?", s)
    if not m:
        return 0
    num = float(m.group(1))
    if m.group(2) == "k":
        num = int(num * 1000)
    return int(num)
def _ensure_adventure_state(user_data):
    user_data.setdefault("pending_adventure_rewards", None)
    user_data.setdefault("adventure_failed", False)
    user_data.setdefault("next_scenario_id", None)

def _parse_items(text: str) -> dict:
    items = {}
    if not text:
        return items
    for m in re.finditer(r"([A-Za-z0-9 _\-]+)\s*x\s*(\d+)", text, flags=re.I):
        key = normalize(m.group(1))
        cnt = int(m.group(2))
        items[key] = items.get(key, 0) + cnt
    # fallback: single-word item names (like "Gold Nugget") — add as single count if found
    # This tries to map common single-item outcomes (no count). You can customize keys as needed.
    words = text.splitlines()
    for w in words:
        w = w.strip()
        if w and any(ch.isalpha() for ch in w) and "coin" not in w.lower() and "end safely" not in w.lower():
            # if not already parsed as count, add single item (use normalized key)
            key = normalize(w)
            if key and key not in items and len(w.split()) <= 3:  # avoid long sentences
                # simple heuristic: treat as one item if looks like item name
                items[key] = items.get(key, 0) + 1
    return items

def _apply_pending_adventure_rewards(query, user_data):
    """Apply and clear pending rewards for the current user. Returns a summary dict."""
    pending = user_data.get("pending_adventure_rewards")
    if not pending:
        return {"coins": 0, "items": []}
    balances = load_balances()
    uid = str(query.from_user.id)
    balances.setdefault(uid, {})
    balances[uid].setdefault("coin", 0)
    balances[uid].setdefault("inventory", {})
    # apply coins
    coins = int(pending.get("coins", 0) or 0)
    if coins:
        balances[uid]["coin"] = balances[uid].get("coin", 0) + coins
    # apply items
    items_applied = []
    for item_key, count in (pending.get("items") or {}).items():
        if not item_key or count <= 0:
            continue
        inv = balances[uid].setdefault("inventory", {})
        inv[item_key] = inv.get(item_key, 0) + int(count)
        items_applied.append((item_key, int(count)))
    save_balances(balances)
    # clear pending
    user_data["pending_adventure_rewards"] = None
    return {"coins": coins, "items": items_applied}

def load_bot_data(app):
    with open("data/fish_npc.json", "r", encoding="utf-8") as f:
        app.bot_data["fish_npc"] = json.load(f)
    with open("shop_items.json", "r", encoding="utf-8") as f:
        app.bot_data["shop_items"] = json.load(f)
    with open("data/fish_baits.json", "r", encoding="utf-8") as f:
        app.bot_data["fish_baits"] = json.load(f)
    with open("data/fishing_tools.json", "r", encoding="utf-8") as f:
        app.bot_data["tools"] = json.load(f)
    # load all locations once
    with open("data/fish_loc.json", "r", encoding="utf-8") as f:
        locations = app.bot_data["fish_locations"] = json.load(f)
    # Load fish prices from individual fish JSON files
    fish_folder = "data/fish_fishes"
    fish_values = {}

    for filename in os.listdir(fish_folder):
        if filename.endswith(".json"):
            path = os.path.join(fish_folder, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    name = data.get("name")
                    price = data.get("price")
                    if name and isinstance(price, (int, float)):
                        key = normalize(name)
                        fish_values[key] = int(price)
            except Exception as e:
                print(f"⚠️ Error loading {filename}: {e}")
    app.bot_data["fish_values"] = fish_values
    # Extract all fish names from fish_loc.json
    # Extract all fish names directly from fish_fishes folder
    fish_keys = set()
    fish_folder = "data/fish_fishes"

    for filename in os.listdir(fish_folder):
        if filename.endswith(".json"):
            path = os.path.join(fish_folder, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    name = data.get("name")
                    if name:
                        fish_keys.add(normalize(name))
            except Exception as e:
                print(f"⚠️ Error reading {filename}: {e}")

    app.bot_data["fish_keys"] = fish_keys

    # filter only entries that actually have a 'link'
    valid_locations = [loc for loc in locations if isinstance(loc, dict) and "link" in loc]
    if not valid_locations:
        raise ValueError("❌ fish_loc.json has no valid entries with 'link' key.")

    # pick one at random for your fallback image
    app.bot_data["location_image"] = random.choice(valid_locations)["link"]



with open("data/pepe_adventure.json", "r", encoding="utf-8") as f:
    adventure_data = json.load(f)
BOT_TOKEN = "8255087799:AAFYsgjh9TVW8k10XtdL11LPmztwVleGHsY"
BALANCE_FILE = "balances.json"
SHOP_ITEMS_FILE = "shop_items.json"
ITEM_IMAGE_FOLDER = "picture_renamed"
LEVEL_REWARDS_FILE = "level_rewards.json"
STARTING_Coin = 100_000
BANK_CAPACITY = 5_000
SHOP_CHANNEL_ID = -1003059305242
SHOP_MESSAGE_ID = 3
COMMAND_XP_VALUES = {
    "Achievements": 5,
    "Balance": 1,
    "Deposit": 15,
    "Inventory": 3,
    "Shop": 4,
    "Use": 50,
    "Rob": 25,
    "Beg": 10,
    "Gamble" : 15,
    "Adventure" : 40
}
BEG_SUCCESS_IMAGE = "https://pbs.twimg.com/media/GPsaG2vWQAAvUi_?format=png&name=small"
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
user_data = {}

PET_KEYS = ["axolotl",
    "birb",
    "bunny",
    "cat",
    "catgirl",
    "crab",
    "dog",
    "duck",
    "fox",
    "hamster",
    "kraken",
    "monkey",
    "panda bear",
    "pepe",
    "rock",
    "turtle"]
PET_EMOJIS = {
    "axolotl": "🦎",
    "birb": "🐦",
    "bunny": "🐰" ,
    "cat": "🐱" ,
    "catgirl" :"😺" ,
    "crab" :"🦀" ,
    "dog":"🐶",
    "duck":"🦆",
    "fox":"🦊",
    "hamster":"🐹",
    "kraken":"🦑",
    "monkey":"🐒",
    "pepe":"🐸",
    "rock":"🪨",
    "turtle":"🐢"
}

USER_CACHE_FILE = "user_cache.json"

TRANSACTION_LOG = "transactions.log"
# ==========================
# emoji loading
# ==========================
def load_item_emojis_by_name():
    emoji_map = {}
    with open("items.txt", "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(" ", 1)
            if len(parts) == 2:
                name, emoji = parts
                key = name.replace("_", " ").lower().strip()  # ✅ Normalize to lowercase
                emoji_map[key] = emoji.strip()
        for item in powerups + sellables:
            name = item["name"].lower()
            emoji_map[name] = item.get("emoji", "")

    return emoji_map

def load_tool_emojis_by_name():
    tools = json.load(open("data/fishing_tools.json", "r", encoding="utf-8"))
    return {tool["name"].lower(): tool["emoji"] for tool in tools}

def load_fail_reactions():
    with open("fail_reactions.json", "r", encoding="utf-8") as f:
        return json.load(f)
with open("pets.json", "r", encoding="utf-8") as f:
    pet_data = json.load(f)
# ==========================
# 📦 Balance Storage
# ==========================

async def error_handler(update, context):
    print(f"Error: {context.error}")
    if update and update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Something went wrong. Please try again later."
        )

def update_balance(user_id, coin=None, bank=None, inventory=None):
    balances = load_balances()
    user = balances.setdefault(user_id, {})
    if coin is not None:
        user["coin"] = coin
    if bank is not None:
        user["bank"] = bank
    if inventory is not None:
        user["inventory"] = inventory
    save_balances(balances)
def load_balances():
    if not os.path.exists(BALANCE_FILE):
        return {}
    with open(BALANCE_FILE, "r") as f:
        return json.load(f)


def _atomic_write(path, data_str):
    tmp = None
    dirn = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(prefix="balances-", dir=dirn, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data_str)
        # atomic replace
        shutil.move(tmp, path)
    finally:
        if tmp and os.path.exists(tmp):
            try:
                os.remove(tmp)
            except:
                pass

def save_balances(data):
    """Atomic save of balances.json and append a compact transaction snapshot."""
    try:
        s = json.dumps(data, indent=2, ensure_ascii=False)
        _atomic_write(BALANCE_FILE, s)
    except Exception as e:
        print("❌ Failed to save balances atomically:", e)
    # append a brief snapshot line to transaction log (timestamp + total users + optional size)
    try:
        ts = datetime.utcnow().isoformat() + "Z"
        total_users = len(data) if isinstance(data, dict) else 0
        with open(TRANSACTION_LOG, "a", encoding="utf-8") as f:
            f.write(f"{ts}\tusers={total_users}\n")
    except Exception:
        pass
def load_level_rewards():
    if not os.path.exists(LEVEL_REWARDS_FILE):
        return {}
    with open(LEVEL_REWARDS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)["levelRewards"]
def load_user_cache():
    if not os.path.exists(USER_CACHE_FILE):
        return {}
    with open(USER_CACHE_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_user_cache(data):
    with open(USER_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
# ==========================
# 🛍️ Pets
# ==========================
async def _adv_send_start_button(query):
    kb = [[InlineKeyboardButton("🚀 Start Adventure", callback_data="adv_start")]]
    await query.edit_message_caption("Ready to begin?", parse_mode="Markdown",
                                   reply_markup=InlineKeyboardMarkup(kb))
async def _adv_send_scenario(query, context, sid):
    """Post scenario #sid with its inline choice buttons."""
    scenario = adventure_data[sid - 1]
    buttons = [
        InlineKeyboardButton(c["option"], callback_data=f"adv_choice_{sid}_{i}")
        for i, c in enumerate(scenario["choices"])
    ]
    kb = InlineKeyboardMarkup([buttons[i:i+2] for i in range(0, len(buttons), 2)])
    await query.edit_message_caption(
        f"*Scenario {sid}:* {scenario['scenario']}",
        parse_mode="Markdown",
        reply_markup=kb
    )
async def adventure_command(update, context):
    """Show splash #1 (Pepe Goes To Space) with Next/Confirm controls."""
    context.user_data["adv_index"] = 0
    context.chat_data["adventure_owner"] = update.effective_user.id

    keyboard = [
        [
            InlineKeyboardButton("Next ❯", callback_data="adv_next"),
            InlineKeyboardButton("Confirm", callback_data="adv_confirm")
        ]
    ]
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open(r"C:\Users\Administrator\Desktop\TelegramBot\data\advpic\PepeGoesToSpace.png", "rb"),
        caption="🌌 **Pepe Goes To Space**",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
async def error_handler(update, context):
    err = context.error
    print(f"Error: {err}")
    if isinstance(err, RetryAfter):
        # log and skip sending a message to avoid cascading RetryAfter
        print(f"Flood control: retry after {err.retry_after} seconds")
        return
    # safe: only try to notify for other errors
    if update and update.effective_chat:
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="⚠️ Something went wrong. Please try again later."
            )
        except RetryAfter as ra:
            print(f"Suppressed notification due to flood control: {ra.retry_after}s")
        except Exception as e:
            print(f"Failed to send error notification: {e}")
async def _safe_edit(query, text_func,reply_markup=None):
    """Try editing the message, handle RetryAfter by waiting, suppress other edit errors."""
    try:
        if query.message.photo:
            await query.edit_message_caption(text_func(), parse_mode="Markdown", reply_markup=reply_markup)
        else:
            await query.edit_message_text(text_func(), parse_mode="Markdown", reply_markup=reply_markup)
        return True
    except RetryAfter as ra:
        wait = getattr(ra, "retry_after", 1)
        print(f"Flood control: retry after {wait}s (during progress updates)")
        await asyncio.sleep(wait)
        try:
            if query.message.photo:
                await query.edit_message_caption(text_func(), parse_mode="Markdown", reply_markup=reply_markup)
            else:
                await query.edit_message_text(text_func(), parse_mode="Markdown", reply_markup=reply_markup)
            return True
        except Exception as e:
            print(f"Progress update suppressed after RetryAfter: {e}")
            return False
    except Exception as e:
        print(f"Progress update suppressed: {e}")
        return False
async def adventure_callback(update, context):
    query = update.callback_query
    await query.answer()
    user_data = context.user_data
    idx = user_data.get("adv_index", 0)
    owner_id = context.chat_data.get("adventure_owner")
    if owner_id and query.from_user.id != owner_id:
        await query.answer("❌ This adventure isn't yours!", show_alert=True)
        return

    # ---------- splash paging ----------
    if query.data == "adv_next":
        idx = min(1, idx + 1)
        user_data["adv_index"] = idx

    if query.data == "adv_prev":
        idx = max(0, idx - 1)
        user_data["adv_index"] = idx

    if query.data in ("adv_next", "adv_prev"):
        pic = [
            r"C:\Users\Administrator\Desktop\TelegramBot\data\advpic\PepeGoesToSpace.png",
            r"C:\Users\Administrator\Desktop\TelegramBot\data\advpic\PepeGoesOutWest.png"
        ][idx]
        keyboard = []
        if idx == 1:
            keyboard.append([
                InlineKeyboardButton("❮ Previous", callback_data="adv_prev"),
                InlineKeyboardButton("Confirm", callback_data="adv_confirm")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("Next ❯", callback_data="adv_next"),
                InlineKeyboardButton("Confirm", callback_data="adv_confirm")
            ])
        await query.edit_message_media(
            media=InputMediaPhoto(open(pic, "rb"),
                                  caption=("🌌 Pepe Goes To Space" if idx == 0 else "🤠 Pepe Goes Out West")),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    # ---------- confirm splash ----------
    if query.data == "adv_confirm":
        if idx == 0:
            if query.message.photo:
                await query.edit_message_caption("⚙️ *Under progress...*", parse_mode="Markdown")
            else:
                await query.edit_message_text("⚙️ *Under progress...*", parse_mode="Markdown")
            return

        balances = load_balances()
        inv = balances.get(str(query.from_user.id), {}).get("inventory", {})
        choices = []
        if inv.get("lifesaver", 0) > 0:
            choices.append("lifesaver")
        if inv.get("apple", 0) > 0:
            choices.append("apple")

        if choices:
            kb = [
                [InlineKeyboardButton(item.title(), callback_data=f"adv_bag_{item}")]
                for item in choices
            ]
            kb.append([InlineKeyboardButton("Skip 🏃", callback_data="adv_bag_skip")])
            await query.edit_message_caption(
                "🎒 *What do you want to keep in your backpack?*",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(kb)
            )
        else:
            await _adv_send_start_button(query)
        return

    # ---------- backpack stash ----------
    if query.data.startswith("adv_bag_"):
        choice = query.data.split("_", 2)[2]
        if choice != "skip":
            balances = load_balances()
            user_id = str(query.from_user.id)
            inv = balances.setdefault(user_id, {}).setdefault("inventory", {})
            if inv.get(choice, 0) > 0:
                inv[choice] -= 1
                user_data.setdefault("backpack", []).append(choice)
                save_balances(balances)
                if query.message.photo:
                    await query.edit_message_caption(f"🎉 *{choice.title()}* added to backpack!", parse_mode="Markdown")
                else:
                    await query.edit_message_text(f"🎉 *{choice.title()}* added to backpack!", parse_mode="Markdown")
            else:
                if query.message.photo:
                    await query.edit_message_caption(f"❌ You don’t have any {choice.title()} left.", parse_mode="Markdown")
                else:
                    await query.edit_message_text(f"❌ You don’t have any {choice.title()} left.", parse_mode="Markdown")

        await _adv_send_start_button(query)
        return

    # ---------- start / continue ----------
    if query.data == "adv_start":
        user_data["current_scenario"] = 1
        user_data["pending_adventure_rewards"] = None
        user_data["adventure_failed"] = False
        user_data["next_scenario_id"] = 1
        user_data["adv_last_choice_ts"] = 0
        await _adv_send_scenario(query, context, 1)
        return

    # Cooldown enforcement helper (15s)
    def _cooldown_remaining(user_data):
        last = user_data.get("adv_last_choice_ts", 0)
        elapsed = time.time() - last
        remaining = 15 - int(elapsed)
        return max(0, remaining)

    # When Continue pressed: if next_id exists, run cooldown sequence then send next scenario
    if query.data == "adv_continue":
        next_id = user_data.get("next_scenario_id")
        # finalize if no next or failed
        if not next_id or user_data.get("adventure_failed") or next_id > len(adventure_data):
            if not user_data.get("adventure_failed"):
                applied = _apply_pending_adventure_rewards(query, user_data)
            else:
                user_data["pending_adventure_rewards"] = None
                applied = {"coins": 0, "items": []}

            summary_parts = []
            if applied.get("coins"):
                summary_parts.append(f"⏣ {applied['coins']:,} coins added")
            if applied.get("items"):
                items_str = ", ".join(f"{k} x{v}" for k, v in applied["items"])
                summary_parts.append(f"Items: {items_str}")
            summary = ("\n\n" + "✅ Rewards: " + "; ".join(summary_parts)) if summary_parts else ""
            if query.message.photo:
                await query.edit_message_caption("🏁 *Adventure Complete!*" + summary, parse_mode="Markdown")
            else:
                await query.edit_message_text("🏁 *Adventure Complete!*" + summary, parse_mode="Markdown")
            return

        # enforce cooldown before allowing transition to the next scenario
        remaining = _cooldown_remaining(user_data)
        if remaining > 0:
            await query.answer(f"⏳ Wait {remaining}s before moving on.", show_alert=True)
            return

        # update last choice timestamp to start cooldown
        user_data["adv_last_choice_ts"] = time.time()

        # show intermediate walking/progress message with initial bar
        walking_line = "Pepe walking to the next event 🚶"
        total_seconds = 15
        updates = 5
        interval = total_seconds / updates
        bar_width = 15

        await _safe_edit(query,lambda: f"{walking_line}\n\n[{'░' * bar_width}]")

        start_ts = time.time()
        for i in range(1, updates + 1):
            filled = int((i / updates) * bar_width)
            bar = "█" * filled + "░" * (bar_width - filled)
            await asyncio.sleep(interval)
            await _safe_edit(query, lambda: f"{walking_line}\n\n[{bar}]")

        # ensure full cooldown
        elapsed = time.time() - start_ts
        remaining = total_seconds - elapsed
        if remaining > 0:
            await asyncio.sleep(remaining)

        # show Continue button after cooldown
        await _safe_edit(
            query,
            lambda: f"{walking_line}\n\n[{'█' * bar_width}]",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➡️ Continue", callback_data="adv_continue_ready")]
            ])
        )

        return
    if query.data == "adv_continue_ready":
        next_id = user_data.get("next_scenario_id")
        if not next_id or user_data.get("adventure_failed") or next_id > len(adventure_data):
            if not user_data.get("adventure_failed"):
                applied = _apply_pending_adventure_rewards(query, user_data)
            else:
                user_data["pending_adventure_rewards"] = None
                applied = {"coins": 0, "items": []}

            summary_parts = []
            if applied.get("coins"):
                summary_parts.append(f"⏣ {applied['coins']:,} coins added")
            if applied.get("items"):
                items_str = ", ".join(f"{k} x{v}" for k, v in applied["items"])
                summary_parts.append(f"Items: {items_str}")
            summary = ("\n\n" + "✅ Rewards: " + "; ".join(summary_parts)) if summary_parts else ""
            if query.message.photo:
                await query.edit_message_caption("🏁 *Adventure Complete!*" + summary, parse_mode="Markdown")
            else:
                await query.edit_message_text("🏁 *Adventure Complete!*" + summary, parse_mode="Markdown")
            return

        await _adv_send_scenario(query, context, next_id)
        return

    # ---------- scenario choice ----------
    parts = query.data.split("_")
    if len(parts) == 4 and parts[0] == "adv" and parts[1] == "choice":
        try:
            sid = int(parts[2])
        except (ValueError, IndexError):
            await query.answer("❌ Invalid scenario id.", show_alert=True)
            return

        if sid < 1 or sid > len(adventure_data):
            await query.answer("❌ Scenario out of range.", show_alert=True)
            return

        scenario = adventure_data[sid - 1]

        raw_opt = parts[3]
        opt = None
        try:
            opt = int(raw_opt)
        except ValueError:
            for i, c in enumerate(scenario.get("choices", [])):
                if str(c.get("option", "")).lower() == raw_opt.replace("%20", " ").lower():
                    opt = i
                    break
            if opt is None:
                for i, c in enumerate(scenario.get("choices", [])):
                    if raw_opt.lower() in str(c.get("option", "")).lower():
                        opt = i
                        break

        if opt is None:
            await query.answer("❌ Invalid choice identifier.", show_alert=True)
            return

        try:
            choice = scenario["choices"][opt]
        except (IndexError, TypeError) as e:
            await query.answer("❌ Choice index invalid.", show_alert=True)
            print(f"Adventure error: {e}")
            return

        outcome = random.choice(choice["outcomes"])

        # parse rewards (helpers _parse_coins / _parse_items are expected to exist)
        coins = _parse_coins((outcome.get("result") or "") + " " + (outcome.get("reaction") or ""))
        items = _parse_items((outcome.get("result") or "") + " " + (outcome.get("reaction") or ""))

        pending = user_data.get("pending_adventure_rewards") or {"coins": 0, "items": {}}
        if coins:
            pending["coins"] = pending.get("coins", 0) + coins
        for k, v in items.items():
            pending["items"][k] = pending["items"].get(k, 0) + v
        user_data["pending_adventure_rewards"] = pending

        # Losing outcome -> immediate end, clear pending and stop (no Continue)
        if outcome["result"].lower() in ["lose everything", "lose inventory item"]:
            user_data["adventure_failed"] = True
            user_data["pending_adventure_rewards"] = None
            user_data["next_scenario_id"] = None

            text = (
                f"*{scenario['scenario']}*\n"
                f"> *Your pick: {choice['option']}\n"
                f"> *Outcome: {outcome['result']}\n"
                f"{outcome['reaction']}\n\n"
                f"💀 *Adventure ended.*"
            )
            if query.message.photo:
                await query.edit_message_caption(text, parse_mode="Markdown")
            else:
                await query.edit_message_text(text, parse_mode="Markdown")
            return

        # End safely is now a successful scenario result but DOES NOT end the entire adventure.
        # It simply counts as a successful outcome for this scenario and allows continuation.
        # Therefore treat it like any non-ending outcome (do not finalize).
        if outcome["result"].lower() == "end safely":
            # keep pending as-is (already added), do NOT finalize the run
            user_data["adventure_failed"] = user_data.get("adventure_failed", False)
            # schedule next scenario
            user_data["next_scenario_id"] = sid + 1

            text = (
                f"*{scenario['scenario']}*\n"
                f"> *Your pick: {choice['option']}\n"
                f"> *Outcome: {outcome['result']}\n"
                f"{outcome['reaction']}\n\n"
            )

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("➡️ Continue", callback_data="adv_continue")]
            ])

            if query.message.photo:
                await query.edit_message_caption(text, parse_mode="Markdown", reply_markup=keyboard)
            else:
                await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)
            return

        # Non-ending regular outcome -> schedule next scenario and show Continue
        user_data["next_scenario_id"] = sid + 1

        text = (
            f"*{scenario['scenario']}*\n"
            f"> *Your pick: {choice['option']}\n"
            f"> *Outcome: {outcome['result']}\n"
            f"{outcome['reaction']}"
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("➡️ Continue", callback_data="adv_continue")]
        ])

        if query.message.photo:
            await query.edit_message_caption(text, parse_mode="Markdown", reply_markup=keyboard)
        else:
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)
        return

    # fallback invalid format
    if query.message.photo:
        await query.edit_message_caption("❌ Invalid adventure choice format.")
    else:
        await query.edit_message_text("❌ Invalid adventure choice format.")
    return
async def pets_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_data
    user_id = str(update.effective_user.id)
    args = context.args if hasattr(context, "args") else []

    # ✅ Handle "/pets shop"
    if args and args[0].lower() == "shop":
        await pets_shop_logic(update, context)
        return

    # ✅ Handle "/pets buy [pet name]"
    if args and args[0].lower() == "buy":
        pet_name = " ".join(args[1:]).strip()
        with open("pets.json", "r", encoding="utf-8") as f:
            pet_data = json.load(f)

        pet = next((p for p in pet_data if p["name"].lower() == pet_name.lower()), None)

        if not pet:
            await update.message.reply_text(f"❌ Pet '{pet_name}' not found.")
            return

        friendly = pet.get("friendly_with", [])
        hostile = pet.get("hostile_with", [])

        caption = (
            f"🐾 *{pet['name']}*\n"
            f"💰 Price: {pet['price']}\n"
            f"🤝 Friendly with: {', '.join(friendly)}\n"
            f"⚔️ Hostile with: {', '.join(hostile)}"
        )

        image_path = pet.get("link")

        keyboard = [
            [
                InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_buy:{pet['name']}"),
                InlineKeyboardButton("❌ Cancel", callback_data="cancel_buy")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if user_id not in user_data:
            user_data[user_id] = {}

        user_data[user_id]["confirmationType"] = "pet"
        user_data[user_id]["pendingPet"] = pet["name"]

        try:
            if image_path.startswith("http"):
                response = requests.get(image_path)
                response.raise_for_status()
                image_bytes = BytesIO(response.content)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=image_bytes,
                    caption=caption,
                    parse_mode="Markdown",
                    reply_markup=reply_markup
                )
            elif os.path.exists(image_path):
                with open(image_path, "rb") as image_file:
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=image_file,
                        caption=caption,
                        parse_mode="Markdown",
                        reply_markup=reply_markup
                    )
            else:
                await update.message.reply_text(caption)
        except Exception:
            await update.message.reply_text(caption)
        return

    # ✅ Default response for plain "/pets"
    await update.message.reply_text(
        "🐾 Use `/pets shop` to view the pet shop or `/pets buy [pet name]` to adopt a pet.",
        parse_mode=ParseMode.MARKDOWN
    )

async def pets_shop_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.forward_message(
            chat_id=update.effective_chat.id,
            from_chat_id=-1003059305242,  # Correct format for private channels
            message_id=4
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Could not forward message: {e}")
# ==========================
# 🛍️ inv format
# ==========================
def format_inventory(inv):
    items = []
    pets = []

    for key, count in inv.items():
        if key in PET_KEYS:
            pets.append(f"{key} x{count}")
        else:
            items.append(f"{key} x{count}")

    result = "items (with emoji):\n"
    result += "\n".join(items) if items else "None"
    result += "\n-------------------\n"
    result += "pets:\n"
    result += "\n".join(pets) if pets else "None"
    return result

# ==========================
# 🛍️ Shop Items
# ==========================

def load_shop_items():
    with open(SHOP_ITEMS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def normalize(text):
    return re.sub(r'\W+', '', text).lower()
# ==========================
# 🚀 xp function
# ==========================
def xp_required_for_level(level):
    if level <= 10:
        return level * 100
    elif level <= 100:
        return 1000 + (level - 10) * 250
    else:
        return 1000 + (90 * 250) + (level - 100) * 500
# ==========================
# 🚀 xp add function
# ==========================
async def add_xp(user_id, command_name, update=None, context=None):

    balances = load_balances()
    user = balances.get(user_id)
    if not user:
        return

    # Ensure required fields exist
    user.setdefault("xp", 0)
    user.setdefault("level", 1)
    user.setdefault("coin", 0)
    user.setdefault("inventory", {})
    user.setdefault("titles", [])

    xp_gain = COMMAND_XP_VALUES.get(command_name, 0)
    user["xp"] += xp_gain

    previous_level = user["level"]
    leveled_up = False
    level_up_messages = []

    while user["xp"] >= xp_required_for_level(user["level"]):
        user["xp"] -= xp_required_for_level(user["level"])
        user["level"] += 1
        leveled_up = True

        rewards = load_level_rewards().get(str(user["level"]), [])
        coin_reward = 0
        item_rewards = []

        for reward in rewards:
            if reward.startswith("⏣"):
                amount = int(reward.replace("⏣", "").replace(",", "").strip())
                user["coin"] += amount
                coin_reward += amount
            elif reward.startswith("Title:"):
                title = reward.replace("Title:", "").strip()
                user["titles"].append(title)
            elif "x" in reward:
                count, item_name = reward.split("x", 1)
                item_key = normalize(item_name.strip())
                user["inventory"].setdefault(item_key, 0)
                user["inventory"][item_key] += int(count.strip())
                item_rewards.append(f"{count.strip()}x {item_name.strip()}")

        # Build level-up message
        message = f"🎉 *Level Up!* You reached level {user['level']}!\n"
        if coin_reward:
            message += f"🪙 {coin_reward:,} coins have been added to your inventory.\n"
        if item_rewards:
            message += f"🎁 Items received: {', '.join(item_rewards)}"
        level_up_messages.append(message)

    save_balances(balances)

    # Send level-up messages
    if leveled_up and update and context:
        for msg in level_up_messages:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=msg,
                parse_mode=ParseMode.MARKDOWN
            )
# ==========================
# 🚀 xp progress
# ==========================
def xp_progress_bar(current, required, length=20):
    filled = int((current / required) * length)
    empty = length - filled
    return f"[{'█' * filled}{'░' * empty}]"

# ==========================
# 🚀 /start Command
# ==========================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    balances = load_balances()
    username = update.effective_user.username

    if username:
        cache = load_user_cache()
        cache[username] = user_id
        save_user_cache(cache)
    if user_id not in balances:
        balances[user_id] = {
            "coin": STARTING_Coin,
            "bank": 0,
            "xp": 0,
            "level": 1,
            "inventory": {}
        }

        save_balances(balances)
        await update.message.reply_text(
            "Welcome to DankMemer Bot! 💸 100,000 coins have been added to your pocket."
        )
    else:
        await update.message.reply_text("You've already started your journey!")
# ==========================
# 💰 /rob command
# ==========================


async def rob_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    robber_id = str(update.effective_user.id)
    if update.message.reply_to_message:
        target_id = str(update.message.reply_to_message.from_user.id)
    elif context.args:
        username = context.args[0].lstrip("@")
        cache = load_user_cache()
        target_id = cache.get(username)

        if not target_id:
            await update.message.reply_text(
                "❌ Couldn't find that username in the cache. Make sure they've used /start.")
            return



    else:
        await update.message.reply_text(
            "❌ You must reply to a user's message or tag their user ID. Example: /rob <user_id>")
        return
    balances = load_balances()

    robber = balances.get(robber_id)

    target = balances.get(target_id)

    if not target:
        await update.message.reply_text("❌ Target user not found.")
        return

    robber_inv = robber.get("inventory", {})
    target_inv = target.get("inventory", {})
    if target["coin"] <= 0:
        await update.message.reply_text("💸 That user has no coins to steal.")
        return

    # Check for padlock
    if "padlock" in target_inv:
        if "cutters" not in robber_inv:
            await update.message.reply_text(
                "🔒 The target had a padlock and you don't have a bolt cutter. Robbery failed.")
            return

    # Check for landmine
    if "landmine" in target_inv and random.random() < 0.3:
        await update.message.reply_text("💥 You triggered a landmine and exploded. Robbery failed.")
        return
    has_pet = any(key in target_inv for key in PET_KEYS)
    if has_pet and random.random() < 0.33:
        fine = random.randint(100, 5200)
        robber["coin"] = max(0, robber.get("coin", 0) - fine)
        await update.message.reply_text(
            f"🏥 You were hospitalized by their pet!\nYou lost ⏣ {fine:,} coins."
        )
        save_balances(balances)
        return
    # Random failure chance
    # Apply item effects
    rob_boost = context.user_data.get("rob_boost", {})
    rob_vulnerability = context.user_data.get("rob_vulnerability", {})
    rob_multiplier = 1.0
    success_bonus = 0.0

    if rob_boost and time.time() < rob_boost.get("expires", 0):
        rob_multiplier = rob_boost.get("multiplier", 1.0)
        success_bonus += (rob_multiplier - 1.0)

    if rob_vulnerability and time.time() < rob_vulnerability.get("expires", 0):
        # You are more vulnerable to being robbed (if you were the target)
        pass  # You can use this in reverse logic if you implement rob defense later

    # Adjust success chance
    roll = random.random()
    adjusted_roll = roll - success_bonus

    roll = random.random()

    if adjusted_roll < 0.20:
        fail_reactions = load_fail_reactions()
        fail = random.choice(fail_reactions)
        fine = random.randint(100, 500)
        robber["coin"] = max(0, robber.get("coin", 0) - fine)

        if fail["gif"].endswith((".gif", ".mp4")):
            await update.message.reply_animation(
                animation=fail["gif"],
                caption=f"{fail['text']}\nYou lost ⏣ {fine:,} coins."
            )
        else:
            await update.message.reply_photo(
                photo=fail["gif"],
                caption=f"{fail['text']}\nYou lost ⏣ {fine:,} coins."
            )

        save_balances(balances)
        return
    elif adjusted_roll < 0.50:
        percent = 0.10
        msg = "🤏 You stole a TINY portion!"
    elif adjusted_roll < 0.85:
        percent = 0.15
        msg = "💸 You stole a small portion!"
    elif adjusted_roll < 0.95:
        percent = 0.30
        msg = "💰 You stole a fairly decent chunk!"
    else:
        percent = 0.50
        msg = "🤑 You stole BASICALLY EVERYTHING YOU POSSIBLY COULD LMFAO!"
    stolen = max(1, int(target["coin"] * percent * rob_multiplier))

    drop = int(stolen * random.uniform(0, 0.08))  # 0–8% drop
    final_gain = stolen - drop

    target["coin"] -= stolen
    robber["coin"] += final_gain

    caption = (
        f"{msg}\n"
        f"You stole ⏣ {stolen:,} coins.\n"
        f"You dropped ⏣ {drop:,} coins.\n"
        f"Final gain: ⏣ {final_gain:,} coins."
    )

    await update.message.reply_animation(
        animation="https://static.wikia.nocookie.net/dank_memer/images/a/a9/Pepe_rob_command.gif/revision/latest?cb=20240304115419",
        caption=caption
    )



    await add_xp(robber_id, "Rob", update, context)
    save_balances(balances)
# ==========================
# 💰 /balance Command
# ==========================

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    await add_xp(user_id, "Balance", update, context)

    balances = load_balances()

    if user_id not in balances:
        await update.message.reply_text("Use /start to begin!")
        return
    user = balances[user_id]
    level = user.get("level", 1)
    xp = user.get("xp", 0)
    xp_needed = xp_required_for_level(level)
    progress_bar = xp_progress_bar(xp, xp_needed)
    bank = user["bank"]
    coin = user["coin"]
    bank = balances[user_id].get("bank", 0)
    max_capacity = balances[user_id].get("bank_capacity", BANK_CAPACITY)
    level = balances[user_id].get("level", 1)
    xp = balances[user_id].get("xp", 0)
    xp_needed = level * 100
    bank = balances[user_id].get("bank", 0)
    max_capacity = balances[user_id].get("bank_capacity", BANK_CAPACITY)
    coin = balances[user_id].get("coin", 0)
    # XP progress bar
    bar_width = 20
    filled = int((xp / xp_needed) * bar_width)
    bar = "█" * filled + "░" * (bar_width - filled)
    await update.message.reply_text(
        f"💰 Coin: ⏣ {coin:,}\n"
        f"🏦 Bank: ⏣ {bank:,} / {max_capacity:,}\n"
        f"📈 Level: {level}\n"
        f"🔢 XP: {xp:,} / {xp_needed:,}\n"
        f"[{bar}]"
    )



# ==========================
# 📥 /deposit Command
# ==========================

async def deposit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    now = time.time()
    await add_xp(user_id, "Deposit", update, context)

    balances = load_balances()

    # Check cooldown
    last_time = last_deposit_time.get(user_id, 0)
    if now - last_time < COOLDOWN_SECONDS:
        remaining = int(COOLDOWN_SECONDS - (now - last_time))
        await update.message.reply_text(f"⏳ Please wait {remaining} seconds before depositing again.")
        return

    last_deposit_time[user_id] = now  # Update timestamp

    await add_xp(user_id, "Deposit", update, context)

    await add_xp(user_id, "Deposit", update, context)
    balances = load_balances()
    if user_id not in balances:
        await update.message.reply_text("Use /start to begin!")
        return

    try:
        amount = int(context.args[0])
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /deposit <amount>")
        return

    coin = balances[user_id]["coin"]
    bank = balances[user_id]["bank"]

    if amount > coin:
        await update.message.reply_text("❌ You don't have enough coin!")
    max_capacity = balances[user_id].get("bank_capacity", BANK_CAPACITY)
    if bank + amount > max_capacity:

        await update.message.reply_text("❌ Bank capacity exceeded!")
    else:
        balances[user_id]["coin"] -= amount
        balances[user_id]["bank"] += amount
        save_balances(balances)
        await update.message.reply_text(f"✅ Deposited {amount:,} coins to your bank.")

# ==========================
# 📤 /withdraw Command
# ==========================

async def withdraw_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    now = time.time()
    balances = load_balances()
    last_time = last_withdraw_time.get(user_id, 0)
    if now - last_time < COOLDOWN_SECONDS:
        remaining = int(COOLDOWN_SECONDS - (now - last_time))
        await update.message.reply_text(f"⏳ Please wait {remaining} seconds before withdrawing again.")
        return

    last_withdraw_time[user_id] = now  # Update timestamp
    if user_id not in balances:
        await update.message.reply_text("Use /start to begin!")
        return

    try:
        amount = int(context.args[0])
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /withdraw <amount>")
        return

    bank = balances[user_id]["bank"]

    if amount > bank:
        await update.message.reply_text("❌ You don't have enough in the bank!")
    else:
        balances[user_id]["coin"] += amount
        balances[user_id]["bank"] -= amount
        save_balances(balances)
        await update.message.reply_text(f"✅ Withdrew {amount:,} coins from your bank.")

# ==========================
# 🛒 /shop Command
# ==========================

async def shop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    source_chat_id = -1003059305242  # Full channel ID
    message_ids = [4, 3]  # Messages to forward

    for msg_id in message_ids:
        await context.bot.forward_message(
            chat_id=chat_id,
            from_chat_id=source_chat_id,
            message_id=msg_id
        )

# ==========================
# 🛍️ /buy Command
# ==========================

async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_data
    user_id = str(update.effective_user.id)
    balances = load_balances()
    items = load_shop_items()

    if user_id not in balances:
        await update.message.reply_text("Use /start to begin!")
        return

    if not context.args:
        await update.message.reply_text("Usage: /buy <item or pet name>")
        return

    query = normalize(" ".join(context.args))

    # 🔍 Try matching shop item first
    matched_item = next((i for i in items if normalize(i["itemKey"]) == query or normalize(i["name"]) == query), None)

    if matched_item:
        price = matched_item["value"]
        if balances[user_id]["coin"] < price:
            await update.message.reply_text("❌ You don't have enough coins to buy this item.")
            return

        name = matched_item["name"]
        rarity = matched_item.get("rarity", "Unknown")
        flags = matched_item.get("flags", {})
        flags_text = ", ".join([f for f, v in flags.items() if v]) or "None"
        image_path = os.path.join(ITEM_IMAGE_FOLDER, f"{matched_item['itemKey']}.png")

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_buy:{matched_item['itemKey']}"),
                InlineKeyboardButton("❌ Cancel", callback_data="cancel_buy")
            ]
        ])

        if not os.path.exists(image_path):
            await update.message.reply_text(f"❌ Image not found for item: {matched_item['itemKey']}")
            return

        try:
            await update.message.reply_photo(
                photo=open(image_path, "rb"),
                caption=(
                    f"🛒 {name}\n"
                    f"💵 Price: {price:,}\n"
                    f"🧬 Rarity: {rarity}\n"
                    f"🏷️ Flags: {flags_text}\n\n"
                    f"📜 Description: {matched_item.get('description', 'No description.')}\n"
                    f"🧪 Use: {matched_item.get('longDescription', 'No effect.')}"
                ),
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to send item image: {e}")
            return

        # ✅ Save confirmation context
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]["confirmationType"] = "shop"
        user_data[user_id]["pendingItem"] = matched_item["itemKey"]
        return

    # 🐾 Try matching pet
    with open("pets.json", "r", encoding="utf-8") as f:
        pet_data = json.load(f)

    matched_pet = next((p for p in pet_data if normalize(p["name"]) == query), None)

    if matched_pet:
        friendly = matched_pet.get("friendly_with", [])
        hostile = matched_pet.get("hostile_with", [])
        caption = (
            f"🐾 *{matched_pet['name']}*\n"
            f"💰 Price: {matched_pet['price']}\n"
            f"🤝 Friendly with: {', '.join(friendly)}\n"
            f"⚔️ Hostile with: {', '.join(hostile)}"
        )

        image_path = matched_pet.get("link")
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_buy:{matched_pet['name']}"),
                InlineKeyboardButton("❌ Cancel", callback_data="cancel_buy")
            ]
        ])

        try:
            if image_path.startswith("http"):
                response = requests.get(image_path)
                response.raise_for_status()
                image_bytes = BytesIO(response.content)
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=image_bytes,
                    caption=caption,
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
            elif os.path.exists(image_path):
                with open(image_path, "rb") as image_file:
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=image_file,
                        caption=caption,
                        parse_mode="Markdown",
                        reply_markup=keyboard
                    )
            else:
                await update.message.reply_text(caption, reply_markup=keyboard)
        except Exception:
            await update.message.reply_text(caption, reply_markup=keyboard)

        # ✅ Save confirmation context
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]["confirmationType"] = "pet"
        user_data[user_id]["pendingPet"] = matched_pet["name"]
        return

    # ❌ Nothing matched
    await update.message.reply_text("❌ Item or pet not found.")

# ==========================
# ✅ Inventory Command
# ==========================
with open(r"C:\Users\Administrator\Desktop\TelegramBot\power-up.json", "r", encoding="utf-8") as f:
    powerups = json.load(f)
with open(r"C:\Users\Administrator\Desktop\TelegramBot\sellable.json", "r", encoding="utf-8") as f:
    sellables = json.load(f)
# Which keys to show on Page 0 under “Tools”
def build_inventory_page(page, inventory, context):
    shop_items = context.bot_data.get("shop_items", [])
    fish_keys = context.bot_data.get("fish_keys", set())
    hunt_keys = {r[0] for r in HUNT_REWARDS if r[0] != "fail"}
    dig_keys = {r[0] for r in DIG_REWARDS if r[0] != "fail"}

    shop_keys = {normalize(i["itemKey"]) for i in shop_items}
    fish_keys = {normalize(k) for k in fish_keys}
    hunt_keys = {normalize(k) for k in hunt_keys}
    dig_keys = {normalize(k) for k in dig_keys}
    pet_keys = {normalize(k) for k in PET_KEYS}

    emoji_map = {
        # 🛍️ Shop
        "padlock": "🔐", "shovel": "⛏️", "cutters": "✂️", "newplayerpack": "🎁",
        "huntingrifle": "🏹", "fishingpole": "🎣",

        # 🐟 Fish
        "starfish": "⭐🐠", "boxfish": "📦🐠", "shrimp": "🍤", "jellyfish": "🪼",
        "butterflyfish": "🦋🐠", "whiteperch": "⚪🐟", "bluetang": "🔵🐠",
        "bluegill": "🔷🐟", "yellowperch": "🟡🐟",

        # 🏹 Hunt
        "boar": "🐗", "skunk": "🦨", "deer": "🦌",

        # ⛏️ Dig
        "ant": "🐜", "fossil": "🦴", "banknote": "💵", "garbage": "🗑️",

        # 📦 Others
        "ammo": "🔫", "pepe": "🐸", "cat": "🐱", "eyeballbait": "👁️🪱",
        "luckybait": "🍀🪱", "magnetbait": "🧲🪱", "xpbait": "📚🪱",
        "dynamite": "🧨", "weightedbait": "⚖️🪱", "adventurecompass": "🧭",

        # 🐾 Pets
        "axolotl": "🦎", "birb": "🐦", "bunny": "🐰", "catgirl": "😺",
        "crab": "🦀", "dog": "🐶", "duck": "🦆", "fox": "🦊", "hamster": "🐹",
        "kraken": "🦑", "monkey": "🐒", "pandabear": "🐼", "rock": "🪨", "turtle": "🐢"
    }

    sections = {
        "🛍️ *Shop Items:*": [],
        "🐟 *Fish:*": [],
        "🏹 *Hunt Items:*": [],
        "⛏️ *Dig Items:*": [],
        "🐾 *Pets:*": [],
        "📦 *Others:*": []
    }

    for key, count in inventory.items():
        norm_key = normalize(key)
        emoji = emoji_map.get(norm_key, "📦")
        line = f"{emoji} {key.title()} x{count}"

        if norm_key in shop_keys:
            sections["🛍️ *Shop Items:*"].append(line)
        elif norm_key in fish_keys:
            sections["🐟 *Fish:*"].append(line)
        elif norm_key in hunt_keys:
            sections["🏹 *Hunt Items:*"].append(line)
        elif norm_key in dig_keys:
            sections["⛏️ *Dig Items:*"].append(line)
        elif norm_key in pet_keys:
            sections["🐾 *Pets:*"].append(line)
        else:
            sections["📦 *Others:*"].append(line)

    # Pagination: page 0 = Shop, Fish, Hunt; page 1 = Dig, Pets, Others
    if page == 0:
        selected = ["🛍️ *Shop Items:*", "🐟 *Fish:*", "🏹 *Hunt Items:*"]
    else:
        selected = ["⛏️ *Dig Items:*", "🐾 *Pets:*", "📦 *Others:*"]

    output = [f"{title}\n" + "\n".join(sections[title]) for title in selected if sections[title]]
    return "\n\n".join(output) if output else "📭 Your inventory is empty."

async def inventory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    balances = load_balances()
    inventory = balances.get(user_id, {}).get("inventory", {})

    text = build_inventory_page(0, inventory, context)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Next ▶️", callback_data="inventory_page_1")]
    ])
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")

async def inventory_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, _, page_str = query.data.split("_")
    page = int(page_str)

    user_id = str(query.from_user.id)
    balances = load_balances()
    inventory = balances.get(user_id, {}).get("inventory", {})

    text = build_inventory_page(page, inventory, context)

    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton("◀️ Previous", callback_data=f"inventory_page_{page - 1}"))
    if page < 1:
        buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"inventory_page_{page + 1}"))

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([buttons]), parse_mode="Markdown")
# ==========================
# ✅ use command
# ==========================
async def use_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    await add_xp(user_id, "Use", update, context)

    balances = load_balances()
    powerups = json.load(open("power-up.json", "r", encoding="utf-8"))
    consumables = json.load(open("consumable.json", "r", encoding="utf-8"))

    if user_id not in balances:
        await update.message.reply_text("Use /start to begin!")
        return

    if not context.args:
        await update.message.reply_text("Usage: /use <item name>")
        return

    query = normalize(" ".join(context.args))
    all_items = powerups + consumables
    matched_item = None

    for item in all_items:
        keys = [
            normalize(item["name"]),
            normalize(item["itemKey"]),
        ]
        if query in keys:
            matched_item = item
            break

    if not matched_item:
        await update.message.reply_text("❌ Item not found or not usable.")
        return

    # Skip unusable power-ups
    if matched_item["type"] == "Power-up" and matched_item["itemKey"] in ["lifesaver", "poster", "collar"]:
        await update.message.reply_text("❌ This item cannot be used directly.")
        return

    inventory = balances[user_id].get("inventory", {})
    item_key = matched_item["itemKey"]
    if inventory.get(item_key, 0) < 1:
        await update.message.reply_text("❌ You don't own this item.")
        return

    # Show confirmation
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Use", callback_data=f"use_confirm:{item_key}"),
         InlineKeyboardButton("❌ Cancel", callback_data="use_cancel")]
    ])

    await update.message.reply_photo(
        photo=open(os.path.join(ITEM_IMAGE_FOLDER, f"{item_key}.png"), "rb"),
        caption=(
            f"🛒 {matched_item['name']}\n"
            f"🧬 Rarity: {matched_item.get('rarity', 'Unknown')}\n"
            f"📜 Description: {matched_item.get('description', 'No description.')}\n"
            f"🧪 Use: {matched_item.get('longDescription', 'No effect.')}"
        ),
        reply_markup=keyboard
    )

# ==========================
# ✅ Buy Confirmation Handler
# ==========================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_data
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    balances = load_balances()
    items = load_shop_items()

    if user_id not in balances:
        await query.edit_message_text("Use /start to begin!")
        return

    if query.data == "cancel_buy":
        await query.edit_message_caption("❌ Purchase cancelled.")
        return

    if query.data == "use_cancel":
        await query.edit_message_caption("❌ Use cancelled.")
        return

    if query.data.startswith("use_confirm:"):
        item_key = query.data.split(":")[1]
        all_items = json.load(open("power-up.json", "r", encoding="utf-8")) + json.load(
            open("consumable.json", "r", encoding="utf-8"))
        item = next((i for i in all_items if i["itemKey"] == item_key), None)

        if not item:
            await query.edit_message_caption("❌ Item not found.")
            return

        inventory = balances[user_id].get("inventory", {})
        if inventory.get(item_key, 0) < 1:
            await query.edit_message_caption("❌ You don't own this item.")
            return

        inventory[item_key] -= 1
        if inventory[item_key] == 0:
            del inventory[item_key]
        save_balances(balances)
        effect_text = ""

        if item_key == "banknote":
            balances[user_id]["bank_capacity"] = balances[user_id].get("bank_capacity", BANK_CAPACITY) + 2500
            save_balances(balances)
            effect_text = "🏦 Your bank capacity increased by 2,500 coins!"

        elif item_key == "pizza":
            context.user_data["xp_boost"] = {"multiplier": 2.5, "expires": time.time() + 1800}
            effect_text = "🍕 You gained a 2.5x XP boost for 30 minutes!"

        elif item_key == "cupidsbigtoe":
            context.user_data["beg_boost"] = {"multiplier": 1.69, "expires": time.time() + 69}
            context.user_data["rob_boost"] = {"multiplier": 1.69, "expires": time.time() + 69}
            effect_text = "💘 69% boost for begging and robbing for 69 seconds!"

        elif item_key == "ammo":
            context.user_data["hunt_protection"] = time.time() + 3600
            effect_text = "🔫 Your hunts won't fail for 1 hour!"

        elif item_key == "alcohol":
            context.user_data["rob_boost"] = {"multiplier": 1.15, "expires": time.time() + 3600}
            context.user_data["rob_vulnerability"] = {"multiplier": 1.15, "expires": time.time() + 3600}
            if random.random() < 0.10:
                original_coin = balances[user_id].get("coin", 0)
                balances[user_id]["coin"] = int(original_coin * 0.7)
                balances[user_id]["bank"] = 0
                effect_text = (
                    "☠️ You died from alcohol poisoning!\n"
                    f"💸 You lost 30% of your wallet and your bank was wiped out."
                )

            else:
                effect_text = "🍺 15% robbery boost, but you're easier to rob!"

        elif item_key == "whiskey":
            context.user_data["rob_boost"] = {"multiplier": 1.10, "expires": time.time() + 3600}
            effect_text = "🥃 10% robbery boost for 1 hour!"

        await query.edit_message_caption(
            f"✅ You used {item['name']}!\n\n🧪 Effect: {effect_text or item['longDescription']}")

        return

    if query.data.startswith("confirm_buy:"):
        item_key = query.data.split(":", 1)[1]

        if user_id not in user_data:
            await query.edit_message_caption("❌ No pending purchase found.")
            return

        confirmation_type = user_data[user_id].get("confirmationType")

        if confirmation_type == "shop":
            matched_item = next((i for i in items if normalize(i["itemKey"]) == normalize(item_key)), None)
            if not matched_item:
                await query.edit_message_caption("❌ Item not found.")
                return

            price = matched_item["value"]
            if balances[user_id]["coin"] < price:
                await query.edit_message_caption("❌ You don't have enough coins to buy this item.")
                return

            balances[user_id]["coin"] -= price
            inventory = balances[user_id].setdefault("inventory", {})
            inventory[item_key] = inventory.get(item_key, 0) + 1
            save_balances(balances)

            await query.edit_message_caption(
                f"✅ You have successfully purchased *{matched_item['name']}*!",
                parse_mode=ParseMode.MARKDOWN
            )

        elif confirmation_type == "pet":
            with open("pets.json", "r", encoding="utf-8") as f:
                pet_data = json.load(f)

            pet = next((p for p in pet_data if normalize(p["name"]) == normalize(item_key)), None)
            if not pet:
                await query.edit_message_caption("❌ Pet not found.")
                return

            price_str = pet["price"]
            price_clean = re.sub(r"[^\d]", "", price_str)
            price = int(price_clean) if price_clean else 0

            if balances[user_id]["coin"] < price:
                await query.edit_message_caption("❌ You don't have enough coins to buy this pet.")
                return

            balances[user_id]["coin"] -= price
            inventory = balances[user_id].setdefault("inventory", {})
            pet_key = item_key.lower()
            inventory[pet_key] = inventory.get(pet_key, 0) + 1
            save_balances(balances)

            await query.edit_message_caption(
                f"✅ You have successfully adopted *{pet['name']}*!",
                parse_mode=ParseMode.MARKDOWN
            )

        else:
            await query.edit_message_caption("❌ No pending purchase to confirm.")
            return

        # ✅ Cleanup
        user_data[user_id]["confirmationType"] = None
        user_data[user_id]["pendingItem"] = None
        user_data[user_id]["pendingPet"] = None


async def give_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Owner-only: reply to someone and use /give <amount> to add coins to their wallet."""
    # verify owner
    sender = update.effective_user
    if not sender or (sender.username or "").lower() != OWNER_USERNAME.lower():
        return await update.message.reply_text("❌ You are not authorized to use this command.")

    # must be a reply
    if not update.message.reply_to_message:
        return await update.message.reply_text("Usage: reply to a user's message, then send /give <amount>.")

    # parse amount
    args = context.args or []
    if not args:
        return await update.message.reply_text("Usage: /give <amount> (reply to target user)")
    try:
        amount = int(args[0])
        if amount <= 0:
            raise ValueError()
    except Exception:
        return await update.message.reply_text("❌ Please provide a valid positive integer amount.")

    # target user id and balances
    target_user = update.message.reply_to_message.from_user
    if not target_user:
        return await update.message.reply_text("❌ Could not determine target user from reply.")
    target_id = str(target_user.id)

    balances = load_balances()
    balances.setdefault(target_id, {"coin": 0, "bank": 0, "xp": 0, "level": 1, "inventory": {}})

    before = balances[target_id].get("coin", 0)
    balances[target_id]["coin"] = before + amount
    save_balances(balances)

    # audit log (append)
    try:
        with open("admin_give_log.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.utcnow().isoformat()}Z\towner:@{sender.username}\tto:{target_id}(@{target_user.username or 'unknown'})\tamount:{amount}\n")
    except Exception:
        pass

    # notify
    await update.message.reply_text(f"✅ Gave ⏣ {amount:,} to {target_user.full_name} (ID {target_id}).")
    try:
        await context.bot.send_message(chat_id=target_user.id, text=f"🎁 You received ⏣ {amount:,} from the bot owner.")
    except Exception:
        # if DM fails (privacy settings), ignore silently
        pass
# ==========================
# 🚦 Bot Initialization
# ==========================
async def cancel_gamble(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("❌ Gambling cancelled.")
    return ConversationHandler.END

def main():
    from commands2 import beg_command
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    load_bot_data(app)
    from telegram.ext import MessageHandler, filters
    app.add_error_handler(error_handler)  # ✅ Register here
    # Core commands
    from commands2 import heist_message_collector
    gamble_handler = ConversationHandler(
        entry_points=[CommandHandler("gamble", gamble_command)],
        states={
            GAMBLE_CHOICE: [CallbackQueryHandler(handle_gamble_choice)],
            GAMBLE_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_gamble_amount)],
            GAMBLE_ROULETTE: [CallbackQueryHandler(handle_roulette_logic)],
            GAMBLE_BLACKJACK: [
                CallbackQueryHandler(handle_blackjack_hit, pattern="^blackjack_hit$"),
                CallbackQueryHandler(handle_blackjack_stand, pattern="^blackjack_stand$"),
                CallbackQueryHandler(handle_blackjack_double, pattern="^blackjack_double$")  # if you added this
            ],
            GAMBLE_DICE: [
                CallbackQueryHandler(handle_dice_logic, pattern="^dice_"),
                CallbackQueryHandler(handle_slots_callback, pattern="^slots_"),
                CallbackQueryHandler(handle_slots_callback, pattern="^slots_spin$")
            ],

        },
        fallbacks=[CallbackQueryHandler(cancel_gamble, pattern="^gamble_cancel$")],

    per_message=False  # or True if you're using only CallbackQueryHandlers
    )

    app.add_handler(gamble_handler)
    app.add_handler(CommandHandler("crime", crime_command))
    app.add_handler(CallbackQueryHandler(crime_callback, pattern="^crime_"))
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("balance", balance_command))
    app.add_handler(CommandHandler("deposit", deposit_command))
    app.add_handler(CommandHandler("withdraw", withdraw_command))
    app.add_handler(CommandHandler("inventory", inventory_command))
    app.add_handler(CommandHandler("use", use_command))
    app.add_handler(CommandHandler("rob", rob_command))
    app.add_handler(CommandHandler("beg", beg_command))
    app.add_handler(CommandHandler("give", give_command))
    # Shop and buying
    app.add_handler(CallbackQueryHandler(handle_slots_callback, pattern="^slots_"))
    # Also allow catching "slots_spin" exact
    app.add_handler(CallbackQueryHandler(handle_slots_callback, pattern="^slots_spin$"))
    app.add_handler(CommandHandler("adventure", adventure_command))
    app.add_handler(CallbackQueryHandler(adventure_callback, pattern="^adv_"))
    app.add_handler(CommandHandler("shop", shop_command))
    app.add_handler(CommandHandler("buy", buy_command))
    #work fish
    app.add_handler(CommandHandler("work", work_command))
    app.add_handler(CommandHandler("daily", daily_command))
    app.add_handler(CommandHandler("profile", profile_command))
    app.add_handler(CommandHandler("setbalance", setbalance_command))
    app.add_handler(CommandHandler("take", take_command))
    app.add_handler(CommandHandler("rollback", rollback_command))
    #pets
    app.add_handler(CommandHandler("pets", pets_command))
    app.add_handler(CommandHandler("sell", sell_command))

    app.add_handler(CallbackQueryHandler(confirm_sell_callback, pattern=r"^confirm_sell:"))
    app.add_handler(CallbackQueryHandler(cancel_sell_callback, pattern=r"^cancel_sell$"))
    app.add_handler(
        CallbackQueryHandler(inventory_page_callback,
                             pattern=r"^inventory_page_[01]$")
    )
    # Heist feature

    app.add_handler(CallbackQueryHandler(handle_cast_fish, pattern="^cast_fish_"))
    app.add_handler(CallbackQueryHandler(handle_hunt, pattern="^work:hunt$"))
    app.add_handler(CallbackQueryHandler(handle_work_choice, pattern="^work_"))
    app.add_handler(CallbackQueryHandler(handle_fish_navigation, pattern="^fish_"))
    app.add_handler(CallbackQueryHandler(handle_callback))
    print("🤖 Bot is running...")
    app.run_polling()




if __name__ == "__main__":
    main()
