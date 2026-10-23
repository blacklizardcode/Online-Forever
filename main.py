import asyncio
import json
import requests
import websockets
import os

TOKEN = os.getenv("DISCORD_TOKEN")                         # Your discord token.
STATUS = os.getenv("DISCORD_STATUS") or "online"           # online / dnd / idle
STATUS_MESSAGE = os.getenv("DISCORD_STATUS_MESSAGE") or "" # Leave empty if you don't want a custom status.
USE_EMOJI = os.getenv("DISCORD_EMOJI") or False            # Enable the use of an emoji in the status.

activity = {
    "name": "Custom Status",
    "type": 4,
    "state": STATUS_MESSAGE,
    "id": "custom"
}

if USE_EMOJI:
    activity["emoji"] = {
        "name": os.getenv("DISCORD_EMOJI_NAME") or "🔥",    # Unicode emoji or emoji name.
        "id": os.getenv("DISCORD_EMOJI_ID") or None,        # Required only for custom emojis.
        "animated": os.getenv("DISCORD_EMOJI_ANIMATED") or False
    }

r = requests.get("https://discord.com/api/v10/users/@me", headers={"Authorization": TOKEN})
if r.status_code != 200:
    print(f"An error occured, code: {r.status_code}")
    exit()

user = r.json()
print(f"Logged in as {user['username']} ({user['id']})!")

async def discord_gateway():
    uri = "wss://gateway.discord.gg/?v=10&encoding=json"

    async with websockets.connect(uri) as ws:
        hello = json.loads(await ws.recv())
        heartbeat_interval = hello["d"]["heartbeat_interval"]

        async def heartbeat():
            while True:
                await asyncio.sleep(heartbeat_interval / 1000)
                await ws.send(json.dumps({"op": 1, "d": None}))

        asyncio.create_task(heartbeat())

        identify = {
            "op": 2,
            "d": {
                "token": TOKEN,
                "properties": {
                    "$os": "windows",
                    "$browser": "chrome",
                    "$device": "pc"
                },
                "presence": {
                    "status": STATUS,
                    "afk": False,
                    "activities": [activity]
                }
            }
        }
        await ws.send(json.dumps(identify))

        while True:
            try:
                msg = await ws.recv()
                data = json.loads(msg)

                if data.get("op") == 11:
                    pass

            except Exception as e:
                print("Connection lost, reconnecting...", e)
                break

if __name__ == "__main__":
    while True:
        try:
            asyncio.run(discord_gateway())
        except Exception as e:
            print("Gateway error:", e)

        import time
        time.sleep(5)