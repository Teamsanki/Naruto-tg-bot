import asyncio
import os
import aiohttp
from pyrogram import Client, filters
from pytgcalls import PyTgCalls, idle
from pytgcalls.types.input_stream import AudioVideoPiped
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
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

# ----------------- /play command -----------------
@app.on_message(filters.command("play") & filters.group)
async def play_command(client, message):
    try:
        # Firebase se anime list fetch
        url = f"{FIREBASE_URL}/anime.json?auth={API_KEY}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
    except Exception as e:
        return await message.reply(f"⚠️ Failed to fetch anime list: {e}")

    if not data:
        return await message.reply("⚠️ No anime available!")

    # Inline buttons for all anime
    buttons = []
    for name in data.keys():
        buttons.append([InlineKeyboardButton(name, callback_data=f"play:{name}")])

    await message.reply(
        "🎬 **Available Anime:**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ----------------- Callback Query -----------------
@app.on_callback_query(filters.regex(r"^play:"))
async def play_callback(client, callback_query):
    anime_name = callback_query.data.split("play:")[1]

    try:
        url = f"{FIREBASE_URL}/anime.json?auth={API_KEY}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
    except Exception as e:
        return await callback_query.answer(f"⚠️ Failed to fetch episodes: {e}", show_alert=True)

    anime_data = data.get(anime_name)
    if not anime_data:
        return await callback_query.answer("⚠️ Anime data not found!", show_alert=True)

    # Auto-play: pick first episode
    first_ep_url = None
    for ep_num, ep_data in anime_data.get("episodes", {}).items():
        first_ep_url = ep_data["video_url"]
        break

    if not first_ep_url:
        return await callback_query.answer("⚠️ No episodes found!", show_alert=True)

    chat_id = callback_query.message.chat.id

    try:
        await call.join_group_call(
            chat_id,
            AudioVideoPiped(first_ep_url)
        )
        await callback_query.answer(f"▶️ Playing {anime_name} in VC!", show_alert=True)
    except Exception as e:
        await callback_query.answer(f"⚠️ Failed to play: {e}", show_alert=True)

# ----------------- Speed Command -----------------
@app.on_message(filters.command("speed") & filters.group)
async def change_speed(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: `/speed 1.5`", quote=True)
    try:
        speed = float(message.command[1])
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
