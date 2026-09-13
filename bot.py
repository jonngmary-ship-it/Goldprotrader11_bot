import logging
import os
import re

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Hi! I'm Word Counter Bot.\n\n"
        "Send me any text and I'll tell you:\n"
        "• Word count\n"
        "• Character count (with and without spaces)\n"
        "• Sentence count\n\n"
        "Just type or paste text below to try it out!"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Just send me any message and I'll count it for you.\n"
        "Commands:\n"
        "/start - welcome message\n"
        "/help - show this help"
    )


async def count_words(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text

    if not text or not text.strip():
        await update.message.reply_text("Send me some text and I'll count it!")
        return

    words = text.split()
    word_count = len(words)
    char_count_with_spaces = len(text)
    char_count_no_spaces = len(text.replace(" ", "").replace("\n", ""))
    sentence_count = len(re.findall(r"[.!?]+", text)) or (1 if text.strip() else 0)

    reply = (
        "📊 *Text stats*\n\n"
        f"📝 Words: {word_count}\n"
        f"🔤 Characters (with spaces): {char_count_with_spaces}\n"
        f"🔡 Characters (no spaces): {char_count_no_spaces}\n"
        f"📖 Sentences: {sentence_count}"
    )

    await update.message.reply_text(reply, parse_mode="Markdown")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Update %s caused error %s", update, context.error)


def main() -> None:
    if not TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN environment variable is not set. "
            "Set it in Railway's Variables tab."
        )

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, count_words)
    )
    application.add_error_handler(error_handler)

    logger.info("Bot starting with polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
