import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Функция для команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я Telegram-бот.")

# Функция для команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Доступные команды:\n/start - Начать\n/help - Помощь")

# Основной класс Telegram-бота
class TelegramBot:
    def __init__(self, token):
        # Создаем приложение
        self.app = Application.builder().token(token).build()

        # Добавляем обработчики команд
        self.app.add_handler(CommandHandler("start", start))
        self.app.add_handler(CommandHandler("help", help_command))

    def start_bot(self):
        # Создаем новый цикл событий для потока
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.app.run_polling())
        print("Telegram-бот запущен")

    async def stop_bot(self):
        # Останавливаем бота
        await self.app.stop()
        print("Telegram-бот остановлен")