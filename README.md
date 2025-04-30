# 📅 Discord Event Sync Bot

This is a simple, one-way Discord bot that syncs upcoming events from Lukium’s Maryland-area pro-democracy JSON API into your Discord server as scheduled events. It avoids duplicates, updates existing events when details change, and respects Discord rate limits.

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

Tested on Python 3.11 and 3.12

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

## ✅ Expected API response

- start and end must be ISO 8601 formatted strings with timezone offset.
- recurring_id must be present even for non-recurring events to allow deduplication.
- link, description, and location can be null or empty, but are preferred for richer Discord event data.

```json
[
  {
    "summary": "Example Event One",
    "description": "This is a description of the event.",
    "start": "2025-06-01T10:00:00-04:00",
    "end": "2025-06-01T12:00:00-04:00",
    "location": "123 Main St, Hometown, ST",
    "link": "https://example.org/event/1",
    "is_recurring": false,
    "recurring_id": "abc123",
    "recurrence": null,
    "same_day": true
  },
  {
    "summary": "Example Weekly Rally",
    "description": "Join us for a recurring weekly rally.",
    "start": "2025-06-03T17:00:00-04:00",
    "end": "2025-06-03T18:00:00-04:00",
    "location": "Central Park, Hometown, ST",
    "link": "https://example.org/event/2",
    "is_recurring": true,
    "recurring_id": "weekly456",
    "recurrence": ["RRULE:FREQ=WEEKLY;BYDAY=TU"],
    "same_day": true
  },
  {
    "summary": "Community Meeting",
    "description": "",
    "start": "2025-06-05T19:00:00-04:00",
    "end": "2025-06-05T20:30:00-04:00",
    "location": "Library Hall, 456 Elm St, Hometown, ST",
    "link": null,
    "is_recurring": false,
    "recurring_id": "mtg789",
    "recurrence": null,
    "same_day": true
  }
]
```


## 🧠 Notes

- This bot assumes your API returns **individual event instances**, even for recurring events.  
- It uses the combination of `start|end|location` to uniquely identify events.  
- It updates events only if their summary, description, or link change.  
- Discord API does not support recurring scheduled events — each recurrence must be posted as a separate scheduled event.  

---

## 📜 License

MIT — use freely, improve widely.
