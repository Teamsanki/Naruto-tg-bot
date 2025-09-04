import asyncio
import os
import aiohttp
from pyrogram import Client, filters
from pytgcalls import PyTgCalls, idle
from pytgcalls.types.input_stream import AudioVideoPiped  # ✅ Updated import
from dotenv import load_dotenv

# ----------------- Load ENV -----------------
load_dotenv()

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
USER_STRING_SESSION = os.getenv("USER_STRING_SESSION", "")
FIREBASE_URL = os.getenv("FIREBASE_URL", "")
API_KEY = os.getenv("API_KEY", "")

if not all([API_ID, API_HASH, BOT_TOKEN, USER_STRING_SESSION]):
    raise SystemExit("❌ Missing config. Please set environment variables properly.")

# ----------------- Firebase Anime API Resolver -----------------
async def anime_api_resolve(query: str):
    if not FIREBASE_URL:
        raise ValueError("FIREBASE_URL missing in env")

    url = f"{FIREBASE_URL}/anime.json?auth={API_KEY}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Firebase API error: {resp.status}")
            data = await resp.json()

    for name, item in data.items():
        if query.lower() in name.lower():
            return item.get("video_url"), item.get("title", name)

    raise ValueError(f"No result found for {query}")

# ----------------- Pyrogram Clients -----------------
app = Client(
    "anime-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

user = Client(
    "anime-user",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=USER_STRING_SESSION,
)

call = PyTgCalls(user)

# ----------------- Command Handlers -----------------
@app.on_message(filters.command("play") & filters.group)
async def play_video(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: `/play naruto 27`", quote=True)

    query = " ".join(message.command[1:])
    try:
        video_url, title = await anime_api_resolve(query)
    except Exception as e:
        return await message.reply(f"⚠️ Error: {e}")

    chat_id = message.chat.id

    try:
        await call.join_group_call(
            chat_id,
            AudioVideoPiped(
                video_url,
            )
        )
        await message.reply(f"▶️ **Playing:** `{title}`", quote=True)
    except Exception as e:
        await message.reply(f"⚠️ Failed to join VC: {e}")

# ----------------- Speed Command -----------------
@app.on_message(filters.command("speed") & filters.group)
async def change_speed(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: `/speed 1.5`", quote=True)
    try:
        speed = float(message.command[1])
        # ⚡ Placeholder: FFmpeg filter for speed is advanced, coming soon
        await message.reply(f"⚡ Video speed set to {speed}x (Feature Coming Soon!)", quote=True)
    except:
        await message.reply("⚠️ Invalid speed value!", quote=True)

# ----------------- Startup -----------------
async def main():
    await app.start()
    await user.start()
    await call.start()
    print("✅ Bot Started!")
    await idle()
    await app.stop()
    await user.stop()

if __name__ == "__main__":
    asyncio.run(main())
