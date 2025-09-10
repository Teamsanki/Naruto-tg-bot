import asyncio
import aiohttp
import os
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from py_tgcalls import PyTgCalls
from py_tgcalls.types.input_stream import AudioPiped
from py_tgcalls.exceptions import NoActiveGroupCall

# ---------------- CONFIG ---------------- #
load_dotenv()
API_ID = int(os.getenv("API_ID", "24393327"))
API_HASH = os.getenv("API_HASH", "55f3460a683b019f7c764fc6b5f2a946")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8202234623:AAHvuE9S5fPWaBe3jCKIEKOkZdOULOjLAWs")
USER_STRING_SESSION = os.getenv("USER_STRING_SESSION", "BQF0Nm8AfADioJ8J6EcT21gOSev-VMlD2QW6AEdU2U6zkxyC_c96W1exZF6KVQ8UD4ic0tMTrMSMCqdCnUjKDcH-4qD9YOYohSeq2v3F8OyE4-U6TfD5AY4osnfjXG33up9ghfzxH3qI84WDe5_LWpaOaQtl8ZZoQgWM99s-Csu5rWOC1OQxuzLljGvrgxyW4HLP0F8zO-xT_zmkDY_9NskdSVK9WanjMmVgrBUdtjaWj-qHujzAMBqTRruSyQeoafxQG4RU9YA7xWoVWERJqbbkH5Zt6uOM3BX-XuJugoEFkTRmICHFwzvi2igoJ5B1CpYc96tZe7kFLH6FCuXa0AytJUgeWAAAAAHynjhfAA")
FIREBASE_URL = os.getenv("FIREBASE_URL", "https://social-bite-skofficial-default-rtdb.firebaseio.com/files.json")

# ---------------- INIT CLIENTS ---------------- #
app = Client("naruto_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user = Client("naruto_user", api_id=API_ID, api_hash=API_HASH, session_string=USER_STRING_SESSION)
call_py = PyTgCalls(user)

# ---------------- UTILS ---------------- #
async def fetch_firebase_data():
    async with aiohttp.ClientSession() as session:
        async with session.get(FIREBASE_URL) as resp:
            if resp.status != 200:
                return None
            return await resp.json()

# ---------------- COMMANDS ---------------- #
@app.on_message(filters.command("naruto") & filters.group)
async def naruto_list(client, message):
    mystic = await message.reply_text("🔎 Fetching Naruto episodes...")
    data = await fetch_firebase_data()
    if not data:
        return await mystic.edit_text("⚠️ Firebase me koi episode nahi hai.")

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

@app.on_callback_query(filters.regex(r"naruto_play\|.*"))
async def play_naruto_episode(client, callback):
    ep_key = callback.data.split("|")[1]
    chat_id = callback.message.chat.id
    await callback.answer("▶️ Playing episode...", show_alert=True)
    mystic = await callback.message.edit_text("🔄 Loading Naruto episode...")

    data = await fetch_firebase_data()
    if not data or ep_key not in data:
        return await mystic.edit_text("⚠️ Episode not found in Firebase.")

    ep_data = data[ep_key]
    audio_url = ep_data.get("url")
    if not audio_url:
        return await mystic.edit_text("❌ Episode URL missing.")

    try:
        await call_py.join_group_call(
            chat_id,
            AudioPiped(audio_url)
        )
        await mystic.edit_text(f"▶️ Now Playing in VC: {ep_data.get('name', f'NARUTO Episode {ep_key}')}")
    except NoActiveGroupCall:
        await mystic.edit_text("⚠️ Group VC not active. Start VC first.")
    except Exception as e:
        await mystic.edit_text(f"⚠️ VC Join/Stream Error: {str(e)}")

@app.on_message(filters.command("play") & filters.group)
async def play_command(client, message):
    await message.reply_text("ℹ️ Play command received. Implement your stream logic here.")

# ---------------- START BOT ---------------- #
async def main():
    await app.start()
    print("Bot started...")

    try:
        await user.start()
        print("User client started...")
    except Exception as e:
        print(f"⚠️ User client failed to start: {e}")
        print("Bot will continue without VC streaming...")

    await call_py.start()
    print("PyTgCalls started...")
    print("✅ Naruto Bot is ready!")

    await asyncio.Future()  # keep running

if __name__ == "__main__":
    asyncio.run(main())
