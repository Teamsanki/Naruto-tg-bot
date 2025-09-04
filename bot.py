import asyncio
import aiohttp
from pyrogram import Client, filters
from pytgcalls import PyTgCalls, idle
from pytgcalls.types.input_stream import AudioVideoPiped
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ----------------- CONFIG -----------------
API_ID = 24393327
API_HASH = "55f3460a683b019f7c764fc6b5f2a946"
BOT_TOKEN = "8202234623:AAHvuE9S5fPWaBe3jCKIEKOkZdOULOjLAWs"
USER_STRING_SESSION = "BQF0Nm8AZIvnVjdk9kfqftXn_rsCElKou1IQFqdeAQ5Rbypqwp7_sBGllKM0YvoKjbBusjmfRg3JVkwwdYHW8auvuXFMLZcLLqD8061gJq4VNx8EyltLx4WDONF1irVH9KS3ffkgtIQ5Sn_t9mpYy24LuMq7u8e07OEto2ezUlNRgSKvtKIwKS3GcYvZcm51A6mD1wWMsnyN5BlHsG6XhOSyS1pqY_KNds06pg5VTtClE7vaxMuyYwWd4SFOeuydrNxeljTyv4eHDqxZ2jc0HAbA7wAAIO-fElzLXOUWpEepKQ2X20NCv3V-x1V7__6M6x0cWtcWMHjE2DJI2livqWXOwr3mXAAAAAHynjhfAA"
FIREBASE_URL = "https://social-bite-skofficial-default-rtdb.firebaseio.com/files.json"
API_KEY = "sk_n56p50uxd5m"

# ----------------- PYROGRAM CLIENTS -----------------
bot = Client("anime-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user = Client("anime-user", api_id=API_ID, api_hash=API_HASH, session_string=USER_STRING_SESSION)
call = PyTgCalls(user)

# ----------------- Fetch anime list -----------------
async def fetch_anime_list():
    async with aiohttp.ClientSession() as session:
        async with session.get(FIREBASE_URL + f"?auth={API_KEY}") as resp:
            data = await resp.json()
    return data or {}

# ----------------- /play command -----------------
@bot.on_message(filters.command("play") & filters.group)
async def play_command(client, message):
    data = await fetch_anime_list()
    if not data:
        return await message.reply("⚠️ No anime available!")

    buttons = [[InlineKeyboardButton(name, callback_data=f"play:{name}")] for name in data.keys()]
    await message.reply("🎬 **Available Anime:**", reply_markup=InlineKeyboardMarkup(buttons))

# ----------------- Callback Query -----------------
@bot.on_callback_query(filters.regex(r"^play:"))
async def play_callback(client, callback_query):
    anime_name = callback_query.data.split("play:")[1]
    data = await fetch_anime_list()
    anime_data = data.get(anime_name)
    if not anime_data:
        return await callback_query.answer("⚠️ Anime not found!", show_alert=True)

    # Pick first episode
    first_ep_url = None
    for ep_num, ep_data in anime_data.get("episodes", {}).items():
        first_ep_url = ep_data.get("video_url")
        break

    if not first_ep_url:
        return await callback_query.answer("⚠️ No episodes found!", show_alert=True)

    chat_id = callback_query.message.chat.id

    try:
        await call.join_group_call(chat_id, AudioVideoPiped(first_ep_url))
        await callback_query.answer(f"▶️ Playing {anime_name} in VC!", show_alert=True)
    except Exception as e:
        await callback_query.answer(f"⚠️ Failed to play: {e}", show_alert=True)

# ----------------- Speed Command -----------------
@bot.on_message(filters.command("speed") & filters.group)
async def change_speed(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: `/speed 1.5`", quote=True)
    try:
        speed = float(message.command[1])
        await message.reply(f"⚡ Video speed set to {speed}x (Feature Coming Soon!)", quote=True)
    except:
        await message.reply("⚠️ Invalid speed value!", quote=True)

# ----------------- Start Bot -----------------
async def main():
    await bot.start()
    await user.start()
    await call.start()
    print("✅ Anime Bot Started!")
    await idle()
    await bot.stop()
    await user.stop()

if __name__ == "__main__":
    asyncio.run(main())
