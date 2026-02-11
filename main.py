from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import os
import sqlite3
import random

# =========================
# DATABASE
# =========================
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS groups (
    group_id INTEGER PRIMARY KEY,
    event_type TEXT,
    song_requests TEXT
)
""")

conn.commit()

# =========================
# CONFIG
# =========================
ADMIN_IDS = [5724886738]  # TVOJE TELEGRAM ID

# =========================
# ADMIN MENU
# =========================
def admin_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎉 Veřejná akce", callback_data="event_public")],
        [InlineKeyboardButton("🔒 Soukromá akce", callback_data="event_private")],
        [InlineKeyboardButton("⛔ Pozastavit přání", callback_data="pause_requests")],
        [InlineKeyboardButton("🧹 Reset akce", callback_data="reset_confirm")],
        [InlineKeyboardButton("📣 Rychlé zprávy", callback_data="broadcast_menu")]
    ])

# =========================
# START (DM)
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    await update.message.reply_text(
        "Ahoj!\n"
        "Zdraví Tě DJ.DAN 🎧\n\n"
        "Tento bot slouží pro zasílání písniček na přání.\n"
        "Přijímám pouze odkazy z TIDALu 🎶\n\n"
        "Jak postupovat:\n"
        "1️⃣ Otevři TIDAL.com\n"
        "2️⃣ Najdi písničku, která se ti líbí\n"
        "3️⃣ Klikni na Sdílet → Kopírovat odkaz\n"
        "4️⃣ Odkaz pošli do skupiny a můžeš přidat krátké věnování pro koho to je\n\n"
        "DJ vybírá a mixuje – ne všechna přání musí zaznít 😉\n\n"
        "👉 instagram.com/pasekart.cz"
    )

    if user_id in ADMIN_IDS:
        await update.message.reply_text(
            "🎛️ Admin menu – správa akce",
            reply_markup=admin_menu()
        )

# =========================
# ADMIN BUTTONS
# =========================
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id not in ADMIN_IDS:
        return

    chat_id = query.message.chat_id
    data = query.data

    if data == "event_public":
        cursor.execute(
            "INSERT OR REPLACE INTO groups VALUES (?, ?, ?)",
            (chat_id, "public", "on")
        )
        conn.commit()
        await query.message.reply_text("🎉 Nastavena VEŘEJNÁ AKCE")

    elif data == "event_private":
        cursor.execute(
            "INSERT OR REPLACE INTO groups VALUES (?, ?, ?)",
            (chat_id, "private", "on")
        )
        conn.commit()
        await query.message.reply_text("🔒 Nastavena SOUKROMÁ AKCE")

    elif data == "pause_requests":
        cursor.execute(
            "UPDATE groups SET song_requests='off' WHERE group_id=?",
            (chat_id,)
        )
        conn.commit()
        await query.message.reply_text("⛔ Přání dočasně pozastavena")

    elif data == "reset_confirm":
        cursor.execute("DELETE FROM groups WHERE group_id=?", (chat_id,))
        conn.commit()
        await query.message.reply_text("🧹 Akce resetována")

    elif data == "broadcast_menu":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎶 Přání povoleny", callback_data="msg_on")],
            [InlineKeyboardButton("⏸️ Přání omezené", callback_data="msg_limited")],
            [InlineKeyboardButton("⏰ Končí za hodinu", callback_data="msg_last")],
            [InlineKeyboardButton("❤️ Poděkování", callback_data="msg_thanks")]
        ])
        await query.message.reply_text("📣 Vyber zprávu:", reply_markup=keyboard)

    elif data.startswith("msg_"):
        messages = {
            "msg_on": "🎶 Písničky na přání jsou povolené! 🎧",
            "msg_limited": "⏸️ Přání jsou na chvilku omezené – díky za pochopení 🙌",
            "msg_last": "⏰ Přání budou končit zhruba za hodinu – pospěš si 🎶",
            "msg_thanks": "❤️ DJ.DAN děkuje všem! Byli jste skvělí 🎧🔥"
        }
        await context.bot.send_message(chat_id=chat_id, text=messages[data])

# =========================
# MESSAGE HANDLER (GROUP)
# =========================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text.lower()

    cursor.execute(
        "SELECT event_type, song_requests FROM groups WHERE group_id=?",
        (chat_id,)
    )
    row = cursor.fetchone()

    if not row or row[1] == "off":
        return

    if "tidal.com" not in text:
        try:
            await update.message.delete()
        except:
            pass

        await context.bot.send_message(
            chat_id=chat_id,
            text="⛔ Přijímám pouze odkazy z TIDAL.\n"
                 "Zkopíruj prosím odkaz z aplikace nebo z webu TIDAL 🎶"
        )
        return

responses = [
    "🎶 Díky za správný odkaz!\nZa chvilku se na to kouknu 👀\nDJ.DAN 😁👌",

    "🔥 Odkaz dorazil správně!\nNech to na mě 🎧\nDJ.DAN",

    "🎧 Nice choice!\nMrknu na to a uvidíme, kam se to hodí 😉\n"
    "Více akcí a zákulisí 👉 https://instagram.com/pasekart.cz\n"
    "DJ.DAN",

    "✅ TIDAL link OK!\nDíky za tip, jede se dál 🎶\nDJ.DAN",

    "😎 Přání přijato!\nSprávný odkaz = správný vibe 🔥\n"
    "Sleduj mě i na IG 👉 https://instagram.com/pasekart.cz\n"
    "DJ.DAN",

    "🎶 Díky za tip!\nHudba se už chystá 🎧\nDJ.DAN",

    "👌 Máme to!\nTIDAL odkaz sedí, mrknu na to 👀\nDJ.DAN",

    "🎧 To zní zajímavě!\nNech to projet playlistem 😁\n"
    "Další akce najdeš zde 👉 https://instagram.com/pasekart.cz\n"
    "DJ.DAN",

    "🔥 Správný link!\nHudební kontrola probíhá 🎶\nDJ.DAN",

    "😁 Odkaz v cajku!\nDíky za přání a jedeme dál 🎧\n"
    "Follow pro další party 👉 https://instagram.com/pasekart.cz\n"
    "DJ.DAN"
]


    await update.message.reply_text(random.choice(responses))

# =========================
# RUN APP
# =========================
TOKEN = os.getenv("BOT_TOKEN")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_buttons))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
