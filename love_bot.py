from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, filters, ContextTypes,
    ConversationHandler
)
import os

TOKEN = os.getenv("BOT_TOKEN")
START, QUESTION = range(2)

QUESTIONS = [
    {"type": "fact", "question": "Где было наше первое свидание?", "answer": "парк Горького"},
    {"type": "open", "question": "Назови мою самую смешную привычку?"},
]

user_progress = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_progress[user_id] = 0
    await update.message.reply_text("С Днем Рождения, любимый! 🎉 Готов к приключению? Напиши 'Да' ✨")
    return START

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.lower() in ["да", "конечно"]:
        return await ask_question(update, context)
    await update.message.reply_text("Ответь 'Да', чтобы начать 🥰")
    return START

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    step = user_progress.get(user_id, 0)
    if step >= len(QUESTIONS):
        await update.message.reply_text("Все вопросы пройдены! 🎉")
        return ConversationHandler.END
    q = QUESTIONS[step]
    await update.message.reply_text(q["question"])
    return QUESTION

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    step = user_progress.get(user_id, 0)
    q = QUESTIONS[step]
    text = update.message.text or ""

    if q["type"] == "fact":
        if text.lower() == q["answer"].lower():
            await update.message.reply_text("Верно! 😘")
        else:
            await update.message.reply_text(f"Правильный ответ был: {q['answer']} 😉")
    elif q["type"] == "open":
        await update.message.reply_text("Запомню это ❤️")

    ticket_number = step + 1
    ticket_path = f"tickets/ticket_{ticket_number}.jpg"
    if os.path.exists(ticket_path):
        await update.message.reply_photo(InputFile(ticket_path), caption=f"🎟 Билет №{ticket_number}\nБессрочный 💌")

    user_progress[user_id] = step + 1
    return await ask_question(update, context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пока ❤️")
    return ConversationHandler.END

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_start)],
            QUESTION: [MessageHandler(filters.ALL, handle_answer)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()