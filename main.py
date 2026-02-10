from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
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
    group_settings[group_id]["song_requests"] = "off"

    await update.message.reply_text(
        "⛔ Přijímání písniček bylo vypnuto"
    )

# Kontrola zprav
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text.lower()

    settings = group_settings.get(chat_id)
    if not settings or settings["song_requests"] == "off":
        await update.message.reply_text(
            "⛔ Přání písniček jsou momentálně uzavřena."
        )
        return

    if settings["event_type"] == "public":
        if "tidal.com" not in text:
            await update.message.reply_text(
                "⛔ Veřejná akce přijímá pouze odkazy z TIDAL.\n"
                "Zkopíruj prosím odkaz z aplikace TIDAL."
            )
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

        "Pro možnost poslání žádosti o písničku na přání je nutné potvrdit, že sledujete můj INSTA profil"
        "Na můj INSTA profil se dostanete zde: www.pasek-art.cz"
    )

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("public", set_public))
app.add_handler(CommandHandler("private", set_private))
app.add_handler(CommandHandler("stop", stop_requests))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
