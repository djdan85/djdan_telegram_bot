from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

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

app.run_polling()
