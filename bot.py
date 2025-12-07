import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
import config
import discord_bot

# Хранение времени последней активности
last_activity = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Напишите свое сообщение ниже, отвечу как можно скорее.\n"
        "Чтобы я мог вам ответить — добавьте меня в контакты: @rvande1"
    )
    last_activity[update.effective_user.id] = asyncio.get_event_loop().time()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    last_activity[user.id] = asyncio.get_event_loop().time()

    # Отправка в Discord
    await discord_bot.send_to_discord(user.username or str(user.id), text)

    await update.message.reply_text("Сообщение отправлено.")


async def inactivity_checker():
    while True:
        now = asyncio.get_event_loop().time()
        to_remove = []

        for user_id, last_time in last_activity.items():
            if now - last_time > 300:  # 5 минут
                to_remove.append(user_id)

        for uid in to_remove:
            last_activity.pop(uid, None)

        await asyncio.sleep(10)


async def main():
    # Запуск Telegram
    app = ApplicationBuilder().token(config.TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота Discord параллельно
    asyncio.create_task(discord_bot.start_discord())
    asyncio.create_task(inactivity_checker())

    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
