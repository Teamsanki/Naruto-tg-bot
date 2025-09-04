import asyncio
import aiohttp
from pyrogram import Client, filters
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import AudioVideoPiped
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

# ----------------- HELPER: Fetch anime list from Firebase -----------------
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

    buttons = []
    for anime_name in data.keys():
        buttons.append([InlineKeyboardButton(anime_name, callback_data=f"play:{anime_name}")])

    await message.reply("🎬 **Available Anime:**", reply_markup=InlineKeyboardMarkup(buttons))

# ----------------- Callback Query for Inline -----------------
@bot.on_callback_query(filters.regex(r"^play:"))
async def play_callback(client, callback_query):
    anime_name = callback_query.data.split("play:")[1]
    data = await fetch_anime_list()
    anime_data = data.get(anime_name)

    if not anime_data:
        return await callback_query.answer("⚠️ Anime not found!", show_alert=True)

    # pick first episode
    first_ep_url = None
    episodes = anime_data.get("episodes", {})
    if not episodes:
        return await callback_query.answer("⚠️ No episodes found!", show_alert=True)

    # show inline list of episodes
    ep_buttons = []
    for ep_num, ep_data in episodes.items():
        ep_buttons.append([InlineKeyboardButton(f"Episode {ep_num}", callback_data=f"play_ep:{anime_name}:{ep_num}")])

    await callback_query.message.edit_text(f"🎬 **{anime_name} Episodes:**", reply_markup=InlineKeyboardMarkup(ep_buttons))

# ----------------- Callback Query for Episodes -----------------
@bot.on_callback_query(filters.regex(r"^play_ep:"))
async def play_episode_callback(client, callback_query):
    _, anime_name, ep_num = callback_query.data.split(":")
    data = await fetch_anime_list()
    anime_data = data.get(anime_name)
    ep_data = anime_data.get("episodes", {}).get(ep_num)

    if not ep_data:
        return await callback_query.answer("⚠️ Episode not found!", show_alert=True)

    video_url = ep_data.get("video_url")
    chat_id = callback_query.message.chat.id

    try:
        await call.join_group_call(chat_id, AudioVideoPiped(video_url))
        await callback_query.answer(f"▶️ Playing {anime_name} Ep {ep_num} in VC!", show_alert=True)
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

# ----------------- STARTUP -----------------
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
