import os
import json
from datetime import datetime
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
        "question": "Какое самое безумное приключение ты бы хотел пережить со мной? 🌍",
        "responses": {
            "Пусть будет зафиксировано здесь, в скором времени нам стоит это осуществить, хихих"
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

    # Обработка "Продолжить"
    if text.lower() == "продолжить" and user_id in waiting_for_continue:
        waiting_for_continue.remove(user_id)
        user_states[user_id] += 1  # Теперь можно увеличивать шаг
        await ask_question(update, context)  # Показываем следующий вопрос
        return

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

    # Логика ответа на текущий вопрос
    if q["type"] == "quiz":
        if text.strip().lower() == q["answer"].lower():
            response = RESPONSES[step]["правильно"]
        else:
            response = RESPONSES[step]["неправильно"].format(answer=q["answer"])
    elif q["type"] == "choice":
        response = RESPONSES[step].get(text.strip().lower(), "Ты выбрал интересный вариант 🥰")
    elif q["type"] == "photo":
        if photo:
            response = RESPONSES[step]
        else:
            await update.message.reply_text("Жду фото! 📷")
            return
    elif q["type"] == "final":
        response = RESPONSES[step]
        await update.message.reply_text(response, reply_markup=ReplyKeyboardRemove())
        user_states[user_id] += 1
        return
    else:
        response = RESPONSES[step]

    await update.message.reply_text(response, reply_markup=ReplyKeyboardRemove())

    # 🎟 Выдача билета (именно после ответа, по текущему шагу)
    ticket_path = f"tickets/ticket{step+1}.jpg"
    if os.path.exists(ticket_path):
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=InputFile(ticket_path),
            caption=f"🎟 Билет №{step+1} выдан!"
        )

    # ⏭ Предложить перейти к следующему вопросу
    if step + 1 < len(QUESTIONS):
        keyboard = [[KeyboardButton("Продолжить")]]
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Нажми 'Продолжить', чтобы перейти к следующему вопросу 💌", reply_markup=markup)
        waiting_for_continue.add(user_id)
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
    await update.message.reply_text("До встречи❤️")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))
    app.run_polling()
