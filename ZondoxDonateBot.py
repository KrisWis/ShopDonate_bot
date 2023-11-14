from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
import logging.handlers
import logging
import os
import aiogram
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import StatesGroup, State
import dotenv
import keyboards
import re
from datetime import datetime
import sqlite3 


conn = sqlite3.connect('Zondox_Donate_bot_users.db')
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS users(
username TEXT,
balance INT,
referrer_id INT);""")


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
Bot = aiogram.Bot(os.environ["DONATE_BOT_TOKEN"])
DP = aiogram.Dispatcher(Bot, storage=MemoryStorage())

items = {'Brawl stars ⭐️': keyboards.brawlStars_choose_item, 'Brawl stars (мод) 🌟': keyboards.brawlStars_mod_choose_item, 
'Clash Royale 👑': keyboards.clashRoyale_choose_item, 'Clash of clans 🔨': keyboards.clashOfClans_choose_item, 'Roblox 👤': keyboards.roblox_choose_item}
admins = [5617065768, 1979922062, 933122837]


class UserState(StatesGroup):  # Создаём состояния
    referral = State() 
    email = State()
    withdrawal = State()
    

@DP.message_handler(commands=["start"], state="*")      # КОГДА ПОЛЬЗОВАТЕЛЬ ПИШЕТ /start
async def start(msg: Message, state: FSMContext):
    
    if cur.execute(f"SELECT username FROM users WHERE username='{msg.from_user.username}'").fetchone() is None:
        referrer_id = msg.text[7:]
        if referrer_id and referrer_id != str(msg.from_user.id):
            cur.execute(f"INSERT INTO users ('username', 'balance', 'referrer_id') VALUES(?, ?, ?)",(msg.from_user.username, 0, referrer_id))
            conn.commit()
            await Bot.send_message(int(referrer_id), f"По вашей реферальной ссылке зарегистрировался пользователь @{msg.from_user.username} ✅")
        else:
            cur.execute(f"INSERT INTO users ('username', 'balance') VALUES(?, ?)",(msg.from_user.username, 0))
            conn.commit()

    await msg.answer("""Привет, в этом боте ты  можешь заказать донат от Zondox'a в игры от Supercell и не только по самым низким ценам! 🌟

Чтобы посмотреть свой баланс/получить реферальную ссылку, жми "Мой профиль 👤"
Чтобы сделать заказ, жми "Задонатить 🛒"

Удачных покупок! ❤️‍🔥""",
    reply_markup=keyboards.start_keyboard)
    await state.finish()
    

@DP.message_handler()
async def ReplyKeyboard_handling(msg: Message, state: FSMContext):

    if msg.text == 'Задонатить 🛒':
        await msg.answer("Выбери игру, в которую хочешь задонатить:",
        reply_markup=keyboards.choose_game)

    elif msg.text == 'Мой профиль 👤':
        user_balance = cur.execute(f"SELECT * FROM users WHERE username='{msg.from_user.username}'").fetchone()[1]
        referrers_amount = cur.execute(f"SELECT COUNT(username) as count FROM users WHERE referrer_id = {msg.from_user.id}").fetchone()[0]
        await msg.answer(f'Мой профиль 👤\n\nВаш баланс: {user_balance} зондикоинов ({user_balance}₽) \
        \nТвоя реферальная ссылка: https://t.me/{os.environ["BOT_NICKNAME"]}?start={msg.from_user.id}\nКоличество рефералов: {referrers_amount}', reply_markup=keyboards.withdrawal_keyboard)

    elif msg.text == 'Brawl stars (мод) 🌟':
        await msg.answer("❗️Перед покупкой гемов через мод обрати внимание ❗️ \n\n- Ты сможешь приобрести одно количество гемов на один аккаунт только единожды. \
        \n- При покупке все возможные риски ты берешь на себя.", reply_markup=keyboards.brawl_stars_mod_alert)

    elif msg.text in ['Brawl stars ⭐️', 'Clash of clans 🔨', 'Clash Royale 👑', 'Roblox 👤', 'Я принимаю условия ✅']:
        photo = open("{}_prices.png".format(re.sub(' +', '_', msg.text) if msg.text != 'Я принимаю условия ✅' else "Brawl_stars_(мод)_🌟"), "rb")
        await Bot.send_photo(chat_id=msg.from_user.id, photo=photo, caption="Выбери товар, который хочешь приобрести:", reply_markup=items[msg.text if msg.text != 'Я принимаю условия ✅' else 'Brawl stars (мод) 🌟'])

    elif msg.text == 'Hay day 🐓':
        await msg.answer("Пока что недоступно в боте, поэтому за покупкой пишите в лс @ZondoxOrderBot 🔅")

    elif "гемов" in msg.text or "кристаллов" in msg.text or "робуксов" in msg.text or msg.text in ["💫 Пасс рояль - 279₽", "💫 Золотой пропуск - 279₽"]:
        await state.update_data(price=int(msg.text.split()[-1][:-1]))
        await state.update_data(item=msg.text)
        await msg.answer('Хотите ли вы указать реферала? Если да, то отправьте боту его в формате @user, иначе нажмите кнопку "Пропустить ⏩".', reply_markup=keyboards.skip_keyboard)
        await UserState.referral.set()

    elif msg.text == "Пропустить ⏩":
        await msg.answer("Укажи электронную почту, на которую зарегестрирован твой аккаунт.", reply_markup=ReplyKeyboardRemove())

    elif msg.text in ["Реальные деньги 💵", "Зондикоины 🧿"]:
        data = await state.get_data()
        user_balance = cur.execute("SELECT balance FROM users WHERE username = ?", (msg.from_user.username,)).fetchone()[0]

        if user_balance >= data["price"] and msg.text == "Зондикоины 🧿" or msg.text == "Реальные деньги 💵":

            if msg.text == "Зондикоины 🧿":
                cur.execute("UPDATE users SET balance = ? WHERE username = ?", (user_balance - data["price"], msg.from_user.username))
                conn.commit()

            await msg.answer("Спасибо за заказ! Можете ознакомиться с нами на @proximabits. Напишите в бота для общения с Zondoxx - @ZondoxOrderBot", reply_markup=ReplyKeyboardRemove())
            await Bot.send_message(93312286262624642642327, f'Пользователь @{msg.from_user.username} сделал заказ \nТовар: {data["item"]} \nВремя заказа: {datetime.now().strftime("%H:%M")} \
            \nРеферал: {data["referral"]} \nПочта: {data["email"]}')
            await state.finish()

        else:
            await msg.answer("У тебя не хватает денег для покупки! ❌")

    elif msg.text.startswith("/add"):
        user = msg.text.split()[1][1:]
        if cur.execute(f"SELECT username FROM users WHERE username='{user}'").fetchone() is None:
            await msg.answer("Пользователя нету в базе данных! ❌")
        else:
            amount = int(msg.text.split()[2])
            user_balance = cur.execute("SELECT balance FROM users WHERE username = ?", (user,)).fetchone()[0]
            cur.execute("UPDATE users SET balance = ? WHERE username = ?", (user_balance + amount, user))
            conn.commit()
            await msg.answer(f"На аккаунт пользователя @{user} добавлено {amount} зондикоинов ✅")


@DP.callback_query_handler()
async def callback_worker(call: CallbackQuery):
    if call.data == "Вывести зондкоины":
        await call.message.edit_text("Какую сумму хотите вывести?")
        await UserState.withdrawal.set()


@DP.message_handler(state=UserState.withdrawal)  # Когда появляется состояние с withdrawal
async def withdrawal(msg: Message, state: FSMContext):
    withdrawal = int(msg.text)
    user_balance = cur.execute("SELECT balance FROM users WHERE username = ?", (msg.from_user.username,)).fetchone()[0]
    if user_balance >= withdrawal:
        cur.execute("UPDATE users SET balance = ? WHERE username = ?", (user_balance - withdrawal, msg.from_user.username))
        conn.commit()
        await msg.answer(f'Пользователь: @{msg.from_user.username} \nВремя заказа: {datetime.now().strftime("%H:%M")} \nСумма вывода: {withdrawal} зондикоинов. \
        \nНапишите в бота для общения с Zondoxx - @ZondoxOrderBot')
        await Bot.send_message(933122832522642646427, f'Пользователь @{msg.from_user.username} сделал вывод средств. \nВремя заказа: {datetime.now().strftime("%H:%M")}  \
        \nСумма вывода: {withdrawal} зондикоинов.')
        await state.finish()
    else:
        await msg.answer("У вас на балансе недостаточно зондикоинов для вывода средств! ❌ \nПопробуйте ещё раз.")


@DP.message_handler(state=UserState.referral)  # Когда появляется состояние с referral
async def adding_referral(msg: Message, state: FSMContext):

    if msg.text == "Пропустить ⏩":
        await state.update_data(referral="Не указан.")
        await msg.answer("Укажи электронную почту, на которую зарегестрирован твой аккаунт.", reply_markup=ReplyKeyboardRemove())
    else:
        await state.update_data(referral=msg.text)
        await msg.answer("Реферал добавлен! ✅\nТеперь укажи электронную почту, на которую зарегестрирован твой аккаунт.", reply_markup=ReplyKeyboardRemove())
    
    await UserState.email.set()


@DP.message_handler(state=UserState.email)  # Когда появляется состояние с email
async def adding_email(msg: Message, state: FSMContext):

    await state.update_data(email=msg.text)
    await msg.answer("Что вы хотите использовать для оплаты?", reply_markup=keyboards.choose_payment)
    await state.reset_state(with_data=False)


if __name__ == "__main__":  # Если файл запускается как самостоятельный, а не как модуль
    logger.info("Запускаю бота...")  # В консоле будет отоброжён процесс запуска бота
    executor.start_polling(  # Бот начинает работать
        dispatcher=DP,  # Передаем в функцию диспетчер
        # (диспетчер отвечает за то, чтобы сообщения пользователя доходили до бота)
        on_startup=logger.info("Загрузился успешно!"), skip_updates=True)
    # Если бот успешно загрузился, то в консоль выведется сообщение