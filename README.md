# 📅 Discord Event Sync Bot

This is a simple, one-way Discord bot that syncs upcoming events from a JSON API to your Discord server as scheduled events. It ensures no duplicates, tracks updates, and respects Discord rate limits.

---

## 🚀 Features

- Pulls events from a secured JSON API with a bearer token  
- Automatically creates new events in your Discord server  
- Detects and updates existing events if key fields change  
- Only creates the next upcoming instance of recurring events  
- Prunes expired events from the internal registry  
- Smart logging with rate limit visibility  

---

## ⚙️ Setup Instructions

### 1. Clone the Project

```bash
git clone https://github.com/yourusername/discord-event-sync-bot.git
cd discord-event-sync-bot
```

---

### 2. Install Dependencies

We recommend using [Poetry](https://python-poetry.org/) for managing dependencies.

```bash
poetry install
```

Or use `pip` if you're not using Poetry:

```bash
pip install -r requirements.txt
```

---

### 3. Create a Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)  
2. Click **“New Application”**  
3. Give your app a name and click **Create**  
4. In the left menu, go to **“Bot”**  
5. Click **“Add Bot”** and confirm  

#### Get the Bot Token

- Under the **Bot** tab, click **“Reset Token”** and **Copy** the token  
- Store it in your `.env` file (see below)  

#### Set Permissions

1. Go to **OAuth2 > URL Generator**  
2. Select:  
   - **Scopes**: `bot`  
   - **Bot Permissions**:  
     - `Manage Events`
     - `Create Events`  
3. Copy the generated URL and use it to **invite the bot to your server**  

---

### 4. Enable Developer Mode & Get Your Server (Guild) ID

1. In Discord, go to **User Settings > Advanced**  
2. Toggle **Developer Mode** ON  
3. Right-click your **server icon**, and click **"Copy ID"**  
4. Store that ID in your `.env` file  

---

### 5. Create `.env` File

Create a `.env` file in your project root:

```
DISCORD_TOKEN=your-bot-token-here
DISCORD_GUILD_ID=your-discord-server-id
EVENTS_API_URL=https://upcomingactions.americanmanifesto.news/api/events
EVENTS_API_BEARER=your-bearer-token-for-api
```

---

### 6. Run the Bot

Using Poetry:

```bash
poetry run python bot.py
```

Using plain Python:

```bash
python bot.py
```

---

## 📁 Project Files

- `bot.py` — the main sync bot  
- `created_events.json` — local registry of all events synced to Discord (Make sure to backup and restore this file if reinstalling the bot. Failing to do so will likely result in duplication of events) 
- `.env` — stores your secrets (not included in version control)  

---

## 🧠 Notes

- This bot assumes your API returns **individual event instances**, even for recurring events.  
- It uses the combination of `start|end|location` to uniquely identify events.  
- It updates events only if their summary, description, or link change.  
- Discord API does not support recurring scheduled events — each recurrence must be posted as a separate scheduled event.  

---

## 📜 License

MIT — use freely, improve widely.
