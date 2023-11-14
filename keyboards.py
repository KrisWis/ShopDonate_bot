from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
start_keyboard.add(*['Мой профиль 👤', 'Задонатить 🛒'])
withdrawal_keyboard = InlineKeyboardMarkup()
withdrawal_keyboard.add(InlineKeyboardButton(
    text="Вывести зондкоины",
    callback_data="Вывести зондкоины"
))
choose_game = ReplyKeyboardMarkup(resize_keyboard=True)
choose_game.add(*['Brawl stars ⭐️', 'Brawl stars (мод) 🌟', 'Clash of clans 🔨', 'Clash Royale 👑', 'Roblox 👤', 'Hay day 🐓'])
brawlStars_choose_item = ReplyKeyboardMarkup(resize_keyboard=True)
brawlStars_choose_item.add(*['💎 30 гемов - 105₽', '💎 80 гемов - 245₽', '💎 170 гемов - 455₽', '💎 360 гемов - 855₽', '💎 950 гемов - 2255₽', '💎 2000 гемов - 4225₽'])
brawl_stars_mod_alert = ReplyKeyboardMarkup(resize_keyboard=True)
brawl_stars_mod_alert.add("Я принимаю условия ✅")
brawlStars_mod_choose_item = ReplyKeyboardMarkup(resize_keyboard=True)
brawlStars_mod_choose_item.add(*['💎 100 гемов - 90₽', '💎 170 гемов - 160₽', '💎 205 гемов - 255₽', '💎 400 гемов - 299₽', '💎 500 гемов - 499₽', 
'💎 610 гемов - 649₽', '💎 730 гемов - 749₽', '💎 890 гемов - 949₽'])
clashRoyale_choose_item = ReplyKeyboardMarkup(resize_keyboard=True)
clashRoyale_choose_item.add(*['💎 80 кристаллов - 90₽', '💎 500 кристаллов - 249₽', '💎 1200 кристаллов - 449₽', '💎 2500 кристаллов - 899₽', 
'💎 6500 кристаллов - 2199₽', '💎 14000 кристаллов - 3999₽', "💫 Пасс рояль - 279₽"])
clashOfClans_choose_item = ReplyKeyboardMarkup(resize_keyboard=True)
clashOfClans_choose_item.add(*['💎 500 кристаллов - 199₽', '💎 1200 кристаллов - 379₽', '💎 2500 кристаллов - 749₽', '💎 6500 кристаллов - 1699₽', 
'💎 14000 кристаллов - 3399₽', "💫 Золотой пропуск - 279₽"])
roblox_choose_item = ReplyKeyboardMarkup(resize_keyboard=True)
roblox_choose_item.add(*['💶 40 робуксов - 40₽', '💶 80 робуксов - 80₽', '💶 200 робуксов - 200₽', '💶 400 робуксов - 400₽', '💶 800 робуксов - 750₽'])
skip_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
skip_keyboard.add("Пропустить ⏩")
choose_payment = ReplyKeyboardMarkup(resize_keyboard=True)
choose_payment.add(*["Реальные деньги 💵", "Зондикоины 🧿"])
