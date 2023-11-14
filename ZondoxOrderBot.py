from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import logging.handlers
import logging
import os
import aiogram
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
import dotenv
import sqlite3 


conn = sqlite3.connect('Zondox_Order_bot_users.db')
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS users(
user_id INT,
isChatting INT,
ChattingWithID INT);""")

dotenv.load_dotenv()  # Загружаем файл .env

# Логирование.
logger = logging.getLogger(__name__)

# Записываем в переменную результат логирования
os.makedirs("Logs", exist_ok=True)


# Cоздаёт все промежуточные каталоги, если они не существуют.
logging.basicConfig(  # Чтобы бот работал успешно, создаём конфиг с базовыми данными для бота
    level=logging.INFO,
    format="[%(levelname)-8s %(asctime)s at           %(funcName)s]: %(message)s",
    datefmt="%d.%d.%Y %H:%M:%S",
    handlers=[logging.handlers.RotatingFileHandler("Logs/     TGBot.log", maxBytes=10485760, backupCount=0),
    logging.StreamHandler()])


# Создаём Telegram бота и диспетчер:
Bot = aiogram.Bot(os.environ["ORDER_BOT_TOKEN"])
DP = aiogram.Dispatcher(Bot, storage=MemoryStorage())
admins = [5617065768, 1979922062, 933122837]
user_messageIDs = {}


@DP.message_handler(commands=["start"])      # КОГДА ПОЛЬЗОВАТЕЛЬ ПИШЕТ /start
async def start(msg: Message):

    if msg.from_user.id != admins[0]:
        await msg.answer("Привет 👋. Я Telegram Bot, для общения с @Zondoxx! \nВам придёт уведомление, когда Zondoxx будет свободен и вы начнёте диалог.")

        if cur.execute(f"SELECT user_id FROM users WHERE user_id={msg.from_user.id}").fetchone() is None:
            cur.execute(f"INSERT INTO users (user_id, isChatting, ChattingWithID) VALUES(?, ?, ?)", (msg.from_user.id, 1, None))
            conn.commit()
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton(
                text="Начать диалог ✅",
                callback_data=msg.from_user.id
            ))
            await Bot.send_message(admins[0], f'Вам пишет пользователь @{msg.from_user.username}! \nЧтобы начать разговор нажмите кнопку "Начать диалог ✅"', reply_markup=keyboard)

        else:
            if not cur.execute(f"SELECT isChatting FROM users WHERE user_id={msg.from_user.id}").fetchone()[0]:
                cur.execute("UPDATE users SET isChatting = ? WHERE user_id = ?", (1, msg.from_user.id))
                keyboard = InlineKeyboardMarkup()
                keyboard.add(InlineKeyboardButton(
                    text="Начать диалог ✅",
                    callback_data=msg.from_user.id
                ))
                await Bot.send_message(admins[0], f'Вам пишет пользователь @{msg.from_user.username}! \nЧтобы начать разговор нажмите кнопку "Начать диалог ✅"', reply_markup=keyboard)

    else:
        if cur.execute(f"SELECT user_id FROM users WHERE user_id={msg.from_user.id}").fetchone() is None:
            cur.execute(f"INSERT INTO users (user_id, isChatting, ChattingWithID) VALUES(?, ?, ?)", (msg.from_user.id, 0, None))
            conn.commit()

        await msg.answer("Привет 👋. Я твой личный Telegram Bot для общения с клиентами 👥")


@DP.message_handler(commands=["stop"])
async def stop_command(msg: Message):

    user_data = cur.execute(f"SELECT * FROM users WHERE user_id={msg.from_user.id}").fetchone()

    if user_data[1] and user_data[2]:
        second_id = user_data[2]
        await Bot.send_message(second_id, "Пользователь прервал с вами диалог.")
        await msg.answer("Чат с пользователем был завершён.")
        cur.execute("UPDATE users SET isChatting = ?, ChattingWithID = ? WHERE user_id = ?", (0, 0, msg.from_user.id))
        cur.execute("UPDATE users SET isChatting = ?, ChattingWithID = ? WHERE user_id = ?", (0, 0, second_id))
        conn.commit()
        return

    await msg.answer("Вы не были в чате с пользователем.")  # Если пользователь не был в поиске, но нажал /stop


@DP.message_handler(content_types=["text", "photo", "audio", "voice", "document", "sticker", "video", "video_note"])
async def regular_message_handler(msg: Message):

    admin_data = cur.execute(f"SELECT * FROM users WHERE user_id={admins[0]}").fetchone()

    if admin_data[1] and admin_data[2] != msg.from_user.id and msg.from_user.id != admins[0]:
        await msg.answer("Подождите пока Zondoxx вам ответит! ❗️")
        return 

    if cur.execute(f"SELECT user_id FROM users WHERE user_id={msg.from_user.id}").fetchone() is None:
        cur.execute(f"INSERT INTO users (user_id, isChatting, ChattingWithID) VALUES(?, ?, ?)", (msg.from_user.id, 0, None))
        conn.commit()

    elif cur.execute(f"SELECT isChatting FROM users WHERE user_id={msg.from_user.id}").fetchone()[0]:
        ChattingWIthID = cur.execute(f"SELECT ChattingWithID FROM users WHERE user_id={msg.from_user.id}").fetchone()[0]
        reply_message_id = None

        if msg.reply_to_message:
            reply_message_id = user_messageIDs.get(msg.reply_to_message.message_id)

        copied_message = await msg.copy_to(ChattingWIthID, reply_to_message_id=reply_message_id)  # Бот отправляет сообщение собеседнику пользователя, которое пользователь отправил

        user_messageIDs.update({  # Обновляем данные
            msg.message_id: copied_message.message_id,
            copied_message.message_id: msg.message_id
        })

        conn.commit()


@DP.callback_query_handler()
async def callback_worker(call: CallbackQuery):
    ChattingWIthID = cur.execute(f"SELECT ChattingWithID FROM users WHERE user_id={call.from_user.id}").fetchone()[0]
    if ChattingWIthID:
        cur.execute("UPDATE users SET isChatting = ?, ChattingWithID = ? WHERE user_id = ?", (0, 0, ChattingWIthID))
        await call.message.answer("Чат с пользователем был завершён.")
        await Bot.send_message(ChattingWIthID, "Пользователь прервал с вами диалог.")

    cur.execute("UPDATE users SET isChatting = ?, ChattingWithID = ? WHERE user_id = ?", (1, call.data, call.from_user.id))
    cur.execute("UPDATE users SET isChatting = ?, ChattingWithID = ? WHERE user_id = ?", (1, call.from_user.id, call.data))
    conn.commit()
    await Bot.send_message(call.data, "Zondoxx начал с вами диалог ✅")
    await call.message.edit_text("Диалог начат ✅")


if __name__ == "__main__":  # Если файл запускается как самостоятельный, а не как модуль
    logger.info("Запускаю бота...")  # В консоле будет отоброжён процесс запуска бота
    executor.start_polling(  # Бот начинает работать
        dispatcher=DP,  # Передаем в функцию диспетчер
        # (диспетчер отвечает за то, чтобы сообщения пользователя доходили до бота)
        on_startup=logger.info("Загрузился успешно!"), skip_updates=True)
    # Если бот успешно загрузился, то в консоль выведется сообщение