import logging
import os
import json
import asyncio
import urllib.parse
import time
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    WebAppInfo
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
from telegram.constants import ParseMode

# ==================== SOZLAMALAR ====================
BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_USERNAME   = "@Nobody_ff2"
ADMIN_TG_LINK    = "https://t.me/Nobody_ff2"
REQUIRED_CHANNEL = "@premosit"
CARD_NUMBER      = "9860-6067-5228-3238"
CARD_OWNER       = "X.I."
CARD_PHONE       = "+998-88-855-13-20"
OWNER_ID         = 7362457858
WEBAPP_URL       = "https://sakura-on.github.io/TopUp-Zone"
DATA_FILE        = "bot_data.json"

# ── Stikerlar (file_id) ──
STICKER_WELCOME = "CAACAgIAAxkBAAIBgWf2xgABHQUhQzFz8M_0vEklFLJvAAIyAAMw1J0R6OTAAWPy2rAeNgQ"
STICKER_SUCCESS = "CAACAgIAAxkBAAIBgmf2xgABtgpP2yHqOeLr5wgB7BInAAI4AAMw1J0Rj2FLB-2RVqEeNgQ"
STICKER_REJECT  = "CAACAgIAAxkBAAIBg2f2xgABpL3p0CqMjWF8FmDHVIwZAAI6AAMw1J0RvpFeBmkDL9keNgQ"
STICKER_WAIT    = "CAACAgIAAxkBAAIBhGf2xgABfmoxJc_eELXrWe-VAAI7AAMw1J0R_fquFhqHe0weNgQ"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== DB ====================
DB             = {}
pending_orders = {}

ST_WAITING_TG_USERNAME  = "wt_username"
ST_WAITING_RECEIPT      = "wt_receipt"
ST_WAITING_ADMIN_ADD    = "wt_admin_add"
ST_WAITING_ADMIN_REMOVE = "wt_admin_remove"
ST_WAITING_AD_TEXT      = "wt_ad_text"
ST_WAITING_AD_PHOTO     = "wt_ad_photo"

AP_STATE       = "ap_state"
AP_DATA        = "ap_data"
AP_TG_ADD_NAME  = "ap_tg_add_name"
AP_TG_ADD_PRICE = "ap_tg_add_price"


def load_db():
    global DB
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                DB = json.load(f)
            logger.info("Ma'lumotlar yuklandi")
        except Exception as e:
            logger.error(f"Yuklashda xato: {e}")
            DB = _default_db()
    else:
        DB = _default_db()
        save_db()


def save_db():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(DB, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Saqlashda xato: {e}")


def _default_db():
    return {
        "admin_ids": [],
        "stars_rate": 250,
        "ton_rate": 17500,
        "status": {"prem": True, "stars": True, "ton": True},
        "tg_packages": [],
        "users": {},
        "pending_ads": {},
    }


def fmt(price):
    try:
        return f"{int(price):,}".replace(",", ".") + " so'm"
    except Exception:
        return f"{price} so'm"


def next_id():
    return int(time.time() * 1000) % 999999999


def is_owner(uid):
    return uid == OWNER_ID


def is_admin(uid):
    return uid == OWNER_ID or uid in DB.get("admin_ids", [])


def get_user(uid):
    users = DB.setdefault("users", {})
    key   = str(uid)
    if key not in users:
        users[key] = {"name": "", "username": "", "orders": [], "total_spent": 0}
    return users[key]


def tg_sec_name(key):
    return {"prem": "Telegram Premium", "stars": "Telegram Stars", "ton": "TON"}.get(key, key)


async def check_sub(uid, bot):
    try:
        m = await bot.get_chat_member(REQUIRED_CHANNEL, uid)
        return m.status in ["member", "administrator", "creator"]
    except Exception:
        return False


async def send_sticker(chat_id, sticker_id, bot):
    try:
        await bot.send_sticker(chat_id=chat_id, sticker=sticker_id)
    except Exception as e:
        logger.warning(f"Stiker yuborishda xato: {e}")


def main_kb(uid=0):
    rows = [
        [KeyboardButton("🌐 Do'kon", web_app=WebAppInfo(url=WEBAPP_URL))],
        [KeyboardButton("📱 Telegram Xizmatlar")],
        [KeyboardButton("👤 Profil"), KeyboardButton("💬 Admin bilan bog'lanish")],
    ]
    if is_admin(uid):
        rows.append([
            KeyboardButton("⚙️ Boshqaruv paneli"),
            KeyboardButton("📊 Statistika"),
            KeyboardButton("📣 Reklama"),
        ])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


async def sub_guard(update, context):
    uid = update.effective_user.id
    if not await check_sub(uid, context.bot):
        kb = [[InlineKeyboardButton(
            "📢 Kanalga a'zo bo'lish",
            url=f"https://t.me/{REQUIRED_CHANNEL[1:]}")]]
        msg = update.message or (
            update.callback_query.message if update.callback_query else None)
        if msg:
            await msg.reply_text(
                f"Botdan foydalanish uchun {REQUIRED_CHANNEL} kanaliga a'zo bo'ling!\n\n"
                f"A'zo bo'lgach /start bosing.",
                reply_markup=InlineKeyboardMarkup(kb))
        return False
    return True


async def broadcast_admins(context, text, photo=None, markup=None):
    targets = set(DB.get("admin_ids", [])) | {OWNER_ID}
    for aid in targets:
        try:
            if photo:
                await context.bot.send_photo(
                    chat_id=aid, photo=photo,
                    caption=text, parse_mode=ParseMode.HTML, reply_markup=markup)
            else:
                await context.bot.send_message(
                    chat_id=aid, text=text,
                    parse_mode=ParseMode.HTML, reply_markup=markup)
        except Exception as e:
            logger.error(f"Admin {aid}: {e}")


# ==================== /start ====================

async def cmd_start(update, context):
    user  = update.effective_user
    store = get_user(user.id)
    store["name"]     = user.full_name
    store["username"] = user.username or ""
    save_db()

    if not await check_sub(user.id, context.bot):
        kb = [[InlineKeyboardButton("📢 Kanalga a'zo bo'lish",
                                    url=f"https://t.me/{REQUIRED_CHANNEL[1:]}")]]
        await update.message.reply_text(
            f"Botdan foydalanish uchun {REQUIRED_CHANNEL} ga a'zo bo'ling!",
            reply_markup=InlineKeyboardMarkup(kb))
        return

    # Saytdan deep link
    if context.args:
        payload = "_".join(context.args)
        parts   = payload.split("__")
        if len(parts) >= 3:
            section   = parts[0].replace("_", " ").strip()
            prod_name = parts[1].replace("_", " ").strip()
            u_input   = parts[2].replace("_", " ").strip()
            price_raw = parts[3].replace("_", " ").strip() if len(parts) > 3 else ""
            price     = int("".join(filter(str.isdigit, price_raw))) if price_raw else 0

            pending_orders[user.id] = {
                "product": prod_name, "price": price,
                "section": section,  "recipient": u_input,
                "source": "website", "type": "website",
            }
            context.user_data["state"] = ST_WAITING_RECEIPT
            kb = [[InlineKeyboardButton("✅ To'lov qildim — Chek yuborish",
                                        callback_data="payment_done")]]
            await update.message.reply_text(
                f"Xush kelibsiz, <b>{user.first_name}</b>!\n\n"
                f"📋 <b>Saytdan buyurtma:</b>\n"
                f"Bo'lim: <b>{section}</b>\n"
                f"Mahsulot: <b>{prod_name}</b>\n"
                f"Narxi: <b>{fmt(price) if price else 'aniqlanmadi'}</b>\n"
                f"Username: <b>{u_input}</b>\n\n"
                f"💳 Karta: <code>{CARD_NUMBER}</code>\n"
                f"Egasi: <b>{CARD_OWNER}</b>\n"
                f"Tel: <b>{CARD_PHONE}</b>\n\n"
                f"To'lov qilgach chekni yuborish uchun tugmani bosing:",
                parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))
            return

    # Oddiy start — stiker + xush kelibsiz
    await send_sticker(user.id, STICKER_WELCOME, context.bot)
    await update.message.reply_text(
        f"Assalomu alaykum, <b>{user.first_name}</b>!\n\n"
        f"<b>TopUp Zone</b> ga xush kelibsiz!\n"
        f"Telegram xizmatlari: Premium, Stars, TON.\n\n"
        f"Pastdagi menyudan foydalaning:",
        parse_mode=ParseMode.HTML, reply_markup=main_kb(user.id))
    await update.message.reply_text(
        "Do'konni to'liq ochish:",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("Do'konni ochish", web_app=WebAppInfo(url=WEBAPP_URL))
        ]]))


async def cmd_cancel(update, context):
    uid = update.effective_user.id
    pending_orders.pop(uid, None)
    context.user_data.clear()
    await update.message.reply_text("Bekor qilindi.", reply_markup=main_kb(uid))


# ==================== TELEGRAM XIZMATLAR ====================

async def show_tg(update, context):
    if not await sub_guard(update, context):
        return
    status = DB.get("status", {})
    items  = [
        ("prem",  "💎", "Telegram Premium"),
        ("stars", "⭐", "Telegram Stars"),
        ("ton",   "💠", "TON"),
    ]
    kb = []
    for sid, icon, name in items:
        ok    = status.get(sid, True)
        label = f"{icon} {name}" + ("" if ok else " 🔜")
        cb    = f"tg_{sid}" if ok else "noop"
        kb.append([InlineKeyboardButton(label, callback_data=cb)])

    is_cb = bool(update.callback_query)
    msg   = update.callback_query.message if is_cb else update.message
    fn    = msg.edit_text if is_cb else msg.reply_text
    await fn("📱 <b>Telegram Xizmatlar</b>\n\nXizmat turini tanlang:",
             parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))


async def tg_cat_cb(update, context):
    q   = update.callback_query
    await q.answer()
    cat = q.data.replace("tg_", "")

    if cat == "prem":
        kb = [
            [InlineKeyboardButton("🔑 Acc kirib (login/parol bilan)", callback_data="prem_acc")],
            [InlineKeyboardButton("📨 Acc kirmasdan (gift/@username)", callback_data="prem_id")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="back_tg")],
        ]
        await q.edit_message_text(
            "💎 <b>Telegram Premium</b>\n\nQanday usulda sotib olmoqchisiz?",
            parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))

    elif cat == "stars":
        rate = DB.get("stars_rate", 250)
        pkgs = [p for p in DB.get("tg_packages", []) if p["section"] == "stars"]
        kb   = []
        if pkgs:
            for p in sorted(pkgs, key=lambda x: x["price"]):
                kb.append([InlineKeyboardButton(
                    f"{p['name']} — {fmt(p['price'])}",
                    callback_data=f"buy_tg_{p['id']}")])
        else:
            for n in [50, 100, 250, 500, 1000]:
                kb.append([InlineKeyboardButton(
                    f"⭐ {n} Stars — {fmt(n * rate)}",
                    callback_data=f"buy_sq_{n}")])
        kb.append([InlineKeyboardButton("🔙 Orqaga", callback_data="back_tg")])
        await q.edit_message_text(
            f"⭐ <b>Telegram Stars</b>\n💱 1 Stars = {rate:,} so'm\n\nPaketni tanlang:",
            parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))

    elif cat == "ton":
        rate = DB.get("ton_rate", 17500)
        pkgs = [p for p in DB.get("tg_packages", []) if p["section"] == "ton"]
        kb   = []
        if pkgs:
            for p in sorted(pkgs, key=lambda x: x["price"]):
                kb.append([InlineKeyboardButton(
                    f"{p['name']} — {fmt(p['price'])}",
                    callback_data=f"buy_tg_{p['id']}")])
        else:
            for n in [1, 2, 5, 10, 20]:
                kb.append([InlineKeyboardButton(
                    f"💠 {n} TON — {fmt(n * rate)}",
                    callback_data=f"buy_tq_{n}")])
        kb.append([InlineKeyboardButton("🔙 Orqaga", callback_data="back_tg")])
        await q.edit_message_text(
            f"💠 <b>TON</b>\n💱 1 TON = {rate:,} so'm\n\nPaketni tanlang:",
            parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))


async def prem_acc_cb(update, context):
    q    = update.callback_query
    await q.answer()
    pkgs = [p for p in DB.get("tg_packages", [])
            if p["section"] == "prem" and p.get("method") == "acc"]
    if not pkgs:
        msg_text = (
            "Bo'lim: Telegram Premium\nUsul: Acc kirib\n\n"
            "Narx va muddatlar haqida ma'lumot bering."
        )
        kb = [
            [InlineKeyboardButton("💬 Adminga yozish",
                url=f"https://t.me/Nobody_ff2?text={urllib.parse.quote(msg_text)}")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="tg_prem")],
        ]
        await q.edit_message_text(
            "💎 <b>Premium (Acc kirib)</b>\n\n"
            "Hozircha bu usulda paketlar mavjud emas.\n"
            "Admin bilan bog'laning:",
            parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))
        return
    kb = []
    for p in sorted(pkgs, key=lambda x: x["price"]):
        kb.append([InlineKeyboardButton(
            f"🔑 {p['name']} — {fmt(p['price'])}", callback_data=f"buy_tg_{p['id']}")])
    kb.append([InlineKeyboardButton("🔙 Orqaga", callback_data="tg_prem")])
    await q.edit_message_text(
        "💎 <b>Premium (Acc kirib)</b>\n\n"
        "Login va parol talab qilinadi.\nPaketni tanlang:",
        parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))


async def prem_id_cb(update, context):
    q    = update.callback_query
    await q.answer()
    pkgs = [p for p in DB.get("tg_packages", [])
            if p["section"] == "prem" and p.get("method", "id") == "id"]
    if not pkgs:
        kb = [[InlineKeyboardButton("🔙 Orqaga", callback_data="tg_prem")]]
        await q.edit_message_text(
            "💎 <b>Premium (Gift)</b>\n\nHozircha paketlar mavjud emas.",
            parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))
        return
    kb = []
    for p in sorted(pkgs, key=lambda x: x["price"]):
        kb.append([InlineKeyboardButton(
            f"{p['name']} — {fmt(p['price'])}", callback_data=f"buy_tg_{p['id']}")])
    kb.append([InlineKeyboardButton("🔙 Orqaga", callback_data="tg_prem")])
    await q.edit_message_text(
        "💎 <b>Premium (Gift / Acc kirmasdan)</b>\n\n"
        "@Username orqali yetkaziladi.\nPaketni tanlang:",
        parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))


# ==================== SOTIB OLISH ====================

async def buy_tg_cb(update, context):
    q   = update.callback_query
    await q.answer()
    uid = q.from_user.id
    d   = q.data

    # ── Quick Stars ──
    if d.startswith("buy_sq_"):
        n    = int(d[7:])
        rate = DB.get("stars_rate", 250)
        pending_orders[uid] = {
            "product": f"⭐ {n} Stars", "price": n * rate,
            "section": "Telegram Stars", "recipient": None,
            "source": "bot", "type": "stars",
        }
        context.user_data["state"] = ST_WAITING_TG_USERNAME
        await q.message.reply_text(
            f"Tanlandi: <b>⭐ {n} Stars</b>\n"
            f"Narxi: <b>{fmt(n * rate)}</b>\n\n"
            f"Telegram <b>@Username</b> ingizni kiriting:\n"
            f"<i>Misol: @Username123</i>\n\n"
            f"/cancel — bekor qilish",
            parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardRemove())
        return

    # ── Quick TON ──
    if d.startswith("buy_tq_"):
        n    = int(d[7:])
        rate = DB.get("ton_rate", 17500)
        pending_orders[uid] = {
            "product": f"💠 {n} TON", "price": n * rate,
            "section": "TON", "recipient": None,
            "source": "bot", "type": "ton",
        }
        context.user_data["state"] = ST_WAITING_TG_USERNAME
        await q.message.reply_text(
            f"Tanlandi: <b>💠 {n} TON</b>\n"
            f"Narxi: <b>{fmt(n * rate)}</b>\n\n"
            f"TON <b>hamyon manzilingizni</b> kiriting:\n"
            f"<i>Misol: UQB...xyz</i>\n\n"
            f"/cancel — bekor qilish",
            parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardRemove())
        return

    # ── TG Paket ──
    if d.startswith("buy_tg_"):
        pid = int(d[7:])
        pkg = next((p for p in DB.get("tg_packages", []) if p["id"] == pid), None)
        if not pkg:
            await q.answer("Paket topilmadi!", show_alert=True)
            return

        # Acc kirib
        if pkg.get("method") == "acc":
            msg_text = (
                f"Bo'lim: {tg_sec_name(pkg['section'])}\n"
                f"Mahsulot: {pkg['name']}\n"
                f"Narxi: {fmt(pkg['price'])}\n\n"
                f"Akkount orqali xizmat olmoqchiman."
            )
            back_cb = "prem_acc" if pkg["section"] == "prem" else "back_tg"
            kb = [
                [InlineKeyboardButton(
                    "💬 Adminga yozish",
                    url=f"https://t.me/Nobody_ff2?text={urllib.parse.quote(msg_text)}")],
                [InlineKeyboardButton("🔙 Orqaga", callback_data=back_cb)],
            ]
            await q.edit_message_text(
                f"🔑 <b>{pkg['name']}</b>\n"
                f"Narxi: <b>{fmt(pkg['price'])}</b>\n\n"
                f"Bu xizmat uchun akkount kirish kerak.\n\n"
                f"Quyidagi tugmani bosib adminga yozing,\n"
                f"admin sizning hisobingizga kirib olib beradi. 👇",
                parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))
            return

        # @Username / Hamyon
        order_type = pkg["section"]
        pending_orders[uid] = {
            "product": pkg["name"], "price": pkg["price"],
            "section": tg_sec_name(order_type), "recipient": None,
            "source": "bot", "type": order_type,
        }
        context.user_data["state"] = ST_WAITING_TG_USERNAME

        if order_type == "ton":
            prompt = (
                f"Tanlandi: <b>{pkg['name']}</b>\n"
                f"Narxi: <b>{fmt(pkg['price'])}</b>\n\n"
                f"TON <b>hamyon manzilingizni</b> kiriting:\n"
                f"<i>Misol: UQB...xyz</i>\n\n"
                f"/cancel — bekor qilish"
            )
        else:
            prompt = (
                f"Tanlandi: <b>{pkg['name']}</b>\n"
                f"Narxi: <b>{fmt(pkg['price'])}</b>\n\n"
                f"Telegram <b>@Username</b> ingizni kiriting:\n"
                f"<i>Misol: @Username123</i>\n\n"
                f"/cancel — bekor qilish"
            )
        await q.message.reply_text(prompt, parse_mode=ParseMode.HTML,
                                   reply_markup=ReplyKeyboardRemove())


# ==================== MATN INPUT ====================

async def receive_text(update, context):
    uid   = update.effective_user.id
    state = context.user_data.get("state")
    ap_st = context.user_data.get(AP_STATE)
    text  = update.message.text.strip()

    # ── Username / Hamyon kutish ──
    if state == ST_WAITING_TG_USERNAME:
        if uid not in pending_orders:
            context.user_data.clear()
            await update.message.reply_text(
                "Buyurtma topilmadi. /start bosing.",
                reply_markup=main_kb(uid))
            return
        order_type = pending_orders[uid].get("type", "stars")
        if order_type == "ton":
            if len(text) < 10:
                await update.message.reply_text(
                    "Noto'g'ri hamyon manzili!\n"
                    "Qaytadan kiriting yoki /cancel")
                return
        else:
            if not text.startswith("@") or len(text) < 3:
                await update.message.reply_text(
                    "<b>@Username</b> @ belgisi bilan boshlanishi kerak!\n"
                    "Misol: @Username123\n\n"
                    "Qaytadan kiriting yoki /cancel",
                    parse_mode=ParseMode.HTML)
                return
        pending_orders[uid]["recipient"] = text
        context.user_data["state"]       = ST_WAITING_RECEIPT
        await send_payment_info(update, uid)
        return

    # ── Admin panel matn holatlar ──
    if state == ST_WAITING_ADMIN_ADD and is_owner(uid):
        await proc_admin_add(update, context, text)
        return

    if state == ST_WAITING_ADMIN_REMOVE and is_owner(uid):
        await proc_admin_remove(update, context, text)
        return

    if state == ST_WAITING_AD_TEXT and is_admin(uid):
        await proc_ad_text(update, context, text)
        return

    if ap_st and is_admin(uid):
        await ap_text_handler(update, context, text)
        return

    # ── Menyu tugmalari ──
    if text == "📱 Telegram Xizmatlar":
        await show_tg(update, context)
    elif text == "👤 Profil":
        await show_profile(update, context)
    elif text == "💬 Admin bilan bog'lanish":
        await show_contact(update, context)
    elif text == "⚙️ Boshqaruv paneli" and is_admin(uid):
        await ap_main(update, context)
    elif text == "📊 Statistika" and is_admin(uid):
        await show_stats(update, context)
    elif text == "📣 Reklama" and is_admin(uid):
        await show_ads(update, context)


async def send_payment_info(update, uid):
    order = pending_orders[uid]
    r_lbl = "Hamyon manzili" if order["type"] == "ton" else "@Username"
    kb    = [[InlineKeyboardButton("✅ To'lov qildim — Chek yuborish",
                                   callback_data="payment_done")]]
    await update.message.reply_text(
        f"<b>Buyurtma:</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"Mahsulot: <b>{order['product']}</b>\n"
        f"Narxi: <b>{fmt(order['price'])}</b>\n"
        f"{r_lbl}: <b>{order['recipient']}</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"Karta: <code>{CARD_NUMBER}</code>\n"
        f"Egasi: <b>{CARD_OWNER}</b>\n"
        f"Tel: <b>{CARD_PHONE}</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"To'lov qilgach chek rasmini yuborish uchun tugmani bosing:",
        parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))


async def payment_done_cb(update, context):
    q   = update.callback_query
    await q.answer()
    uid = q.from_user.id
    if uid not in pending_orders:
        await q.answer("Buyurtma topilmadi! /start bosing.", show_alert=True)
        return
    context.user_data["state"] = ST_WAITING_RECEIPT
    await q.message.reply_text(
        "To'lov chekini (skrinshotni) <b>rasm</b> ko'rinishida yuboring:\n\n"
        "/cancel — bekor qilish",
        parse_mode=ParseMode.HTML)


async def receive_photo(update, context):
    uid   = update.effective_user.id
    state = context.user_data.get("state")
    if state == ST_WAITING_RECEIPT:
        await recv_receipt(update, context)
    elif state == ST_WAITING_AD_PHOTO and is_admin(uid):
        await recv_ad_photo(update, context)


async def recv_receipt(update, context):
    uid = update.effective_user.id
    if context.user_data.get("state") != ST_WAITING_RECEIPT or uid not in pending_orders:
        return
    if not update.message.photo:
        await update.message.reply_text(
            "Faqat rasm (screenshot) yuboring!\n\n/cancel — bekor qilish")
        return

    order = pending_orders[uid]
    user  = update.effective_user
    photo = update.message.photo[-1]
    r_lbl = "Hamyon manzili" if order["type"] == "ton" else "@Username"

    await send_sticker(uid, STICKER_WAIT, context.bot)
    await update.message.reply_text(
        "To'lov tekshiruvda... Admin tekshirgach xabar beriladi.",
        reply_markup=main_kb(uid))

    kb = [[
        InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"approve_{uid}"),
        InlineKeyboardButton("❌ Rad etish",  callback_data=f"reject_{uid}"),
    ]]
    text = (
        f"<b>YANGI BUYURTMA!</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"Bo'lim: <b>{order['section']}</b>\n"
        f"Mahsulot: <b>{order['product']}</b>\n"
        f"Narxi: <b>{fmt(order['price'])}</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"Xaridor: <a href='tg://user?id={uid}'>{user.full_name}</a> "
        f"({'@'+user.username if user.username else 'username yoq'})\n"
        f"ID: <code>{uid}</code>\n"
        f"{r_lbl}: <b>{order['recipient']}</b>\n"
        f"Manba: <b>{'Sayt' if order.get('source') == 'website' else 'Bot'}</b>"
    )
    await broadcast_admins(context, text, photo=photo.file_id,
                           markup=InlineKeyboardMarkup(kb))
    context.user_data.pop("state", None)


async def admin_approve_cb(update, context):
    q = update.callback_query
    if not is_admin(q.from_user.id):
        await q.answer("Sizda huquq yo'q!", show_alert=True)
        return
    await q.answer("Tasdiqlandi!")
    tid   = int(q.data[8:])
    order = pending_orders.get(tid)
    if order:
        u = get_user(tid)
        u["orders"].append({
            "product":   order["product"],
            "price":     order["price"],
            "section":   order["section"],
            "recipient": order["recipient"],
        })
        u["total_spent"] = u.get("total_spent", 0) + order["price"]
        save_db()
        try:
            await send_sticker(tid, STICKER_SUCCESS, context.bot)
            await context.bot.send_message(
                chat_id=tid,
                text=(
                    f"To'lovingiz tasdiqlandi!\n\n"
                    f"Mahsulot: <b>{order['product']}</b>\n"
                    f"Oluvchi: <b>{order['recipient']}</b>\n\n"
                    f"Tez orada xizmat yetkaziladi. Rahmat!"
                ),
                parse_mode=ParseMode.HTML, reply_markup=main_kb(tid))
        except Exception as e:
            logger.error(f"Tasdiqlash xabarida xato: {e}")
    pending_orders.pop(tid, None)
    try:
        await q.edit_message_caption(
            caption=(q.message.caption or "") + f"\n\nTaskiqlandi — {q.from_user.full_name}",
            parse_mode=ParseMode.HTML)
    except Exception:
        pass


async def admin_reject_cb(update, context):
    q = update.callback_query
    if not is_admin(q.from_user.id):
        await q.answer("Sizda huquq yo'q!", show_alert=True)
        return
    await q.answer("Rad etildi!")
    tid   = int(q.data[7:])
    order = pending_orders.get(tid)
    try:
        await send_sticker(tid, STICKER_REJECT, context.bot)
        await context.bot.send_message(
            chat_id=tid,
            text=(
                f"To'lovingiz rad etildi.\n\n"
                f"Mahsulot: <b>{order['product'] if order else '—'}</b>\n\n"
                f"Muammo bo'lsa admin bilan bog'laning:\n{ADMIN_USERNAME}"
            ),
            parse_mode=ParseMode.HTML, reply_markup=main_kb(tid))
    except Exception as e:
        logger.error(f"Rad etish xabarida xato: {e}")
    pending_orders.pop(tid, None)
    try:
        await q.edit_message_caption(
            caption=(q.message.caption or "") + f"\n\nRad etildi — {q.from_user.full_name}",
            parse_mode=ParseMode.HTML)
    except Exception:
        pass


# ==================== BOSHQARUV PANELI ====================

async def ap_main(update, context):
    uid = update.effective_user.id
    if not is_admin(uid):
        return
    context.user_data.pop(AP_STATE, None)
    context.user_data.pop(AP_DATA,  None)
    kb = [
        [InlineKeyboardButton("💎 TG Paketlar",   callback_data="ap_tg"),
         InlineKeyboardButton("💱 Kurs sozlash",  callback_data="ap_rate")],
        [InlineKeyboardButton("🔦 Bo'lim holati", callback_data="ap_status")],
    ]
    if is_owner(uid):
        kb.append([InlineKeyboardButton("👮 Adminlar", callback_data="ap_admins")])

    is_cb = bool(update.callback_query)
    msg   = update.callback_query.message if is_cb else update.message
    fn    = msg.edit_text if is_cb else msg.reply_text
    await fn("⚙️ <b>Boshqaruv Paneli</b>\n\nNimani boshqarmoqchisiz?",
             parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))


# ─── TG PAKETLAR ───

async def ap_tg_cb(update, context):
    q    = update.callback_query
    await q.answer()
    pkgs = DB.get("tg_packages", [])
    lines = []
    for p in pkgs:
        meth = "Acc" if p.get("method") == "acc" else "@username"
        lines.append(
            f"• <b>{p['name']}</b> | {fmt(p['price'])} | "
            f"{tg_sec_name(p['section'])} | {meth}")
    kb = [
        [InlineKeyboardButton("➕ Paket qo'shish",  callback_data="ap_tg_add"),
         InlineKeyboardButton("🗑 Paket o'chirish", callback_data="ap_tg_del")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="ap_back_main")],
    ]
    text  = "💎 <b>TG Paketlar</b>\n━━━━━━━━━━━━━━\n"
    text += "\n".join(lines) if lines else "<i>Paket yo'q.</i>"
    text += "\n━━━━━━━━━━━━━━"
    await q.edit_message_text(text, parse_mode=ParseMode.HTML,
                              reply_markup=InlineKeyboardMarkup(kb))


async def ap_tg_add_cb(update, context):
    q = update.callback_query
    await q.answer()
    context.user_data[AP_DATA]  = {}
    context.user_data[AP_STATE] = "tg_add_sec"
    context.user_data.pop("state", None)
    kb = [
        [InlineKeyboardButton("💎 Premium",  callback_data="ap_tg_sec_prem")],
        [InlineKeyboardButton("⭐ Stars",     callback_data="ap_tg_sec_stars")],
        [InlineKeyboardButton("💠 TON",       callback_data="ap_tg_sec_ton")],
        [InlineKeyboardButton("🔙 Bekor",     callback_data="ap_tg")],
    ]
    await q.edit_message_text(
        "➕ <b>Yangi TG Paket</b>\n\n1️⃣ Bo'limni tanlang:",
        parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))


async def ap_tg_sec_cb(update, context):
    q   = update.callback_query
    await q.answer()
    sec = q.data.replace("ap_tg_sec_", "")
    if AP_DATA not in context.user_data:
        context.user_data[AP_DATA] = {}
    context.user_data[AP_DATA]["section"] = sec
    context.user_data[AP_STATE]           = "tg_add_meth"
    kb = [
        [InlineKeyboardButton("🔑 Acc kirib (login/parol kerak)", callback_data="ap_tg_meth_acc")],
        [InlineKeyboardButton("📨 @username orqali (gift)",       callback_data="ap_tg_meth_id")],
        [InlineKeyboardButton("🔙 Bekor", callback_data="ap_tg_add")],
    ]
    await q.edit_message_text(
        f"➕ <b>Yangi TG Paket</b>\n"
        f"Bo'lim: <b>{tg_sec_name(sec)}</b>\n\n"
        f"2️⃣ Usulni tanlang:",
        parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))


async def ap_tg_meth_cb(update, context):
    q    = update.callback_query
    await q.answer()
    meth = q.data.replace("ap_tg_meth_", "")
    if AP_DATA not in context.user_data:
        context.user_data[AP_DATA] = {}
    context.user_data[AP_DATA]["method"] = meth
    context.user_data[AP_STATE]          = AP_TG_ADD_NAME
    context.user_data.pop("state", None)
    sec      = context.user_data[AP_DATA].get("section", "?")
    meth_txt = "Acc kirib" if meth == "acc" else "@username orqali"
    await q.edit_message_text(
        f"➕ <b>Yangi TG Paket</b>\n"
        f"Bo'lim: <b>{tg_sec_name(sec)}</b>  |  Usul: <b>{meth_txt}</b>\n\n"
        f"3️⃣ Paket nomini yozing:\n"
        f"<i>Misol: 1 oylik Premium, 100 Stars, 5 TON</i>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Bekor", callback_data="ap_tg")]]))


async def ap_tg_del_cb(update, context):
    q    = update.callback_query
    await q.answer()
    pkgs = DB.get("tg_packages", [])
    if not pkgs:
        await q.answer("Paket yo'q!", show_alert=True)
        return
    kb = []
    for p in pkgs:
        kb.append([InlineKeyboardButton(
            f"🗑 {p['name']} ({tg_sec_name(p['section'])})",
            callback_data=f"ap_tg_del_{p['id']}")])
    kb.append([InlineKeyboardButton("🔙 Orqaga", callback_data="ap_tg")])
    await q.edit_message_text("🗑 O'chirish uchun paketni tanlang:",
                              reply_markup=InlineKeyboardMarkup(kb))


async def ap_tg_del_confirm_cb(update, context):
    q   = update.callback_query
    await q.answer("Paket o'chirildi!", show_alert=True)
    pid = int(q.data.replace("ap_tg_del_", ""))
    DB["tg_packages"] = [p for p in DB.get("tg_packages", []) if p["id"] != pid]
    save_db()
    pkgs  = DB.get("tg_packages", [])
    lines = []
    for p in pkgs:
        meth = "Acc" if p.get("method") == "acc" else "@username"
        lines.append(
            f"• <b>{p['name']}</b> | {fmt(p['price'])} | "
            f"{tg_sec_name(p['section'])} | {meth}")
    kb = [
        [InlineKeyboardButton("➕ Paket qo'shish",  callback_data="ap_tg_add"),
         InlineKeyboardButton("🗑 Paket o'chirish", callback_data="ap_tg_del")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="ap_back_main")],
    ]
    text  = "💎 <b>TG Paketlar</b>\n━━━━━━━━━━━━━━\n"
    text += "\n".join(lines) if lines else "<i>Paket yo'q.</i>"
    text += "\n━━━━━━━━━━━━━━"
    await q.edit_message_text(text, parse_mode=ParseMode.HTML,
                              reply_markup=InlineKeyboardMarkup(kb))


# ─── KURS SOZLASH ───

async def ap_rate_cb(update, context):
    q     = update.callback_query
    await q.answer()
    stars = DB.get("stars_rate", 250)
    ton   = DB.get("ton_rate",   17500)
    kb    = [
        [InlineKeyboardButton(f"⭐ Stars kursi: {stars:,} so'm", callback_data="ap_rate_stars")],
        [InlineKeyboardButton(f"💠 TON kursi: {ton:,} so'm",     callback_data="ap_rate_ton")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="ap_back_main")],
    ]
    await q.edit_message_text(
        "💱 <b>Valyuta Kurslari</b>\n\nO'zgartirish uchun tanlang:",
        parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))


async def ap_rate_stars_cb(update, context):
    q = update.callback_query
    await q.answer()
    context.user_data[AP_STATE] = "rate_stars"
    await q.edit_message_text(
        f"⭐ <b>Stars kursi</b>\n"
        f"Hozirgi: <b>{DB.get('stars_rate', 250):,} so'm</b>\n\n"
        f"Yangi kursni yozing:\n<i>Misol: 300</i>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Bekor", callback_data="ap_rate")]]))


async def ap_rate_ton_cb(update, context):
    q = update.callback_query
    await q.answer()
    context.user_data[AP_STATE] = "rate_ton"
    await q.edit_message_text(
        f"💠 <b>TON kursi</b>\n"
        f"Hozirgi: <b>{DB.get('ton_rate', 17500):,} so'm</b>\n\n"
        f"Yangi kursni yozing:\n<i>Misol: 20000</i>",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Bekor", callback_data="ap_rate")]]))


# ─── BO'LIM HOLATI ───

async def ap_status_cb(update, context):
    q      = update.callback_query
    await q.answer()
    status = DB.get("status", {})
    items  = [
        {"id": "prem",  "name": "💎 TG Premium"},
        {"id": "stars", "name": "⭐ TG Stars"},
        {"id": "ton",   "name": "💠 TON"},
    ]
    kb = []
    for it in items:
        ok    = status.get(it["id"], True)
        icon  = "✅" if ok else "❌"
        on_off = "Yoqiq" if ok else "O'chiq"
        label  = f"{icon} {it['name']} — {on_off}"
        kb.append([InlineKeyboardButton(label, callback_data=f"ap_toggle_{it['id']}")])
    kb.append([InlineKeyboardButton("🔙 Orqaga", callback_data="ap_back_main")])
    await q.edit_message_text(
        "🔦 <b>Bo'lim Holati</b>\n\nYoqish/o'chirish uchun bosing:",
        parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))


async def ap_toggle_cb(update, context):
    q      = update.callback_query
    await q.answer()
    sid    = q.data.replace("ap_toggle_", "")
    status = DB.setdefault("status", {})
    status[sid] = not status.get(sid, True)
    save_db()
    await ap_status_cb(update, context)


# ─── ADMINLAR ───

async def ap_admins_cb(update, context):
    q = update.callback_query
    await q.answer()
    if not is_owner(q.from_user.id):
        await q.answer("Faqat owner!", show_alert=True)
        return
    admins = DB.get("admin_ids", [])
    lines  = []
    for aid in admins:
        u  = DB.get("users", {}).get(str(aid), {})
        un = f"@{u['username']}" if u.get("username") else "username yo'q"
        lines.append(f"• <b>{u.get('name','?')}</b> | {un} | <code>{aid}</code>")
    kb = [
        [InlineKeyboardButton("➕ Admin qo'shish",  callback_data="ap_admin_add"),
         InlineKeyboardButton("➖ Admin o'chirish", callback_data="ap_admin_del")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="ap_back_main")],
    ]
    text  = "👮 <b>Adminlar</b>\n━━━━━━━━━━━━━━\n"
    text += "\n".join(lines) if lines else "<i>Admin yo'q.</i>"
    text += "\n━━━━━━━━━━━━━━"
    await q.edit_message_text(text, parse_mode=ParseMode.HTML,
                              reply_markup=InlineKeyboardMarkup(kb))


async def ap_admin_add_cb(update, context):
    q = update.callback_query
    await q.answer()
    context.user_data["state"] = ST_WAITING_ADMIN_ADD
    await q.message.reply_text(
        "Admin qo'shish uchun foydalanuvchi <b>ID</b> ini yuboring:\n\n"
        "/cancel — bekor qilish",
        parse_mode=ParseMode.HTML)


async def ap_admin_del_cb(update, context):
    q      = update.callback_query
    await q.answer()
    admins = DB.get("admin_ids", [])
    if not admins:
        await q.answer("Admin yo'q!", show_alert=True)
        return
    kb = []
    for aid in admins:
        u = DB.get("users", {}).get(str(aid), {})
        kb.append([InlineKeyboardButton(
            f"➖ {u.get('name', str(aid))}",
            callback_data=f"ap_adel_{aid}")])
    kb.append([InlineKeyboardButton("🔙 Orqaga", callback_data="ap_admins")])
    await q.edit_message_text("➖ O'chirish uchun adminni tanlang:",
                              reply_markup=InlineKeyboardMarkup(kb))


async def ap_admin_del_confirm_cb(update, context):
    q   = update.callback_query
    await q.answer("Admin o'chirildi!", show_alert=True)
    aid = int(q.data.replace("ap_adel_", ""))
    if aid in DB.get("admin_ids", []):
        DB["admin_ids"].remove(aid)
        save_db()
    await ap_admins_cb(update, context)


# ─── MATN HANDLER (admin panel) ───

async def ap_text_handler(update, context, text):
    ap_st = context.user_data.get(AP_STATE)
    uid   = update.effective_user.id

    if ap_st == "rate_stars":
        try:
            val = int(text.replace(" ", "").replace(",", ""))
            DB["stars_rate"] = val
            save_db()
            context.user_data.pop(AP_STATE, None)
            await update.message.reply_text(
                f"Stars kursi yangilandi: <b>{val:,} so'm</b>",
                parse_mode=ParseMode.HTML, reply_markup=main_kb(uid))
        except ValueError:
            await update.message.reply_text("Faqat raqam kiriting! Misol: 300")
        return

    if ap_st == "rate_ton":
        try:
            val = int(text.replace(" ", "").replace(",", ""))
            DB["ton_rate"] = val
            save_db()
            context.user_data.pop(AP_STATE, None)
            await update.message.reply_text(
                f"TON kursi yangilandi: <b>{val:,} so'm</b>",
                parse_mode=ParseMode.HTML, reply_markup=main_kb(uid))
        except ValueError:
            await update.message.reply_text("Faqat raqam kiriting! Misol: 20000")
        return

    if ap_st == AP_TG_ADD_NAME:
        if AP_DATA not in context.user_data:
            context.user_data[AP_DATA] = {}
        context.user_data[AP_DATA]["name"] = text
        context.user_data[AP_STATE]        = AP_TG_ADD_PRICE
        await update.message.reply_text(
            f"Nom: <b>{text}</b>\n\n"
            f"Narxini yozing (so'mda):\n<i>Misol: 42000</i>",
            parse_mode=ParseMode.HTML)
        return

    if ap_st == AP_TG_ADD_PRICE:
        try:
            price = int(text.replace(" ", "").replace(".", "").replace(",", ""))
        except ValueError:
            await update.message.reply_text("Faqat raqam kiriting! Misol: 42000")
            return
        ap_d = context.user_data.get(AP_DATA, {})
        if not ap_d.get("name") or not ap_d.get("section"):
            await update.message.reply_text(
                "Xato! Qaytadan boshlang.",
                reply_markup=main_kb(uid))
            context.user_data.pop(AP_STATE, None)
            context.user_data.pop(AP_DATA,  None)
            return
        pkg = {
            "id":      next_id(),
            "name":    ap_d["name"],
            "price":   price,
            "section": ap_d["section"],
            "method":  ap_d.get("method", "id"),
        }
        DB.setdefault("tg_packages", []).append(pkg)
        save_db()
        context.user_data.pop(AP_STATE, None)
        context.user_data.pop(AP_DATA,  None)
        meth_txt = "Acc kirib" if pkg["method"] == "acc" else "@username orqali"
        await update.message.reply_text(
            f"TG Paket qo'shildi!\n\n"
            f"Nom: <b>{pkg['name']}</b>\n"
            f"Narx: <b>{fmt(pkg['price'])}</b>\n"
            f"Bo'lim: <b>{tg_sec_name(pkg['section'])}</b>\n"
            f"Usul: <b>{meth_txt}</b>",
            parse_mode=ParseMode.HTML, reply_markup=main_kb(uid))
        return


# ==================== PROFIL / CONTACT / STATS ====================

async def show_profile(update, context):
    user  = update.effective_user
    store = get_user(user.id)
    prem  = getattr(user, "is_premium", False) or False
    uname = ("@" + user.username) if user.username else "Yo'q"
    await update.message.reply_text(
        f"<b>Profilingiz</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"ID: <code>{user.id}</code>\n"
        f"Ism: <b>{user.full_name}</b>\n"
        f"Username: <b>{uname}</b>\n"
        f"Premium: <b>{'✅' if prem else '❌'}</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"Xaridlar: <b>{len(store.get('orders', []))} ta</b>\n"
        f"Sarflangan: <b>{fmt(store.get('total_spent', 0))}</b>",
        parse_mode=ParseMode.HTML, reply_markup=main_kb(user.id))


async def show_contact(update, context):
    kb = [[InlineKeyboardButton("💬 Adminga yozish", url=ADMIN_TG_LINK)]]
    await update.message.reply_text(
        f"Admin: {ADMIN_USERNAME}\n\nSavol yoki muammo bo'lsa yozing:",
        parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb))


async def show_stats(update, context):
    if not is_admin(update.effective_user.id):
        return
    users  = DB.get("users", {})
    total  = len(users)
    orders = sum(len(u.get("orders", [])) for u in users.values())
    income = sum(u.get("total_spent", 0) for u in users.values())
    text   = (
        f"<b>Statistika</b>\n"
        f"━━━━━━━━━━━━━━\n"
        f"Foydalanuvchilar: <b>{total}</b>\n"
        f"Jami xaridlar: <b>{orders}</b>\n"
        f"Jami daromad: <b>{fmt(income)}</b>\n"
        f"━━━━━━━━━━━━━━\n"
    )
    for uid_s, u in list(users.items())[:30]:
        un    = "@" + u["username"] if u.get("username") else "username yo'q"
        spent = fmt(u.get("total_spent", 0))
        n_ord = len(u.get("orders", []))
        text += f"• <b>{u.get('name','?')}</b> | {un} | {n_ord} xarid | {spent}\n"
    if total > 30:
        text += f"\n<i>...yana {total-30} ta</i>"
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


# ==================== ADMIN QO'SHISH ====================

async def proc_admin_add(update, context, text):
    try:
        new_id = int(text.strip())
        admins = DB.setdefault("admin_ids", [])
        if new_id in admins:
            await update.message.reply_text(
                f"<code>{new_id}</code> allaqachon admin!",
                parse_mode=ParseMode.HTML)
        else:
            admins.append(new_id)
            save_db()
            await update.message.reply_text(
                f"<code>{new_id}</code> admin qilindi!",
                parse_mode=ParseMode.HTML, reply_markup=main_kb(update.effective_user.id))
    except ValueError:
        await update.message.reply_text("Faqat raqamli ID kiriting!")
    finally:
        context.user_data.pop("state", None)


async def proc_admin_remove(update, context, text):
    try:
        rem_id = int(text.strip())
        if rem_id in DB.get("admin_ids", []):
            DB["admin_ids"].remove(rem_id)
            save_db()
            await update.message.reply_text(
                f"<code>{rem_id}</code> admin ro'yxatidan o'chirildi!",
                parse_mode=ParseMode.HTML, reply_markup=main_kb(update.effective_user.id))
        else:
            await update.message.reply_text("Bu ID adminlar ro'yxatida yo'q!")
    except ValueError:
        await update.message.reply_text("Faqat raqamli ID kiriting!")
    finally:
        context.user_data.pop("state", None)


# ==================== REKLAMA ====================

async def show_ads(update, context):
    if not is_admin(update.effective_user.id):
        return
    kb = [[InlineKeyboardButton("📝 Yangi reklama", callback_data="create_ad")]]
    await update.message.reply_text(
        "Barcha foydalanuvchilarga xabar yuborish:",
        reply_markup=InlineKeyboardMarkup(kb))


async def create_ad_cb(update, context):
    q = update.callback_query
    await q.answer()
    if not is_admin(q.from_user.id):
        return
    context.user_data["state"]    = ST_WAITING_AD_TEXT
    context.user_data["ad_draft"] = {}
    await q.message.reply_text("Reklama matnini yozing:\n\n/cancel — bekor qilish")


async def proc_ad_text(update, context, text):
    context.user_data["ad_draft"] = {"text": text}
    context.user_data["state"]    = ST_WAITING_AD_PHOTO
    await update.message.reply_text("Rasm yuboring yoki /skip (rasmsiz):")


async def cmd_skip(update, context):
    if context.user_data.get("state") != ST_WAITING_AD_PHOTO:
        return
    await finalize_ad(update, context, None)


async def recv_ad_photo(update, context):
    await finalize_ad(update, context, update.message.photo[-1].file_id)


async def finalize_ad(update, context, photo_id):
    uid   = update.effective_user.id
    draft = context.user_data.get("ad_draft", {})
    text  = draft.get("text", "")
    ad_id = str(next_id())
    DB.setdefault("pending_ads", {})[ad_id] = {
        "text": text, "photo": photo_id,
        "from_id": uid, "from_name": update.effective_user.full_name,
        "status": "pending",
    }
    save_db()
    context.user_data.pop("state", None)
    context.user_data.pop("ad_draft", None)
    await update.message.reply_text(
        "Reklama owner'ga yuborildi. Tasdiqlashini kuting.",
        reply_markup=main_kb(uid))
    kb = [[
        InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"adv_approve_{ad_id}"),
        InlineKeyboardButton("❌ Rad etish",  callback_data=f"adv_reject_{ad_id}"),
    ]]
    body = (
        f"Yangi reklama\n"
        f"{DB['pending_ads'][ad_id]['from_name']} | <code>{uid}</code>\n\n"
        f"{text}"
    )
    if photo_id:
        await context.bot.send_photo(
            chat_id=OWNER_ID, photo=photo_id,
            caption=body, parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(kb))
    else:
        await context.bot.send_message(
            chat_id=OWNER_ID, text=body,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(kb))


async def adv_approve_cb(update, context):
    q = update.callback_query
    if not is_owner(q.from_user.id):
        await q.answer("Faqat owner!", show_alert=True)
        return
    await q.answer()
    ad_id = q.data[12:]
    ad    = DB.get("pending_ads", {}).get(ad_id)
    if not ad:
        return
    ad["status"] = "approved"
    save_db()
    sent = 0
    for uid_s in list(DB.get("users", {}).keys()):
        try:
            if ad.get("photo"):
                await context.bot.send_photo(
                    chat_id=int(uid_s), photo=ad["photo"],
                    caption=ad["text"], parse_mode=ParseMode.HTML)
            else:
                await context.bot.send_message(
                    chat_id=int(uid_s), text=ad["text"],
                    parse_mode=ParseMode.HTML)
            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass
    try:
        caption = (q.message.caption or "") + f"\n\nTaskiqlandi. {sent} ta yuborildi."
        await q.edit_message_caption(caption=caption, parse_mode=ParseMode.HTML)
    except Exception:
        pass


async def adv_reject_cb(update, context):
    q = update.callback_query
    if not is_owner(q.from_user.id):
        await q.answer("Faqat owner!", show_alert=True)
        return
    await q.answer()
    ad_id = q.data[11:]
    ad    = DB.get("pending_ads", {}).get(ad_id)
    if ad:
        try:
            await context.bot.send_message(
                chat_id=ad["from_id"], text="Reklamangiz rad etildi.")
        except Exception:
            pass
        ad["status"] = "rejected"
        save_db()
    try:
        caption = (q.message.caption or "") + "\n\nRad etildi."
        await q.edit_message_caption(caption=caption, parse_mode=ParseMode.HTML)
    except Exception:
        pass


# ==================== NOOP / BACK ====================

async def noop_cb(update, context):
    await update.callback_query.answer(
        "Bu bo'lim hozir mavjud emas 🔜", show_alert=True)


async def back_cb(update, context):
    q = update.callback_query
    await q.answer()
    d = q.data
    if d == "back_tg":
        await show_tg(update, context)
    elif d == "ap_back_main":
        await ap_main(update, context)


# ==================== MAIN ====================

def main():
    load_db()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",  cmd_start))
    app.add_handler(CommandHandler("cancel", cmd_cancel))
    app.add_handler(CommandHandler("skip",   cmd_skip))

    # TG xizmatlar
    app.add_handler(CallbackQueryHandler(tg_cat_cb,   pattern=r"^tg_(prem|stars|ton)$"))
    app.add_handler(CallbackQueryHandler(prem_acc_cb, pattern=r"^prem_acc$"))
    app.add_handler(CallbackQueryHandler(prem_id_cb,  pattern=r"^prem_id$"))

    # Sotib olish
    app.add_handler(CallbackQueryHandler(buy_tg_cb, pattern=r"^buy_(tg_|sq_|tq_)"))

    # To'lov
    app.add_handler(CallbackQueryHandler(payment_done_cb,  pattern=r"^payment_done$"))
    app.add_handler(CallbackQueryHandler(admin_approve_cb, pattern=r"^approve_\d+$"))
    app.add_handler(CallbackQueryHandler(admin_reject_cb,  pattern=r"^reject_\d+$"))

    # Boshqaruv paneli — TG paketlar
    app.add_handler(CallbackQueryHandler(ap_tg_cb,             pattern=r"^ap_tg$"))
    app.add_handler(CallbackQueryHandler(ap_tg_add_cb,         pattern=r"^ap_tg_add$"))
    app.add_handler(CallbackQueryHandler(ap_tg_sec_cb,         pattern=r"^ap_tg_sec_"))
    app.add_handler(CallbackQueryHandler(ap_tg_meth_cb,        pattern=r"^ap_tg_meth_"))
    app.add_handler(CallbackQueryHandler(ap_tg_del_cb,         pattern=r"^ap_tg_del$"))
    app.add_handler(CallbackQueryHandler(ap_tg_del_confirm_cb, pattern=r"^ap_tg_del_\d+$"))

    # Boshqaruv paneli — kurs, holat, adminlar
    app.add_handler(CallbackQueryHandler(ap_rate_cb,       pattern=r"^ap_rate$"))
    app.add_handler(CallbackQueryHandler(ap_rate_stars_cb, pattern=r"^ap_rate_stars$"))
    app.add_handler(CallbackQueryHandler(ap_rate_ton_cb,   pattern=r"^ap_rate_ton$"))
    app.add_handler(CallbackQueryHandler(ap_status_cb,     pattern=r"^ap_status$"))
    app.add_handler(CallbackQueryHandler(ap_toggle_cb,     pattern=r"^ap_toggle_"))

    app.add_handler(CallbackQueryHandler(ap_admins_cb,           pattern=r"^ap_admins$"))
    app.add_handler(CallbackQueryHandler(ap_admin_add_cb,        pattern=r"^ap_admin_add$"))
    app.add_handler(CallbackQueryHandler(ap_admin_del_cb,        pattern=r"^ap_admin_del$"))
    app.add_handler(CallbackQueryHandler(ap_admin_del_confirm_cb,pattern=r"^ap_adel_"))

    # Reklama
    app.add_handler(CallbackQueryHandler(create_ad_cb,   pattern=r"^create_ad$"))
    app.add_handler(CallbackQueryHandler(adv_approve_cb, pattern=r"^adv_approve_"))
    app.add_handler(CallbackQueryHandler(adv_reject_cb,  pattern=r"^adv_reject_"))

    # Util
    app.add_handler(CallbackQueryHandler(noop_cb, pattern=r"^noop$"))
    app.add_handler(CallbackQueryHandler(back_cb, pattern=r"^(back_tg|ap_back_main)$"))

    # Media va matn
    app.add_handler(MessageHandler(filters.PHOTO,                   receive_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_text))

    logger.info("Bot ishga tushdi!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
