import os
import asyncio
from telethon import TelegramClient, events
from telethon.tl.functions.messages import DeleteMessagesRequest
from telethon.tl.types import User
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import io
import datetime

# ─── CONFIG ────────────────────────────────────────────────────────────────────
API_ID   = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION  = os.environ.get("SESSION_STRING", "userbot")

client = TelegramClient(SESSION, API_ID, API_HASH)

# ─── STATE ──────────────────────────────────────────────────────────────────────
afk_message: str | None = None          # None = AFK yoq
afk_replies: dict[int, bool] = {}       # user_id -> already replied bu seansta
info_reply_text: str | None = None      # .info ga javob matni

# ─── AFK ────────────────────────────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.afk off$"))
async def afk_off(event):
    global afk_message, afk_replies
    afk_message = None
    afk_replies = {}
    await event.edit("✅ AFK rejim o'chirildi.")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.afk (.+)$"))
async def afk_on(event):
    global afk_message, afk_replies
    afk_message = event.pattern_match.group(1).strip()
    afk_replies = {}
    await event.edit(f"😴 AFK rejim yoqildi: **{afk_message}**")

@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def afk_auto_reply(event):
    if afk_message is None:
        return
    sender = await event.get_sender()
    if not isinstance(sender, User) or sender.bot:
        return
    uid = sender.id
    if uid in afk_replies:
        return
    afk_replies[uid] = True
    await event.reply(f"🤖 Avto-javob:\n{afk_message}")

# ─── .pdf ────────────────────────────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.pdf$"))
async def make_pdf(event):
    await event.edit("⏳ PDF tayyorlanmoqda...")
    dialogs = await client.get_dialogs()
    
    users = []
    for d in dialogs:
        if d.is_user and isinstance(d.entity, User) and not d.entity.bot:
            u = d.entity
            name = " ".join(filter(None, [u.first_name or "", u.last_name or ""]))
            users.append({
                "id":       u.id,
                "name":     name or "—",
                "username": f"@{u.username}" if u.username else "—",
                "phone":    u.phone or "—",
            })

    # PDF yaratish
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, h - 2*cm, "Shaxsiy chatlar ro'yxati")
    c.setFont("Helvetica", 8)
    c.drawString(2*cm, h - 2.6*cm, f"Sana: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")

    headers = ["#", "Ism", "Username", "Telefon", "ID"]
    col_x   = [2*cm, 3*cm, 8*cm, 13*cm, 17*cm]
    y = h - 3.5*cm

    def draw_row(row, bold=False, y_pos=None):
        c.setFont("Helvetica-Bold" if bold else "Helvetica", 8)
        for i, val in enumerate(row):
            c.drawString(col_x[i], y_pos, str(val))

    draw_row(headers, bold=True, y_pos=y)
    y -= 0.5*cm
    c.line(2*cm, y, w - 2*cm, y)
    y -= 0.4*cm

    for idx, u in enumerate(users, 1):
        if y < 2*cm:
            c.showPage()
            y = h - 2*cm
        draw_row([idx, u["name"], u["username"], u["phone"], u["id"]], y_pos=y)
        y -= 0.45*cm

    c.save()
    buf.seek(0)

    await client.send_file(
        event.chat_id,
        buf,
        caption=f"📋 Jami {len(users)} ta shaxsiy chat",
        file_name="shaxsiylar.pdf",
        force_document=True,
    )
    await event.delete()

# ─── .info ───────────────────────────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.info$"))
async def cmd_info(event):
    target = None
    if event.is_reply:
        rep = await event.get_reply_message()
        target = await rep.get_sender()
    elif event.is_private:
        target = await event.get_chat()

    if not target or not isinstance(target, User):
        await event.edit("❌ Foydalanuvchi topilmadi.")
        return

    lines = [
        "👤 **Foydalanuvchi ma'lumotlari**",
        f"• Ism: {target.first_name or '—'}",
        f"• Familiya: {target.last_name or '—'}",
        f"• Username: @{target.username}" if target.username else "• Username: —",
        f"• Telefon: {target.phone or '—'}",
        f"• ID: `{target.id}`",
        f"• Bot: {'Ha' if target.bot else "Yo'q"}",
        f"• Premium: {'Ha' if getattr(target, 'premium', False) else "Yo'q"}",
    ]
    await event.edit("\n".join(lines))

# ─── .reply (info javobini sozlash) ──────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.reply (.+)$"))
async def set_reply(event):
    global info_reply_text
    info_reply_text = event.pattern_match.group(1).strip()
    await event.edit(f"✅ `.info` javobi saqlandi: {info_reply_text}")

@client.on(events.NewMessage(incoming=True, pattern=r"^\.info$"))
async def answer_info(event):
    if info_reply_text is None:
        return
    if event.is_reply:
        rep = await event.get_reply_message()
        if rep and rep.out:
            await event.reply(info_reply_text)

# ─── .clear ──────────────────────────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.clear (\d+)$"))
async def clear_msgs(event):
    n = int(event.pattern_match.group(1))
    msgs = []
    async for msg in client.iter_messages(event.chat_id, limit=n + 1):
        msgs.append(msg.id)
    if msgs:
        await client(DeleteMessagesRequest(msgs, revoke=True))

# ─── .intellect ──────────────────────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.intellect$"))
async def cmd_intellect(event):
    await event.edit("📚 https://sakura-on.github.io/IELTS/")

# ─── .mafia ──────────────────────────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.mafia$"))
async def cmd_mafia(event):
    await event.edit("🎮 https://sakura-on.github.io/mafia")

# ─── .. quote ─────────────────────────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\.\. (.+)$"))
async def double_dot(event):
    text = event.pattern_match.group(1).strip()
    await event.edit(f'"{text}"')

# ─── . spoiler ────────────────────────────────────────────────────────────────────
@client.on(events.NewMessage(outgoing=True, pattern=r"^\. (.+)$"))
async def single_dot_spoiler(event):
    text = event.pattern_match.group(1).strip()
    await event.edit(f"||{text}||")

# ─── START ────────────────────────────────────────────────────────────────────────
async def main():
    print("✅ Userbot ishga tushdi!")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
