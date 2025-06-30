import os
import json
from datetime import datetime
from telegram import Update, InputFile, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, filters, ContextTypes
)

TOKEN = os.getenv("BOT_TOKEN")
QUESTIONS = [
    {
        "type": "choice",
        "question": "Что бы ты хотел делать в первую очередь, когда мы встретимся? 😉",
        "options": ["Обнимашки", "Рассказывать все новости", "Очень много гулять", "Смотреть в глаза"]
    },
    {
        "type": "quiz",
        "question": "Помнишь нашу поездку в Казань? Как назывался отель, в котором мы остановились?",
        "options": ["Татарская слобода", "Мираж", "Корона", "Кристалл"],
        "answer": "Корона"
    },
    {
        "type": "open",
        "question": "Какое самое безумное приключение ты бы хотел пережить со мной? 🌍"
    },
    {
        "type": "open",
        "question": "Назови 3 вещи, которые тебя искренне радуют в последнее время (кроме меня, я и так знаю) 😉"
    },
    {
        "type": "photo",
        "question": "Сделай милое селфи прямо сейчас и пришли сюда 📸"
    },
    {
        "type": "final",
        "question": "Отлично, квест пройден! Теперь финальное задание: ✨\n\nНапиши время, когда ты сегодня ТОЧНО будешь дома и адрес. Это важно для… сюрприза! 🎂"
    }
]

user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_states[user_id] = -1
    await update.message.reply_text("С Днем Рождения, любимый! 🎉 Я приготовил(а) тебе романтический квест. Готов? Напиши 'Да' ✨")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text or ""
    photo_id = update.message.photo[-1].file_id if update.message.photo else None

    if user_id not in user_states:
        await update.message.reply_text("Напиши /start, чтобы начать 🎉")
        return

    step = user_states[user_id]

    if step == -1:
        if text.lower() in ["да", "конечно"]:
            user_states[user_id] = 0
            await ask_question(update, context)
        else:
            await update.message.reply_text("Напиши 'Да', чтобы начать 💖")
        return

    if step >= len(QUESTIONS):
        await update.message.reply_text("Квест уже завершён! 🎉")
        return

    q = QUESTIONS[step]

    if q["type"] == "quiz":
        if text.strip().lower() == q["answer"].lower():
            await update.message.reply_text("Правильно! 😘")
        else:
            await update.message.reply_text(f"Хм, правильный ответ был: {q['answer']} 😉")
    elif q["type"] == "photo":
        await update.message.reply_text("Улыбка дня принята! 📸")
    elif q["type"] == "final":
        await update.message.reply_text("Все твои ответы и фото — это самое ценное 💌 Мы обязательно сделаем то, что ты хочешь, а теперь просто ожидай сюрприз… 🎁")
        user_states[user_id] = len(QUESTIONS)
        return
    else:
        await update.message.reply_text("Ответ принят! 📝")

    ticket_path = f"tickets/ticket{step + 1}.jpg"
    if os.path.exists(ticket_path):
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=InputFile(ticket_path), caption=f"🎟 Билет №{step+1} выдан!")

    user_states[user_id] += 1
    if user_states[user_id] < len(QUESTIONS):
        await ask_question(update, context)

async def ask_question(update_or_context, context):
    user_id = str(update_or_context.effective_user.id)
    step = user_states.get(user_id, 0)
    if step >= len(QUESTIONS):
        return
    q = QUESTIONS[step]
    if q["type"] in ["choice", "quiz"]:
        keyboard = [[KeyboardButton(opt)] for opt in q["options"]]
        markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await context.bot.send_message(chat_id=user_id, text=q["question"], reply_markup=markup)
    else:
        await context.bot.send_message(chat_id=user_id, text=q["question"])

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("До встречи❤️")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    app.run_polling()
