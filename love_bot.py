import os
import json
from datetime import datetime
from telegram import Update, InputFile, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, filters, ContextTypes,
    ConversationHandler
)

TOKEN = os.getenv("BOT_TOKEN")
STAGE = range(1)
RESPONSES_FILE = "responses.json"

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

def load_responses():
    if os.path.exists(RESPONSES_FILE):
        with open(RESPONSES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_responses(data):
    with open(RESPONSES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

responses = load_responses()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_states[user_id] = 0
    responses[user_id] = []
    save_responses(responses)
    await update.message.reply_text("С Днем Рождения, любимый! 🎉 Я приготовил(а) тебе романтический квест. Готов? Напиши 'Да' ✨")
    return STAGE

async def continue_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    step = user_states.get(user_id, 0)

    if step == 0 and update.message.text.lower() not in ["да", "конечно"]:
        await update.message.reply_text("Напиши 'Да', чтобы начать 💖")
        return STAGE

    q = QUESTIONS[step]
    answer_text = update.message.text
    photo_id = update.message.photo[-1].file_id if update.message.photo else None

    responses.setdefault(user_id, []).append({
        "time": datetime.now().isoformat(),
        "question": q["question"],
        "answer": answer_text,
        "photo": photo_id
    })
    save_responses(responses)

    if q["type"] == "quiz":
        if answer_text and answer_text.strip().lower() == q["answer"].lower():
            await update.message.reply_text("Правильно! 😘")
        else:
            await update.message.reply_text(f"Хм, правильный ответ был: {q['answer']} 😉")
    elif q["type"] == "photo":
        await update.message.reply_text("Улыбка дня принята! 📸")
    elif q["type"] == "final":
        await update.message.reply_text("Все твои ответы и фото — это самое ценное 💌 Мы обязательно сделаем то, что ты хочешь, а теперь просто ожидай сюрприз… 🎁")
        return ConversationHandler.END
    else:
        await update.message.reply_text("Ответ принят! 📝")

    ticket_path = f"tickets/ticket{step + 1}.jpg"
    if os.path.exists(ticket_path):
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=InputFile(ticket_path), caption=f"🎟 Билет №{step+1} выдан!")

    user_states[user_id] += 1
    step += 1
    if step >= len(QUESTIONS):
        return ConversationHandler.END

    next_q = QUESTIONS[step]
    if next_q["type"] in ["choice", "quiz"]:
        keyboard = [[KeyboardButton(opt)] for opt in next_q["options"]]
        markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(next_q["question"], reply_markup=markup)
    else:
        await update.message.reply_text(next_q["question"])
    return STAGE

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("До встречи, Любовь ❤️")
    return ConversationHandler.END

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if os.path.exists(RESPONSES_FILE):
        await update.message.reply_document(document=InputFile(RESPONSES_FILE), filename="responses.json")
    else:
        await update.message.reply_text("Файл ещё не создан 😢")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            STAGE: [MessageHandler(filters.ALL, continue_game)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("download", download))
    app.run_polling()
