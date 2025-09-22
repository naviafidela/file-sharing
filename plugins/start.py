# (©)Codexbotz
# Recode by @mrismanaziz
# t.me/SharingUserbot & t.me/Lunatic0de

import asyncio
from datetime import datetime
from time import time

from bot import Bot
from config import (
    ADMINS,
    CUSTOM_CAPTION,
    DISABLE_CHANNEL_BUTTON,
    FORCE_MSG,
    PROTECT_CONTENT,
    START_MSG,
)
from database.sql import add_user, delete_user, full_userbase, query_msg
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked
from pyrogram.types import InlineKeyboardMarkup, Message

from helper_func import decode, get_messages, subsall, subsch, subsgc

from .button import fsub_button, start_button

START_TIME = datetime.utcnow()
START_TIME_ISO = START_TIME.replace(microsecond=0).isoformat()
TIME_DURATION_UNITS = (
    ("week", 60 * 60 * 24 * 7),
    ("day", 60**2 * 24),
    ("hour", 60**2),
    ("min", 60),
    ("sec", 1),
)


async def _human_time_duration(seconds):
    if seconds == 0:
        return "inf"
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append(f'{amount} {unit}{"" if amount == 1 else "s"}')
    return ", ".join(parts)





@Bot.on_message(filters.command(["users", "stats"]) & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(
        chat_id=message.chat.id, text="<code>Processing ...</code>"
    )
    users = await full_userbase()
    await msg.edit(f"{len(users)} <b>Pengguna menggunakan bot ini</b>")


@Bot.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        query = await query_msg()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0

        pls_wait = await message.reply(
            "<code>Broadcasting Message Tunggu Sebentar...</code>"
        )
        for row in query:
            chat_id = int(row[0])
            if chat_id not in ADMINS:
                try:
                    await broadcast_msg.copy(chat_id, protect_content=PROTECT_CONTENT)
                    successful += 1
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await broadcast_msg.copy(chat_id, protect_content=PROTECT_CONTENT)
                    successful += 1
                except UserIsBlocked:
                    await delete_user(chat_id)
                    blocked += 1
                except InputUserDeactivated:
                    await delete_user(chat_id)
                    deleted += 1
                except BaseException:
                    unsuccessful += 1
                total += 1
        status = f"""<b><u>Berhasil Broadcast</u>
Jumlah Pengguna: <code>{total}</code>
Berhasil: <code>{successful}</code>
Gagal: <code>{unsuccessful}</code>
Pengguna diblokir: <code>{blocked}</code>
Akun Terhapus: <code>{deleted}</code></b>"""
        return await pls_wait.edit(status)
    else:
        msg = await message.reply(
            "<code>Gunakan Perintah ini Harus Sambil Reply ke pesan telegram yang ingin di Broadcast.</code>"
        )
        await asyncio.sleep(8)
        await msg.delete()


@Bot.on_message(filters.command("ping"))
async def ping_pong(client, m: Message):
    start = time()
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    m_reply = await m.reply_text("Pinging...")
    delta_ping = time() - start
    await m_reply.edit_text(
        "<b>PONG!!</b>🏓 \n"
        f"<b>• Pinger -</b> <code>{delta_ping * 1000:.3f}ms</code>\n"
        f"<b>• Uptime -</b> <code>{uptime}</code>\n"
    )


@Bot.on_message(filters.command("uptime"))
async def get_uptime(client, m: Message):
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    await m.reply_text(
        "🤖 <b>Bot Status:</b>\n"
        f"• <b>Uptime:</b> <code>{uptime}</code>\n"
        f"• <b>Start Time:</b> <code>{START_TIME_ISO}</code>"
    )
