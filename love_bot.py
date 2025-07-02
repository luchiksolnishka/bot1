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
    {"type": "open", "question": "Что бы ты хотел сделать в ближайшее время вместе со мной?"},
    {"type": "open", "question": "Что радует тебя в последнее время (кроме меня 😘)?"},
    {"type": "open", "question": "Во сколько ты будешь сегодня дома? Напиши и отправь это Вале!"}
]

user_progress = {}

# Получаем путь до текущего файла
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
        await update.message.reply_text("🎉 Ты прошёл весь квест! Люблю тебя бесконечно ❤️")
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
        if text.lower().strip() == q["answer"].lower().strip():
            await update.message.reply_text("Верно! 😘")
        else:
            await update.message.reply_text(f"Правильный ответ был: {q['answer']} 😉")
    elif q["type"] == "open":
        await update.message.reply_text("Запомню это ❤️")

    ticket_number = step + 1
    ticket_path = os.path.join(BASE_DIR, "tickets", f"ticket_{ticket_number}.jpg")

    print(f"[DEBUG] Путь к билету: {ticket_path}, Существует: {os.path.exists(ticket_path)}")

    if os.path.exists(ticket_path):
        try:
            await update.message.reply_photo(
                InputFile(ticket_path),
                caption=f"🎟 Билет №{ticket_number}\nДействует бессрочно — по взаимной договоренности 💌"
            )
        except Exception as e:
            print(f"[ERROR] Ошибка при отправке фото: {e}")
    else:
        await update.message.reply_text(f"(❗) Билет №{ticket_number} не найден. Проверь папку 'tickets'")

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
            QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()
