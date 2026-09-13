import logging
import os
import random

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

QUESTIONS = [
    {
        "question": "What is the capital of France?",
        "options": ["Berlin", "Paris", "Madrid", "Rome"],
        "correct": 1,
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["Venus", "Mars", "Jupiter", "Saturn"],
        "correct": 1,
    },
    {
        "question": "Who wrote 'Romeo and Juliet'?",
        "options": ["Charles Dickens", "Mark Twain", "William Shakespeare", "Leo Tolstoy"],
        "correct": 2,
    },
    {
        "question": "What is the largest ocean on Earth?",
        "options": ["Atlantic", "Indian", "Arctic", "Pacific"],
        "correct": 3,
    },
    {
        "question": "How many continents are there?",
        "options": ["5", "6", "7", "8"],
        "correct": 2,
    },
    {
        "question": "What is the chemical symbol for gold?",
        "options": ["Go", "Gd", "Au", "Ag"],
        "correct": 2,
    },
    {
        "question": "Which country hosted the 2016 Summer Olympics?",
        "options": ["China", "UK", "Brazil", "Japan"],
        "correct": 2,
    },
    {
        "question": "What is the smallest prime number?",
        "options": ["0", "1", "2", "3"],
        "correct": 2,
    },
]

user_scores: dict[int, dict[str, int]] = {}
user_current_question: dict[int, dict] = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🧠 Welcome to Quiz Bot!\n\n"
        "Test your knowledge with fun trivia questions.\n\n"
        "Commands:\n"
        "/quiz - get a new question\n"
        "/score - see your score\n"
        "/help - show this help\n\n"
        "Send /quiz to start!"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🧠 Quiz Bot Commands:\n"
        "/quiz - get a new trivia question\n"
        "/score - check your current score\n"
        "/help - show this message"
    )


async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    question_data = random.choice(QUESTIONS)
    user_current_question[user_id] = question_data

    options = question_data["options"]
    keyboard = [
        [InlineKeyboardButton(opt, callback_data=str(i))]
        for i, opt in enumerate(options)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"❓ {question_data['question']}",
        reply_markup=reply_markup,
    )


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    question_data = user_current_question.get(user_id)
    if not question_data:
        await query.edit_message_text("This question expired. Send /quiz for a new one!")
        return

    selected_index = int(query.data)
    correct_index = question_data["correct"]
    options = question_data["options"]

    scores = user_scores.setdefault(user_id, {"score": 0, "answered": 0})
    scores["answered"] += 1

    if selected_index == correct_index:
        scores["score"] += 1
        result_text = "✅ Correct!"
    else:
        result_text = f"❌ Wrong! The correct answer was: {options[correct_index]}"

    await query.edit_message_text(
        f"❓ {question_data['question']}\n\n"
        f"{result_text}\n\n"
        f"Score: {scores['score']}/{scores['answered']}\n\n"
        "Send /quiz for another question!"
    )

    user_current_question.pop(user_id, None)


async def show_score(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    scores = user_scores.get(user_id, {"score": 0, "answered": 0})
    await update.message.reply_text(
        f"📊 Your score: {scores['score']}/{scores['answered']}\n"
        "Send /quiz to keep playing!"
    )


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
    application.add_handler(CommandHandler("quiz", send_question))
    application.add_handler(CommandHandler("score", show_score))
    application.add_handler(CallbackQueryHandler(handle_answer))
    application.add_error_handler(error_handler)

    logger.info("Quiz bot starting with polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
