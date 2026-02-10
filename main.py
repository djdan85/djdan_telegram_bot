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
import datetime

conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS groups (
    group_id INTEGER PRIMARY KEY,
    event_type TEXT,
    song_requests TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS verified_users (
    user_id INTEGER,
    group_id INTEGER,
    verified_at TEXT,
    PRIMARY KEY (user_id, group_id)
)
""")

conn.commit()

ADMIN_IDS = [5724886738]  # TVOJE TELEGRAM ID
def admin_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎉 Veřejná akce", callback_data="event_public")],
        [InlineKeyboardButton("🔒 Soukromá akce", callback_data="event_private")],
        [InlineKeyboardButton("⛔ Pozastavit přání", callback_data="pause_requests")],
        [InlineKeyboardButton("🧹 Reset akce", callback_data="reset_confirm")],
        [InlineKeyboardButton("📣 Rychlé zprávy", callback_data="broadcast_menu")]
    ])
async def on_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.id in ADMIN_IDS:
            await context.bot.send_message(
                chat_id=member.id,
                text="🎛️ Správa akce – DJ.DAN\nVyber, co chceš nastavit:",
                reply_markup=admin_menu()
            )
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if user_id not in ADMIN_IDS:
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
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Ano, resetovat", callback_data="reset_yes")],
            [InlineKeyboardButton("❌ Zrušit", callback_data="reset_no")]
        ])
        await query.message.reply_text(
            "⚠️ Opravdu chceš resetovat akci?",
            reply_markup=keyboard
        )

    elif data == "reset_yes":
        cursor.execute("DELETE FROM verified_users WHERE group_id=?", (chat_id,))
        conn.commit()
        await query.message.reply_text("🧹 Akce resetována – ověření smazána")

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

group_settings = {}
ADMIN_IDS = [5724886738]  # ← sem dáte SVŮJ Telegram user_id

# verejna akce
async def set_public(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    group_id = update.effective_chat.id
    group_settings[group_id] = {
        "event_type": "public",
        "song_requests": "on"
    }

    await update.message.reply_text(
        "🎉 Nastaveno: VEŘEJNÁ AKCE\n"
        "• Přijímám pouze odkazy z TIDAL\n"
    )
# soukroma akce
async def set_private(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    group_id = update.effective_chat.id
    group_settings[group_id] = {
        "event_type": "private",
        "song_requests": "on"
    }

    await update.message.reply_text(
        "🔒 Nastaveno: SOUKROMÁ AKCE\n"
        "• Přání jsou volná\n"
    )
# vypnuti prani
async def stop_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return

    group_id = update.effective_chat.id

    if group_id not in group_settings:
        group_settings[group_id] = {
            "event_type": "unset",
            "song_requests": "off"
        }
    else:
        group_settings[group_id]["song_requests"] = "off"

    await update.message.reply_text(
        "⛔ Přijímání písniček bylo vypnuto"
    )


# Kontrola zprav
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Ahoj!\nZdraví Tě DJ.DAN 🎧\n\n"
        "Pro veřejnou akci je nutné potvrdit sledování Instagramu "
        "zasláním screenshotu. Ověření platí pouze po dobu akce."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    text = update.message.text.lower()

    cursor.execute("SELECT event_type, song_requests FROM groups WHERE group_id=?", (chat_id,))
    row = cursor.fetchone()
    if not row or row[1] == "off":
        return

    event_type = row[0]

    if event_type == "public":
        cursor.execute(
            "SELECT 1 FROM verified_users WHERE user_id=? AND group_id=?",
            (user_id, chat_id)
        )
        if not cursor.fetchone():
            await update.message.reply_text(
                "📸 Pro veřejnou akci pošli screenshot, že sleduješ @pasekart.cz"
            )
            return

        if "tidal.com" not in text:
            await update.message.reply_text("⛔ Přijímám pouze odkazy z TIDAL.")
            return

    await update.message.reply_text("🎶 Přání přijato, díky!")


TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Ahoj!\n"
        "Zdraví Tě DJ.DAN 🎧\n\n"
        "Pro usnadnění zadávání písniček na přání jsem vytvořil tohoto bota.\n\n"
        "Tento bot slouží jako návod pro výběr a sdílení hudby "
        "POUZE z TIDALu, protože TIDAL využívám k hudební produkci.\n\n"
        "Jak postupovat:\n"
        "1️⃣ Otevři TIDAL.com\n"
        "2️⃣ Najdi písničku, která se ti líbí\n"
        "3️⃣ Klikni na Sdílet → Kopírovat odkaz\n"
        "4️⃣ Odkaz pošli sem do skupiny\n\n"
        "Doporučení:\n"
        "• vybírej skladby, které mají energii na hraní\n"
        "• klidně připiš krátký komentář nebo přání 🎶"

        "• klidně připiš krátký komentář nebo přání 🎶\n\n"
        "Pro možnost poslání žádosti o písničku na přání je nutné potvrdit, že sledujete můj INSTA profil.\n"
        "Na můj INSTA profil se dostanete zde: https://www.pasek-art.cz"

    )

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, on_new_member))
app.add_handler(CallbackQueryHandler(handle_buttons))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
