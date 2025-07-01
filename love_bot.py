import os
from telegram import Update, InputFile, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, filters, ContextTypes
)

TOKEN = os.getenv("BOT_TOKEN")

QUESTIONS = [
    {
        "type": "choice",
        "question": "Что бы ты хотел делать в первую очередь, когда мы встретимся? 😉",
        "options": ["Обнимашки", "Рассказывать все новости", "Очень много гулять", "Смотреть в глаза"],
        "responses": {
            "обнимашки": "Я бы тоже очень хотела тебя сейчас обнять. Утонуть в тепле и уюте🫂",
            "рассказывать все новости": "Мы можем разговаривать часами напролет, но и молчать нам комфортно🤫",
            "очень много гулять": "Гулять так, что ноги отваливаются. Такое одобряем😃",
            "смотреть в глаза": "Давно я их не видела, надо исправлять💔"
        }
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
    user_states[user_id] = 0
    await update.message.reply_text(
        "С Днем Рождения, любимый! 🎉 Я приготовила тебе романтический квест. Напиши любой ответ, чтобы начать ✨"
    )
    await ask_question(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    message = update.message
    text = message.text or ""
    photo = message.photo[-1].file_id if message.photo else None

    if user_id not in user_states:
        await update.message.reply_text("Напиши /start, чтобы начать 🎉")
        return

    step = user_states[user_id]
    if step >= len(QUESTIONS):
        await update.message.reply_text("Квест уже завершён! 🎉")
        return

    q = QUESTIONS[step]
    response = ""

    # Обработка ответа
    if q["type"] == "choice":
        answer = text.strip().lower()
        response = q["responses"].get(answer, "Ты выбрал интересный вариант 🥰")

    elif q["type"] == "quiz":
        correct = q["answer"].strip().lower()
        if text.strip().lower() == correct:
            response = "Умничка! Это правильный ответ 😍"
        else:
            response = f"Хихи, не совсем. На самом деле — {q['answer']} 😉"

    elif q["type"] == "photo":
        if photo:
            response = "Улыбка тебе очень идёт 😘"
        else:
            await message.reply_text("Жду фото! 📷")
            return

    elif q["type"] == "final":
        response = "Записала! 🎂 Ожидай сюрприза ❤️"

    else:  # open
        response = "Пусть будет зафиксировано. Хочу это с тобой осуществить 😌"

    # Отвечаем
    await update.message.reply_text(response, reply_markup=ReplyKeyboardRemove())

    # Выдаем билет, если есть
    ticket_path = f"tickets/ticket{step+1}.jpg"
    if os.path.exists(ticket_path):
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=InputFile(ticket_path),
            caption=f"🎟 Билет №{step+1} выдан!"
        )

    # Переход к следующему шагу
    user_states[user_id] += 1
    if user_states[user_id] < len(QUESTIONS):
        await ask_question(update, context)
    else:
        await update.message.reply_text("Ты прошёл весь квест! Спасибо за эмоции 💖")

async def ask_question(update_or_context, context):
    user_id = str(update_or_context.effective_user.id)
    step = user_states.get(user_id, 0)
    if step >= len(QUESTIONS):
        return
    q = QUESTIONS[step]

    if q["type"] in ["choice", "quiz"]:
        keyboard = [[KeyboardButton(opt)] for opt in q["options"]]
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await context.bot.send_message(chat_id=user_id, text=q["question"], reply_markup=markup)
    else:
        await context.bot.send_message(chat_id=user_id, text=q["question"], reply_markup=ReplyKeyboardRemove())

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))
    app.run_polling()
