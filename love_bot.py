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
    {"type": "task", "question": "Сфоткай вид из окна и пришли мне!"},
    {"type": "choice", "question": "Что мы будем делать в первую очередь:\nA) Пицца и ужастики 🍕\nB) Гулять под дождем 🌧\nC) Свой вариант?"},
    {"type": "secret", "question": "СЕКРЕТНОЕ ЗАДАНИЕ: Напиши, во сколько ты будешь дома вечером 🕐"}
]

user_progress = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_progress[user_id] = 0
    await update.message.reply_text("С Днем Рождения, любимый! 🎉 Твой Личный Ассистент Любви активирован! Готов к приключению? Напиши 'Да' ✨")
    return START

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.lower() in ["да", "конечно"]:
        return await ask_question(update, context)
    await update.message.reply_text("Ответь 'Да', чтобы начать приключение 🥰")
    return START

async def ask_question(update, context):
    user_id = update.effective_user.id
    step = user_progress.get(user_id, 0)
    if step >= len(QUESTIONS):
        await update.message.reply_text("Все вопросы пройдены! 🎉 Ожидай сюрприза 🎂")
        return ConversationHandler.END
    q = QUESTIONS[step]
    await update.message.reply_text(q["question"])
    return QUESTION

async def handle_answer(update, context):
    user_id = update.effective_user.id
    step = user_progress.get(user_id, 0)
    q = QUESTIONS[step]
    user_text = update.message.text or ""

    if q["type"] == "fact":
        if user_text.lower() == q["answer"].lower():
            await update.message.reply_text("Верно! Ты меня знаешь 😘")
        else:
            await update.message.reply_text(f"Хм, правильный ответ был: {q['answer']} 😉")
    elif q["type"] == "open":
        await update.message.reply_text("Интересно! Я это запомню ❤️")
    elif q["type"] == "task":
        await update.message.reply_text("Красивый вид! Люблю твой город 🌇")
    elif q["type"] == "choice":
        await update.message.reply_text("Ха-ха, отличное решение 😍")
    elif q["type"] == "secret":
        await update.message.reply_text("Принято! Подготовься к волшебству в это время 🎁")
        return ConversationHandler.END

    ticket_number = step + 1
    ticket_path = f"tickets/ticket_{ticket_number}.jpg"
    if os.path.exists(ticket_path):
        await update.message.reply_photo(InputFile(ticket_path), caption=f"🎟 Билет №{ticket_number}\n\nБессрочный, по любви 💌")

    user_progress[user_id] = step + 1
    if step + 1 < len(QUESTIONS):
        await update.message.reply_text("Немного отдохни... Скоро следующий билет! ✨")
    return await ask_question(update, context)

async def cancel(update, context):
    await update.message.reply_text("До встречи, Любовь ❤️")
    return ConversationHandler.END

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            START: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_start)],
            QUESTION: [MessageHandler(filters.ALL, handle_answer)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(conv)
    app.run_polling()
