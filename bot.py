from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

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
    for name, item in data.items():
        # Callback data format: play:<anime_name>
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
        # Fetch episodes for selected anime
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
