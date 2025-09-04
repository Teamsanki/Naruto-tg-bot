import asyncio
import random
import string
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioVideoPiped
from pytgcalls.exceptions import NoActiveGroupCall

# ---------------- CONFIG ---------------- #
API_ID = 24393327
API_HASH = "55f3460a683b019f7c764fc6b5f2a946"
BOT_TOKEN = "8202234623:AAHvuE9S5fPWaBe3jCKIEKOkZdOULOjLAWs"
USER_STRING_SESSION = "BQF0Nm8AZIvnVjdk9kfqftXn_..."  # truncated
FIREBASE_URL = "https://social-bite-skofficial-default-rtdb.firebaseio.com/files.json"

# ---------------- INIT CLIENTS ---------------- #
app = Client("naruto_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user = Client("naruto_user", api_id=API_ID, api_hash=API_HASH, session_string=USER_STRING_SESSION)
call_py = PyTgCalls(app)

# ---------------- UTILS ---------------- #
async def fetch_firebase_data():
    async with aiohttp.ClientSession() as session:
        async with session.get(FIREBASE_URL) as resp:
            if resp.status != 200:
                return None
            return await resp.json()

# ---------------- PLAY COMMAND ---------------- #
@app.on_message(filters.command("play", prefixes=["/", "!", ".", "#"]) & filters.group)
async def play_command(client: Client, message: Message):
    await message.reply_text("ℹ️ Play command received. Implement your stream logic here.")

# ---------------- NARUTO COMMAND ---------------- #
@app.on_message(filters.command("naruto", prefixes=["/", "!", ".", "#"]) & filters.group)
async def naruto_list(client: Client, message: Message):
    mystic = await message.reply_text("🔎 Fetching Naruto episodes...")
    data = await fetch_firebase_data()
    if not data:
        return await mystic.edit_text("⚠️ Firebase me koi episode nahi hai.")
    
    # Sort episodes
    try:
        episodes = sorted(data.items(), key=lambda x: int(x[0].replace("-", "")))
    except:
        episodes = sorted(data.items())

    buttons, temp = [], []
    for key, ep in episodes:
        temp.append(InlineKeyboardButton(ep.get("name", f"Episode {key}"), callback_data=f"naruto_play|{key}"))
        if len(temp) == 3:
            buttons.append(temp)
            temp = []
    if temp:
        buttons.append(temp)

    await mystic.edit_text("📺 Naruto Episodes:", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.regex(r"naruto_play\|"))
async def play_naruto_episode(client: Client, callback):
    ep_key = callback.data.split("|")[1]
    chat_id = callback.message.chat.id
    await callback.answer("▶️ Playing episode...", show_alert=True)
    mystic = await callback.message.edit_text("🔄 Loading Naruto episode...")

    data = await fetch_firebase_data()
    if not data or ep_key not in data:
        return await mystic.edit_text("⚠️ Episode not found in Firebase.")

    ep_data = data[ep_key]
    video_url = ep_data.get("url")
    if not video_url:
        return await mystic.edit_text("❌ Episode URL missing.")

    try:
        # FFmpeg-based audio/video stream
        await call_py.join_group_call(chat_id, AudioVideoPiped(video_url))
        await mystic.edit_text(f"▶️ Now Playing in VC: {ep_data.get('name', f'NARUTO Episode {ep_key}')}")
    except NoActiveGroupCall:
        await mystic.edit_text("⚠️ Group VC not active.")
    except Exception as e:
        await mystic.edit_text(f"⚠️ VC Join/Stream Error: {str(e)}")

# ---------------- START BOT ---------------- #
async def main():
    await app.start()
    await user.start()
    await call_py.start()
    print("Bot and PyTgCalls started...")
    await asyncio.Future()  # keep running

if __name__ == "__main__":
    asyncio.run(main())
