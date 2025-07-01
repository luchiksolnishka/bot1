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
    user_states[user_id] = -1
    await update.message.reply_text("С Днем Рождения, любимый! 🎉 Я приготовила тебе романтический квест. Готов? Напиши 'Да' ✨")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text or ""
    photo = update.message.photo[-1].file_id if update.message.photo else None

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
    response = ""

    # Ответы
    if q["type"] == "quiz":
        if text.strip().lower() == q["answer"].lower():
            response = "Правильно! 🧠 Ты помнишь самые важные моменты 💞"
        else:
            response = f"Хихи, неправильно 😅 На самом деле — {q['answer']}!"
    elif q["type"] == "choice":
        answer_key = text.strip().lower()
        response = q.get("responses", {}).get(answer_key, "Ты выбрал интересный вариант 🥰")
    elif q["type"] == "photo":
        if photo:
            response = "Ооо, ты такой(ая) милый(ая)! 😍"
        else:
            await update.message.reply_text("Жду фото! 📷")
            return
    elif q["type"] == "final":
        response = "Записала! Спасибо, жди волшебства... 🎁"
    else:  # open
        response = "Пусть будет зафиксировано здесь 💌 В скором времени надо это осуществить 😄"

    # Отправка ответа
    await update.message.reply_text(response, reply_markup=ReplyKeyboardRemove())

    # 🎟 Выдача билета
    ticket_path = f"tickets/ticket{step+1}.jpg"
    if os.path.exists(ticket_path):
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=InputFile(ticket_path),
            caption=f"🎟 Билет №{step+1} выдан!"
        )

    # Переход к следующему вопросу
    user_states[user_id] += 1
    if user_states[user_id] < len(QUESTIONS):
        await ask_question(update, context)
    else:
        await update.message.reply_text("Это был последний вопрос! 🎉")

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
        await context.bot.send_message(chat_id=user_id, text=q["question"], reply_markup=ReplyKeyboardRemove())

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("До встречи ❤️", reply_markup=ReplyKeyboardRemove())

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))
    app.run_polling()
