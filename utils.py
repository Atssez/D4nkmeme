import json
import os
import unicodedata
import time
from datetime import datetime
import random
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes

BALANCES_FILE = "balances.json"
SHOP_ITEMS_FILE = "shop_items.json"
ITEM_EMOJI_FILE = "item_emojis.json"
LEVEL_REWARDS_FILE = "level_rewards.json"

user_data = {}

# -----------------------
# Basic storage helpers
# -----------------------
def load_balances():
    if not os.path.exists(BALANCES_FILE):
        return {}
    with open(BALANCES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_balances(balances):
    with open(BALANCES_FILE, "w", encoding="utf-8") as f:
        json.dump(balances, f, indent=4)

def load_shop_items():
    if not os.path.exists(SHOP_ITEMS_FILE):
        return []
    with open(SHOP_ITEMS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_item_emojis_by_name():
    if not os.path.exists(ITEM_EMOJI_FILE):
        return {}
    with open(ITEM_EMOJI_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# -----------------------
# Normalization helpers
# -----------------------
def normalize(text):
    if not isinstance(text, str):
        return ""
    return unicodedata.normalize("NFKD", text).casefold().strip()

# -----------------------
# Player helpers
# -----------------------
def get_player_coins(user_id):
    balances = load_balances()
    return balances.get(user_id, {}).get("coin", 0)

def change_player_coins(user_id, amount):
    balances = load_balances()
    balances.setdefault(user_id, {}).setdefault("coin", 0)
    balances[user_id]["coin"] += amount
    save_balances(balances)

def add_to_inventory(user_id, item_key):
    balances = load_balances()
    inv = balances.setdefault(user_id, {}).setdefault("inventory", {})
    inv[item_key] = inv.get(item_key, 0) + 1
    save_balances(balances)

def remove_from_inventory(user_id, item_key):
    balances = load_balances()
    inv = balances.setdefault(user_id, {}).setdefault("inventory", {})
    if item_key in inv:
        inv[item_key] -= 1
        if inv[item_key] <= 0:
            del inv[item_key]
    save_balances(balances)

# -----------------------
# NPC mood
# -----------------------
def adjust_npc_mood(context, user_id, npc_name, change):
    current = context.bot_data.get("npc_moods", {}).get(user_id, {}).get(npc_name, 0)
    new_mood = max(-2, min(1, current + change))
    context.bot_data.setdefault("npc_moods", {}).setdefault(user_id, {})[npc_name] = new_mood
    return new_mood

# -----------------------
# Leveling helpers
# -----------------------
def xp_required_for_level(level: int) -> int:
    if level <= 10:
        return level * 100
    if level <= 100:
        return 1000 + (level - 10) * 250
    return 1000 + (90 * 250) + (level - 100) * 500

def load_level_rewards():
    if not os.path.exists(LEVEL_REWARDS_FILE):
        return {}
    try:
        with open(LEVEL_REWARDS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("levelRewards", {}) if isinstance(data, dict) else {}
    except Exception:
        return {}

# -----------------------
# XP awarding (safe)
# -----------------------
async def add_xp(user_id: str, command_name: str,
                 update: Optional[Update]=None,
                 context: Optional[ContextTypes.DEFAULT_TYPE]=None):
    balances = load_balances()
    user = balances.get(user_id)
    if user is None:
        return

    user.setdefault("xp", 0)
    user.setdefault("level", 1)
    user.setdefault("coin", 0)
    user.setdefault("inventory", {})
    user.setdefault("titles", [])

    # try to read COMMAND_XP_VALUES from telegram_bot (avoid circular import)
    xp_gain = 0
    try:
        import telegram_bot as tb
        xp_gain = getattr(tb, "COMMAND_XP_VALUES", {}).get(command_name, 0)
    except Exception:
        xp_gain = 0

    user["xp"] += xp_gain

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
            if isinstance(reward, str) and reward.startswith("⏣"):
                try:
                    amt = int(reward.replace("⏣", "").replace(",", "").strip())
                    user["coin"] = user.get("coin", 0) + amt
                    coin_reward += amt
                except Exception:
                    pass
            elif isinstance(reward, str) and reward.startswith("Title:"):
                title = reward.replace("Title:", "").strip()
                user.setdefault("titles", []).append(title)
            elif isinstance(reward, str) and "x" in reward:
                try:
                    cnt, item_name = reward.split("x", 1)
                    item_key = normalize(item_name.strip())
                    user.setdefault("inventory", {}).setdefault(item_key, 0)
                    user["inventory"][item_key] += int(cnt.strip())
                    item_rewards.append(f"{cnt.strip()}x {item_name.strip()}")
                except Exception:
                    pass

        message = f"🎉 Level Up! You reached level {user['level']}!"
        if coin_reward:
            message += f"\n🪙 {coin_reward:,} coins added."
        if item_rewards:
            message += f"\n🎁 Items: {', '.join(item_rewards)}"
        level_up_messages.append(message)

    save_balances(balances)

    if leveled_up and update and context:
        for msg in level_up_messages:
            try:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode="Markdown")
            except Exception:
                pass
