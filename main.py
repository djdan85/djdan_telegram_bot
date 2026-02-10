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

cursor.execute("""
CREATE TABLE IF NOT EXISTS verified_users (
    user_id INTEGER,
    group_id INTEGER,
    verified_at TEXT,
    PRIMARY KEY (user_id, group_id)
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
        "Tento bot slouží pro zadávání písniček na přání.\n"
        "Na veřejných akcích je nutné potvrdit sledování Instagramu "
        "zasláním screenshotu.\n\n"
        "Ověření platí pouze po dobu konání akce."
    )

    if user_id in ADMIN_IDS:
        await update.message.reply_text(
            "🎛️ Admin menu – správa akce",
            reply_markup=admin_menu()
        )

# =========================
# ADMIN BUTTONS
# =========================
async def handle_buttons(update: Update, con_
