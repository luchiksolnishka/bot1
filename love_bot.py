import os
from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, filters, ContextTypes
)

TOKEN = os.getenv("BOT_TOKEN")

QUESTIONS = [
    "Что бы ты хотел делать в первую очередь, когда мы встретимся? 😉",
    "Помнишь нашу поездку в Казань? Как назывался отель, в котором мы остановились?",
    "Какое самое безумное приключение ты бы хотел пережить со мной? 🌍",
    "Назови 3 вещи, которые тебя искренне радуют в последнее время (кроме меня, я и так знаю) 😉",
    "Сделай милое селфи прямо сейчас и пришли сюда 📸",
    "Отлично, квест пройден! Теперь финальное задание: ✨\n\nНапиши время, когда ты сегодня ТОЧНО будешь дома и адрес. Это важно для… сюрприза! 🎂"
]

user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_states[user_id] = 0
    await update.message.reply_text("С Днем Рождения, любимый! 🎉 Я приготовила тебе романтический квест. Готов? Напиши любой ответ, чтобы начать ✨")
    await send_question(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    # Если пользователь не запустил /start
    if user_id not in user_states:
        await update.message.reply_text("Напиши /start, чтобы начать 🎉")
        return

    step = user_states[user_id]

    # Выдаем билет (если есть)
    ticket_path = f"tickets/ticket{step+1}.jpg"
    if os.path.exists(ticket_path):
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=InputFile(ticket_path),
            caption=f"🎟 Билет №{step+1} выдан!"
        )

    # Переходим к следующему вопросу
    user_states[user_id] += 1
    if user_states[user_id] < len(QUESTIONS):
        await send_question(update, context)
    else:
        await update.message.reply_text("Это был последний вопрос. Квест завершён! 🎉 Спасибо за участие 💖")

async def send_question(update_or_context, context):
    user_id = str(update_or_context.effective_user.id)
    step = user_states.get(user_id, 0)
    if step < len(QUESTIONS):
        question = QUESTIONS[step]
        await context.bot.send_message(chat_id=user_id, text=question)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))
    app.run_polling()
