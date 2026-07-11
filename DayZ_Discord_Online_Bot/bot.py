import asyncio
import json
import os
from datetime import datetime

import a2s
import discord
from dotenv import load_dotenv


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "OnlineBot_Config.json")


def load_config():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError("OnlineBot_Config.json not found.")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    instance = data.get("instances", [{}])[0]
    if not instance:
        raise ValueError("Invalid config: instances[0] missing.")
    return instance


def to_activity_type(value):
    mapping = {
        "PLAYING": discord.ActivityType.playing,
        "STREAMING": discord.ActivityType.streaming,
        "LISTENING": discord.ActivityType.listening,
        "WATCHING": discord.ActivityType.watching,
        "COMPETING": discord.ActivityType.competing,
    }
    return mapping.get(str(value or "PLAYING").upper(), discord.ActivityType.playing)


def get_daytime_emoji(emojis):
    hour = datetime.now().hour
    return emojis.get("day", "☀️") if 7 <= hour < 20 else emojis.get("night", "🌙")


def now_hhmm():
    return datetime.now().strftime("%H:%M")


def format_template(template, payload):
    return (
        str(template or "")
        .replace("${online}", str(payload["online"]))
        .replace("${max}", str(payload["max"]))
        .replace("${queue}", str(payload["queue"]))
        .replace("${time}", str(payload["time"]))
        .replace("${emoji.player}", str(payload["emoji"].get("player", "")))
        .replace("${emoji.day}", str(payload["emoji"].get("day", "")))
        .replace("${emoji.night}", str(payload["emoji"].get("night", "")))
        .replace("${emoji.queue}", str(payload["emoji"].get("queue", "")))
        .replace("${emoji.daytime}", str(payload["emoji"].get("daytime", "")))
        .replace("${status.queueBlock}", str(payload["status"].get("queueBlock", "")))
    )


async def query_dayz(server_ip, query_port):
    def _query():
        info = a2s.info((server_ip, query_port), timeout=4.0)
        players = a2s.players((server_ip, query_port), timeout=4.0)
        return info, players

    info, players = await asyncio.wait_for(asyncio.to_thread(_query), timeout=8.0)

    info_count = int(getattr(info, "player_count", 0) or 0)
    players_count = len(players or [])
    online = min(info_count, players_count) if players_count > 0 else info_count
    max_players = int(getattr(info, "max_players", 0) or 0)
    return max(0, online), max_players, 0


class DayzStatusBot(discord.Client):
    def __init__(self, instance):
        intents = discord.Intents.none()
        intents.guilds = True
        super().__init__(intents=intents)
        self.instance = instance
        self.status_cfg = instance.get("status", {})
        self.server_cfg = instance.get("server", {})
        self.emoji_cfg = instance.get("emojis", {})
        self.interval_seconds = int(instance.get("updater", {}).get("intervalSeconds", 30))

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        while True:
            await self.update_presence()
            await asyncio.sleep(self.interval_seconds)

    async def update_presence(self):
        server_ip = self.server_cfg.get("ip")
        query_port = int(self.server_cfg.get("steamQueryPort") or self.server_cfg.get("port") or 0)
        if not server_ip or not query_port:
            print("[ERROR] Invalid server config: need server.ip and server.port/steamQueryPort.")
            return

        activity_type = to_activity_type(self.status_cfg.get("activityType"))

        try:
            online, max_players, queue = await query_dayz(server_ip, query_port)
            queue_block = ""
            if queue > 0 or self.status_cfg.get("showQueueIfNotActive", False):
                queue_block = format_template(
                    self.status_cfg.get("queueBlock", ""),
                    {
                        "online": online,
                        "max": max_players,
                        "queue": queue,
                        "time": now_hhmm(),
                        "emoji": {
                            "player": self.emoji_cfg.get("player"),
                            "day": self.emoji_cfg.get("day"),
                            "night": self.emoji_cfg.get("night"),
                            "queue": self.emoji_cfg.get("queue"),
                            "daytime": get_daytime_emoji(self.emoji_cfg),
                        },
                        "status": {"queueBlock": ""},
                    },
                )

            message = format_template(
                self.status_cfg.get("message", "${online}/${max}"),
                {
                    "online": online,
                    "max": max_players,
                    "queue": queue,
                    "time": now_hhmm(),
                    "emoji": {
                        "player": self.emoji_cfg.get("player"),
                        "day": self.emoji_cfg.get("day"),
                        "night": self.emoji_cfg.get("night"),
                        "queue": self.emoji_cfg.get("queue"),
                        "daytime": get_daytime_emoji(self.emoji_cfg),
                    },
                    "status": {"queueBlock": queue_block},
                },
            ).strip() or f"{online}/{max_players}"

            await self.change_presence(
                status=discord.Status.online,
                activity=discord.Activity(type=activity_type, name=message),
            )
            print(f"[OK] {message}")
        except Exception as exc:
            offline = self.status_cfg.get("serverOfflineMessage", "Server offline")
            await self.change_presence(
                status=discord.Status.idle,
                activity=discord.Activity(type=activity_type, name=offline),
            )
            print(f"[OFFLINE] {offline} :: {exc}")


def main():
    load_dotenv()
    instance = load_config()
    token = os.getenv("DISCORD_TOKEN") or instance.get("discord", {}).get("token")
    if not token:
        raise RuntimeError("DISCORD_TOKEN not found (.env) and discord.token in config is empty.")

    bot = DayzStatusBot(instance)
    bot.run(token)


if __name__ == "__main__":
    main()
