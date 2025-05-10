import asyncio
import os
import pyautogui
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
import configparser

TASKS_FILE_PATH = os.path.join(os.path.expanduser('~'), 'Desktop', 'tasks.txt')
ADDING_TASK, DELETING_TASK = range(2)

def load_tasks():
    try:
        with open(TASKS_FILE_PATH, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        return []

def save_tasks(tasks):
    with open(TASKS_FILE_PATH, 'w', encoding='utf-8') as file:
        for task in tasks:
            file.write(f"{task}\n")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.message.from_user.id) != context.bot_data['AK_telegram_id']:
        await update.message.reply_text("Владелец не распознан")
        return

    keyboard = [
        [KeyboardButton("Спящий режим"), KeyboardButton("Подтвердить игру")],
        [KeyboardButton("Добавить задачу"), KeyboardButton("Удалить задачу"), KeyboardButton("Весь список")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        f"Привет {update.message.from_user.first_name}\nСледующая строка, доступные действия:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.message.from_user.id) != context.bot_data['AK_telegram_id']:
        await update.message.reply_text("Владелец не распознан")
        return

    text = update.message.text
    if text == "Спящий режим":
        await update.message.reply_text("Компьютер переведен в спящий режим, бот отключен")
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

    elif text == "Подтвердить игру":
        await update.message.reply_text("Игра подтверждена!")
        screen_width, screen_height = pyautogui.size()
        pyautogui.click(x=screen_width // 2, y=(screen_height // 2) - 40)

    elif text == "Весь список":
        tasks = context.bot_data.get('tasks', [])
        if tasks:
            task_list = "\n".join(f"{i+1}. {task}" for i, task in enumerate(tasks))
            await update.message.reply_text(f"Список задач:\n{task_list}")
        else:
            await update.message.reply_text("Список задач пуст.")

    elif text == "Добавить задачу":
        await update.message.reply_text("Введите задачу:")
        return ADDING_TASK

    elif text == "Удалить задачу":
        tasks = context.bot_data.get('tasks', [])
        if tasks:
            task_list = "\n".join(f"{i+1}. {task}" for i, task in enumerate(tasks))
            await update.message.reply_text(f"Текущие задачи:\n{task_list}\n\nВведите номер задачи для удаления:")
            return DELETING_TASK
        else:
            await update.message.reply_text("Список задач пуст.")

async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task = update.message.text
    if 'tasks' not in context.bot_data:
        context.bot_data['tasks'] = []
    context.bot_data['tasks'].append(task)
    save_tasks(context.bot_data['tasks'])
    await update.message.reply_text(f"Задача '{task}' добавлена!")
    return ConversationHandler.END

async def delete_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        task_num = int(update.message.text) - 1
        tasks = context.bot_data.get('tasks', [])
        if 0 <= task_num < len(tasks):
            deleted_task = tasks.pop(task_num)
            save_tasks(tasks)
            await update.message.reply_text(f"Задача '{deleted_task}' удалена!")
        else:
            await update.message.reply_text("Неверный номер задачи!")
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите числовой номер задачи!")
    return ConversationHandler.END

class TelegramBot:
    def __init__(self, token, AK_telegram_id):
        self.app = Application.builder().token(token).build()
        self.app.bot_data['AK_telegram_id'] = AK_telegram_id
        self.app.bot_data['tasks'] = load_tasks()

        # Добавляем обработчики
        self.app.add_handler(CommandHandler("start", start))
        
        conv_handler = ConversationHandler(
            entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
            states={
                ADDING_TASK: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_task)],
                DELETING_TASK: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_task)]
            },
            fallbacks=[]
        )
        self.app.add_handler(conv_handler)

    def start_bot(self): #логично старт работы
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.app.run_polling())
        print("Telegram-бот запущен")

    async def stop_bot(self): #логично завершение работы
        await self.app.stop()
        print("Telegram-бот остановлен")



# тест бота из файла а не через main файл
if __name__ == "__main__":
    config = {}
    with open('config.py', 'r', encoding='utf-8') as file:
        exec(file.read(), config)
    bot = TelegramBot(config['AK_telegram'], config['AK_telegram_id'])
    bot.start_bot()
