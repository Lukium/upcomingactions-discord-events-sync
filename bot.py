"""Discord Bot for Event Syncing"""

import asyncio  # pylint: disable=unused-import
import json
import logging
import os
from collections import defaultdict
from datetime import datetime, timezone
from hashlib import sha256

import discord
import aiohttp
from discord.ext import tasks, commands
from dotenv import load_dotenv


class DiscordHttpFilter(logging.Filter):
    """Filter to suppress verbose HTTP requests in Discord.py."""

    def filter(self, record):
        msg = str(record.getMessage())
        # Suppress verbose HTTP requests (POST/GET)
        if msg.startswith("POST") or msg.startswith("GET"):
            return False
        # Allow all other messages (including rate limit warnings)
        return True


# Set up root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Configure discord.http separately
http_logger = logging.getLogger("discord.http")
http_logger.setLevel(logging.DEBUG)
http_logger.propagate = False  # prevent double logging

# Add filtered console output
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.addFilter(DiscordHttpFilter())

http_logger.addHandler(console_handler)


# Load .env config
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))
EVENTS_API_URL = os.getenv("EVENTS_API_URL")
EVENTS_API_BEARER = os.getenv("EVENTS_API_BEARER")
REGISTRY_FILE = "created_events.json"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


# Utility: Generate a unique ID for the event
def generate_event_id(event):
    """Generate a unique ID for the event based on its details."""
    base = f"{event['start']}|{event['end']}|{event['location']}"
    return sha256(base.encode()).hexdigest()


# Utility: Load event registry
def load_registry():
    """Load the event registry from a JSON file."""
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# Utility: Save event registry
def save_registry(registry):
    """Save the event registry to a JSON file."""
    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)


# Utility: Clean up past events
def prune_old_events(registry):
    """Remove events from the registry that have already ended."""
    now = datetime.now(timezone.utc)
    to_delete = []
    for uid, evt in registry.items():
        end = datetime.fromisoformat(evt["end"]).astimezone(timezone.utc)
        if end < now:
            to_delete.append(uid)
    for uid in to_delete:
        del registry[uid]


# Main Sync Logic
@tasks.loop(minutes=15)
async def sync_events():
    print("🔄 Checking for new/updated events...")
    registry = load_registry()
    prune_old_events(registry)
    headers = {"Authorization": f"Bearer {EVENTS_API_BEARER}"}

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(EVENTS_API_URL) as resp:
            if resp.status != 200:
                print(f"❌ Failed to fetch events: {resp.status}")
                return
            all_events = await resp.json()

    # Filter: Only keep first upcoming instance for each recurring_id
    seen = set()
    filtered = []
    now = datetime.now(timezone.utc)

    for event in sorted(all_events, key=lambda e: e["start"]):
        start_dt = datetime.fromisoformat(event["start"]).astimezone(
            timezone.utc
        )
        if start_dt < now:
            continue  # Skip past events

        rid = event.get("recurring_id")
        if rid and rid in seen:
            continue  # Only process one per recurring series
        if rid:
            seen.add(rid)

        filtered.append(event)

    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print("❌ Guild not found.")
        return

    for event in filtered:
        uid = generate_event_id(event)
        start = datetime.fromisoformat(event["start"]).astimezone(timezone.utc)
        end = datetime.fromisoformat(event["end"]).astimezone(timezone.utc)
        summary = event["summary"]
        description = (event.get("description") or "").strip()
        link = event.get("link")
        location = event.get("location") or "TBA"

        # 🔧 New: Prepend link to the top of the description
        if link:
            description = f"{link}\n\n{description}"

        existing = registry.get(uid)
        if existing:
            needs_update = (
                existing["summary"] != summary
                or existing["description"] != description
                or existing.get("link") != link
            )
            if needs_update:
                try:
                    discord_event = await guild.fetch_scheduled_event(
                        existing["discord_event_id"]
                    )
                    await discord_event.edit(
                        name=summary, description=description[:1000]
                    )
                    print(f"✅ Updated event: {summary}")
                    registry[uid] = {
                        "start": event["start"],
                        "end": event["end"],
                        "location": location,
                        "summary": summary,
                        "description": description,
                        "link": link,
                        "discord_event_id": discord_event.id,
                    }
                    save_registry(registry)
                except Exception as e:
                    print(
                        f"⚠️ Failed to update event '{summary}': {e}",
                        flush=True,
                    )
            continue

        # Create new event
        try:
            new_event = await guild.create_scheduled_event(
                name=summary,
                description=description[:1000],
                start_time=start,
                end_time=end,
                location=location,
                entity_type=discord.EntityType.external,
                privacy_level=discord.PrivacyLevel.guild_only,
            )
            print(f"🆕 Created new event: {summary}")
            registry[uid] = {
                "start": event["start"],
                "end": event["end"],
                "location": location,
                "summary": summary,
                "description": description,
                "link": link,
                "discord_event_id": new_event.id,
            }
            save_registry(registry)

        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = getattr(e, "retry_after", "unknown")
                print(
                    f"⚠️ Rate limited. Retry after {retry_after} seconds.",
                    flush=True,
                )
            else:
                print(
                    f"❌ Discord HTTP error while creating '{summary}': {e}",
                    flush=True,
                )
        except Exception as e:
            print(
                f"❌ Unexpected error while creating '{summary}': {e}",
                flush=True,
            )

    save_registry(registry)


@bot.event
async def on_ready():
    """Called when the bot is ready."""
    print(f"✅ Bot connected as {bot.user}")
    sync_events.start()


if __name__ == "__main__":
    bot.run(TOKEN)
