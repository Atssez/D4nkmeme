# 🐸 D4nkmeme

A **Telegram economy and gaming bot inspired by Dank Memer**, built in Python.

D4nkmeme recreates many of the systems that make economy bots fun: earning and spending coins, collecting items, gambling, pets, fishing, hunting, digging, adventures, XP and levels, crime, robbery, daily rewards, and more.

> **Disclaimer:** This is an unofficial fan-made project inspired by Dank Memer. It is not affiliated with, endorsed by, or connected to Dank Memer or its developers.

---

## ✨ Features

### 💰 Economy System

D4nkmeme includes a persistent economy where every player has their own balance, bank, inventory, XP, level, and other account information.

Players can:

- Earn coins
- Deposit coins into their bank
- Withdraw coins
- Spend coins in the shop
- Buy and sell items
- Give coins to other users
- Rob other players
- Earn daily rewards
- Lose or gain money through gambling and crime

Player data is stored locally using JSON files.

---

## 🎒 Inventory & Items

Players can collect and use many different kinds of items.

The project contains separate data files for categories such as:

- Consumables
- Collectables
- Sellable items
- Power-ups
- Tools
- Loot boxes
- Packs
- Pets
- Fishing equipment
- Fishing bait

Items can have their own:

- Name
- Emoji
- Price
- Effects
- Sell value
- Rarity
- Usage behavior

The inventory system keeps track of item quantities for each player.

---

## 🛒 Shop

The bot includes a shop system where players can browse and purchase items using their coins.

Main shop commands include:

```text
/shop
/buy
/sell
```

Shop and item information is primarily stored in:

```text
shop_items.json
sellable.json
consumable.json
collectable.json
power-up.json
tool.json
pack.json
loot box.json
```

---

## 🎰 Gambling / Casino

D4nkmeme contains an interactive casino system.

Available games include:

### 🎡 Roulette

Bet coins and try your luck at roulette.

### 🃏 Blackjack

Play blackjack using interactive Telegram buttons, including actions such as:

- Hit
- Stand
- Double

### 🎲 Dice

Place a bet and gamble using dice.

### 🎰 Slots

Spin a slot machine and try to win coins.

Start the casino with:

```text
/gamble
```

The gambling system also tracks daily wins and can apply daily casino restrictions.

---

## 🧑‍🌾 Work System

The `/work` command opens an interactive work menu.

Available jobs include:

```text
🎣 Fish
⛏️ Dig
🏹 Hunt
```

### 🎣 Fishing

Fishing is one of the larger systems in the project.

Players can:

- Own fishing equipment
- Choose fishing locations
- Cast a fishing line
- Catch different fish
- Fail to catch anything
- Collect catches in their inventory

Fishing data is stored inside the `data/` directory, including:

```text
data/fish_loc.json
data/fish_baits.json
data/fishing_tools.json
data/fish_npc.json
data/fish_fishes/
```

Different fishing locations and fish can have their own properties and values.

A fishing pole is required before a player can fish.

### ⛏️ Digging

Players can dig for random rewards.

Possible results include valuable items, common items, or complete failure.

### 🏹 Hunting

Players can hunt animals and other random rewards.

Possible results include things such as:

```text
Boar
Deer
Duck
Rabbit
Skunk
```

...along with rarer or joke outcomes.

---

## 🚀 Adventure System

D4nkmeme contains an interactive adventure system with different scenarios and choices.

Start an adventure with:

```text
/adventure
```

Players progress through scenarios using Telegram inline buttons.

Choices can lead to:

- Coins
- Items
- Successful outcomes
- Failed outcomes
- Losing rewards
- Continuing deeper into the adventure

The project includes adventures such as:

```text
🌌 Pepe Goes To Space
🤠 Pepe Goes Out West
```

Adventure scenarios are primarily driven using JSON data, making them easier to expand without rewriting the entire bot.

---

## 🐾 Pets

The project contains a pet system with multiple pets that players can browse and purchase.

Examples include:

```text
Axolotl
Birb
Bunny
Cat
Catgirl
Crab
Dog
Duck
Fox
Hamster
Kraken
Monkey
Panda Bear
Pepe
Rock
Turtle
```

Pet commands include:

```text
/pets
/pets shop
/pets buy <pet name>
```

Pet information is stored in:

```text
pets.json
```

Pets can contain information such as their price, image, characteristics, and relationships with other pets.

---

## 🦹 Crime & Robbery

Players do not have to earn their money honestly.

### Crime

```text
/crime
```

The crime command provides interactive crime choices with different possible outcomes.

### Robbery

```text
/rob
```

Players can attempt to steal money from other users.

Both systems introduce risk into the economy instead of making earning coins completely predictable.

---

## 🙏 Begging

Players who need some quick money can use:

```text
/beg
```

The command can succeed or fail and includes randomized responses.

---

## 📅 Daily Rewards

Players can claim rewards with:

```text
/daily
```

This provides another way to build an economy balance over time.

---

## ⭐ XP & Leveling

D4nkmeme contains an XP and leveling system.

Different commands award different amounts of XP.

Examples include:

```text
Balance
Deposit
Inventory
Shop
Use
Rob
Beg
Gamble
Adventure
```

As users gain enough XP, they level up.

Leveling can unlock rewards such as:

- 🪙 Coins
- 🎁 Items
- 🏷️ Titles

Level rewards are configured in:

```text
level_rewards.json
```

This allows progression rewards to be changed without hardcoding every reward into the bot.

---

## 👤 Profiles

Players can view their account/progression information with:

```text
/profile
```

Account information can include things such as:

- Coins
- Level
- XP
- Titles
- Inventory/progression information

---

## 📜 Commands

The bot currently registers the following main commands:

| Command | Description |
|---|---|
| `/start` | Create/start your player account |
| `/balance` | Check your money |
| `/deposit` | Deposit money into your bank |
| `/withdraw` | Withdraw money from your bank |
| `/inventory` | View your inventory |
| `/shop` | Open/view the shop |
| `/buy` | Purchase an item |
| `/sell` | Sell inventory items |
| `/use` | Use an item |
| `/beg` | Beg for coins |
| `/daily` | Claim a daily reward |
| `/work` | Fish, dig, or hunt |
| `/crime` | Attempt a crime |
| `/rob` | Attempt to rob another player |
| `/gamble` | Open the casino |
| `/adventure` | Start an interactive adventure |
| `/pets` | Access the pet system |
| `/profile` | View your profile |
| `/give` | Owner/admin coin-giving command |
| `/setbalance` | Admin balance command |
| `/take` | Admin command for removing assets/balance |
| `/rollback` | Admin rollback functionality |

Some commands use **Telegram inline keyboards**, so interactions continue through buttons rather than additional commands.

---

# 🗂️ Project Structure

A simplified overview of the repository:

```text
D4nkmeme/
│
├── telegram_bot.py
│   └── Main Telegram bot, commands, handlers and initialization
│
├── commands2.py
│   └── Additional commands and game systems
│
├── utils.py
│   └── Shared utility, economy, inventory and leveling functions
│
├── balances.json
│   └── Player/economy database
│
├── shop_items.json
├── pets.json
├── item_effects.json
├── level_rewards.json
├── consumable.json
├── collectable.json
├── sellable.json
├── power-up.json
├── tool.json
├── pack.json
├── loot box.json
├── use_items.json
├── xp_multipliers.json
│
├── data/
│   ├── fish_loc.json
│   ├── fish_baits.json
│   ├── fishing_tools.json
│   ├── fish_npc.json
│   ├── fish_fishes/
│   └── pepe_adventure.json
│
├── petspic/
├── petspic_resized/
├── picture_renamed/
│
├── transactions.log
├── admin_give_log.txt
└── user_cache.json
```

---

# 🛠️ Built With

The project is primarily built with:

- **Python**
- **python-telegram-bot**
- **Telegram Bot API**
- **JSON** for local data persistence
- **Requests** for retrieving external images/resources

The bot uses asynchronous Telegram handlers and inline callback buttons for many interactive features.

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone https://github.com/Atssez/D4nkmeme.git
cd D4nkmeme
```

---

## 2. Create a virtual environment

Recommended:

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install dependencies

At minimum, the project uses packages including:

```bash
pip install python-telegram-bot requests
```

For a cleaner project setup, create a `requirements.txt` and install dependencies with:

```bash
pip install -r requirements.txt
```

---

# 🔐 Bot Token Setup

**Never commit your Telegram bot token to GitHub.**

Create a bot through Telegram's **@BotFather**, obtain your bot token, and keep it outside of your source code.

A recommended setup is to use an environment variable.

Instead of:

```python
BOT_TOKEN = "YOUR_TOKEN"
```

use:

```python
BOT_TOKEN = os.getenv("BOT_TOKEN")
```

Then provide the token before starting the bot.

### Windows PowerShell

```powershell
$env:BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
python telegram_bot.py
```

### Linux / macOS

```bash
export BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
python telegram_bot.py
```

You can also use a `.env` file with a package such as `python-dotenv`.

Example:

```env
BOT_TOKEN=your_token_here
```

Make sure `.env` is included in `.gitignore`.

```gitignore
.env
__pycache__/
*.pyc
.venv/
venv/
```

---

# ▶️ Running the Bot

After installing the dependencies and configuring your token:

```bash
python telegram_bot.py
```

If everything loads correctly, the application starts Telegram polling and the bot begins accepting commands.

Open your bot on Telegram and run:

```text
/start
```

---

# ⚠️ Current Development Notes

This repository was originally developed as a personal project, so some parts are currently tied to the original development environment.

In particular, some code contains absolute Windows paths similar to:

```text
C:\Users\...\Desktop\TelegramBot\...
```

For example, some adventure images and item resources may reference local paths.

If you clone the project onto another computer, these paths should be converted to project-relative paths.

Instead of:

```python
image = r"C:\Users\...\TelegramBot\data\image.png"
```

prefer:

```python
image = os.path.join("data", "image.png")
```

or:

```python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
image = os.path.join(BASE_DIR, "data", "image.png")
```

This is one of the main improvements needed before the project is fully portable.

---

# 💾 Data Storage

D4nkmeme currently uses JSON files as its main database/storage system.

For example:

```text
balances.json
```

stores persistent player information.

The project also includes transaction logging and user cache files.

JSON is convenient for a smaller personal project because the data can easily be inspected and modified manually.

For a larger deployment, a database such as one of the following would be a better long-term solution:

```text
SQLite
PostgreSQL
MongoDB
```

---

# 🛡️ Security

If you fork or deploy this project:

**Do not expose your Telegram bot token.**

Secrets should be stored in environment variables and excluded using `.gitignore`.

If a token has ever been publicly committed, simply removing it from the current file is **not enough**.

You should:

1. Revoke the exposed token.
2. Generate a new token.
3. Store the new token securely.
4. Remove the old secret from Git history if necessary.

Also avoid committing production player databases such as:

```text
balances.json
user_cache.json
transactions.log
admin_give_log.txt
```

if they contain real user information.

---

# 👑 Admin Commands

The bot contains owner/admin functionality such as:

```text
/give
/setbalance
/take
/rollback
```

These commands should remain restricted to the bot owner or trusted administrators.

Never rely only on hiding an admin command from the command list as a security mechanism.

Always validate the Telegram user ID or another trusted identifier before performing privileged operations.

---

# 🧠 How It Works

At a high level:

```text
Telegram User
     │
     ▼
Telegram Bot API
     │
     ▼
telegram_bot.py
     │
     ├── Command handlers
     ├── Callback handlers
     ├── Adventure system
     ├── Economy commands
     └── Bot initialization
             │
             ▼
        commands2.py
             │
             ├── Work system
             ├── Fishing
             ├── Hunting
             ├── Digging
             ├── Gambling
             ├── Crime
             ├── Daily rewards
             └── Other game logic
             │
             ▼
          utils.py
             │
             ├── Balance helpers
             ├── Inventory helpers
             ├── XP helpers
             └── JSON loading/saving
             │
             ▼
          JSON Data
```

---

# 🗺️ Possible Future Improvements

There are many directions this project could be taken.

Some useful improvements would be:

- [ ] Move the bot token completely to environment variables
- [ ] Remove machine-specific absolute file paths
- [ ] Add `requirements.txt`
- [ ] Add `.gitignore`
- [ ] Move player data from JSON to SQLite/PostgreSQL
- [ ] Separate commands into Telegram bot cogs/modules
- [ ] Add automated tests
- [ ] Improve exception handling
- [ ] Add structured logging
- [ ] Add configuration files
- [ ] Add achievements
- [ ] Expand adventures
- [ ] Add more pets
- [ ] Add more fishing locations and fish
- [ ] Add item rarity tiers
- [ ] Add leaderboards
- [ ] Add trading between users
- [ ] Add more casino games
- [ ] Add cooldown management
- [ ] Add proper database migrations
- [ ] Dockerize the bot
- [ ] Add deployment documentation

---

# 🤝 Contributing

Contributions, improvements, and bug fixes are welcome.

If you would like to contribute:

```bash
# Fork the repository

git clone <your-fork>

cd D4nkmeme

git checkout -b feature/my-feature
```

Make your changes and commit them:

```bash
git add .
git commit -m "Add my feature"
git push origin feature/my-feature
```

Then open a Pull Request.

When contributing, please avoid committing:

- Bot tokens
- API keys
- Personal credentials
- Production player data
- Machine-specific file paths

---

# 🐛 Bugs & Issues

This project was built as a personal recreation/learning project and may contain unfinished systems, duplicated code, hardcoded paths, or bugs.

If you find an issue, feel free to open a GitHub Issue with:

- What you were trying to do
- What happened
- What you expected to happen
- Any console traceback
- Steps to reproduce the problem

---

# 🎯 Purpose

D4nkmeme was created as a programming project to recreate and experiment with the mechanics of an economy/game bot using Python and Telegram.

It explores concepts including:

- Asynchronous programming
- Telegram bot development
- Callback queries
- Interactive UI buttons
- Persistent data
- JSON
- Economy design
- Inventory systems
- Randomized game mechanics
- XP and leveling systems
- Cooldowns
- Gambling mechanics
- Game state
- User progression

---

# 📄 License

No license is currently included in this repository.

If you want other people to legally use, modify, and redistribute the project, consider adding an open-source license such as the **MIT License**.

Until a license is added, normal copyright rules apply.

---

# 👨‍💻 Author

Created by **Atssez**

GitHub: [@Atssez](https://github.com/Atssez)

Repository: [D4nkmeme](https://github.com/Atssez/D4nkmeme)

---

## ⭐ Support

If you found the project interesting, consider leaving a ⭐ on the repository.

---

<p align="center">
  🐸 <b>D4nkmeme</b><br>
  A Dank Memer-inspired economy & gaming bot for Telegram.
</p>
