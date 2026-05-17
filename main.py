import sqlite3

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.utils.markdown import hide_link

from youmoney import *
from buttons import *
from config import *
from payment import *
from states import *
from adminpanel import *
from games import *

conn = sqlite3.connect('bebra.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id STRING , nickname STRING, balance INTEGER , referals INTEGER, photo_id STRING, text STRING, output INTEGER, referer STRING, referal_level INTEGER)')
conn.commit()

cursor.execute('CREATE TABLE IF NOT EXISTS info (user_id STRING, nickname STRING, bill_id STRING, amount STRING, bet INTEGER, game STRING, referal_profit STRING, ban INTEGER, method STRING, voucher STRING, promo STRING, winning INTEGER)')
conn.commit()

cursor.execute('CREATE TABLE IF NOT EXISTS promocode (promo STRING, usage_max INTEGER, usage_actual INTEGER, percent INTEGER)')
conn.commit()

cursor.execute('CREATE TABLE IF NOT EXISTS voucher (voucher STRING, usage_max INTEGER, usage_actual INTEGER, amount INTEGER)')
conn.commit()

cursor.execute('CREATE TABLE IF NOT EXISTS admins (user_id STRING, nickname STRING)')
conn.commit()

cursor.execute('CREATE TABLE IF NOT EXISTS forms (user_id STRING, amount STRING, requisites STRING, method STRING)')
conn.commit()

cursor.execute('CREATE TABLE IF NOT EXISTS payment_youmoney (user_id STRING, nickname STRING, bill_id STRING, amount STRING)')
conn.commit()

cursor.execute('CREATE TABLE IF NOT EXISTS payment_bitcoin (user_id STRING, nickname STRING, bill_id STRING, amount STRING)')
conn.commit()

cursor.execute('CREATE TABLE IF NOT EXISTS payment_qiwi (user_id STRING, nickname STRING, bill_id STRING, amount STRING)')
conn.commit()

cursor.execute('CREATE TABLE IF NOT EXISTS payment_crystalpay (user_id STRING, nickname STRING, bill_id STRING, amount STRING)')
conn.commit()

cursor.execute('CREATE TABLE IF NOT EXISTS demo (user_id STRING, demobalance INTEGER, given INTEGER, state INTEGER)')
conn.commit()

cursor.execute('CREATE TABLE IF NOT EXISTS jackpot (founder STRING, player1 STRING, player2 STRING, player3 STRING, player4 STRING, player5 STRING, amount INTEGER, players INTEGER)')
conn.commit()

storage = MemoryStorage()
bot = Bot(token=token)
dp = Dispatcher(bot, storage=storage)

@dp.message_handler(commands=['start', 'keyboard'])
async def start_handler(message):

    split = message.text.split()

    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (message.chat.id,))
    cur = cursor.fetchone()

    try:

        ban = cursor.execute('SELECT ban FROM info WHERE user_id = ?', (message.chat.id,)).fetchone()[0]

        if ban == 0:

            await bot.send_message(message.chat.id, 'Приветствуем Вас 👋', reply_markup = kb)

        else:

            await bot.send_message(message.chat.id, 'Вы были забанены 🚫', reply_markup = kb_ban)

    except:

        if len(split) == 2:

            if split[1] == str(message.chat.id):

                if cur is None:

                    await add_user(message.chat.id, message.from_user.username)

                else:

                    await bot.send_message(message.chat.id, 'Приветствуем Вас 👋', reply_markup=kb)

            else:

                if cur is None:

                    await add_user_with_referal(message.chat.id, split[1], message.from_user.username)

                else:

                    await bot.send_message(message.chat.id, 'Приветствуем Вас 👋', reply_markup=kb)

        else:

            if cur is None:

                await add_user(message.chat.id, message.from_user.username)

            else:

                await bot.send_message(message.chat.id, 'Приветствуем Вас 👋', reply_markup=kb)

# Обработчик текста
@dp.message_handler(content_types=['text'])
async def text_handler(message, state: FSMContext):

    chat_id = message.chat.id
    message_id = message.message_id

    msg = message.text

    ban = cursor.execute('SELECT ban FROM info WHERE user_id = ?', (chat_id,)).fetchone()[0]

    data_good = []
    data_bad = []

    for i in cursor.execute('SELECT promo FROM promocode WHERE usage_actual < usage_max ').fetchall():
        data_good.append(i)

    b = ''.join(''.join(str(elems)) for elems in data_good).replace(',', ' ').replace('(', '').replace(')', '').replace("'", '')

    for i in cursor.execute('SELECT voucher FROM voucher WHERE usage_actual < usage_max ').fetchall():
        data_bad.append(i)

    a = ''.join(''.join(str(elems)) for elems in data_bad).replace(',', ' ').replace('(', '').replace(')', '').replace("'", '')

    a = a.split()
    b = b.split()

    if ban != 1:

        if msg in b:

            await use_promo(chat_id, msg)

        elif msg in a:

            await use_voucher(chat_id, msg)

        else:

            if msg == 'Игры 🎮':
                url = 'https://telegra.ph/file/275afc68305449732ffe7.jpg'
                text = 'Выберите игру 🎮'

                st = cursor.execute('SELECT state FROM demo WHERE user_id = ?', (chat_id,)).fetchone()[0]

                if st == 1:
                    await message.answer(f'Вы играете на демобаланс 🕹{hide_link(url)}', parse_mode='HTML', reply_markup = games)
                else:
                    await message.answer(f'{hide_link(url)}', parse_mode='HTML', reply_markup=games)

            elif msg == 'Профиль 👨‍💻':

                referals = cursor.execute('SELECT referals FROM users WHERE user_id = ?', (chat_id,)).fetchone()[0]
                referal_level = cursor.execute('SELECT referal_level FROM users WHERE user_id = ?', (chat_id,)).fetchone()[0]
                balance = cursor.execute('SELECT balance FROM users WHERE user_id = ?', (chat_id,)).fetchone()[0]
                referal_profit = cursor.execute('SELECT referal_profit FROM info WHERE user_id = ?', (chat_id,)).fetchone()[0]

                ref_link = 'https://telegram.me/{}?start={}'
                me = await bot.get_me()
                username = me.username
                ref = ref_link.format(username, message.from_user.id)
                url = 'https://telegra.ph/file/0cec7cc8de99e7f9ee639.jpg'

                admins = cursor.execute('SELECT user_id FROM admins').fetchall()
                users = []

                for i in admins:
                    users.append(i[0])

                # Формируем текст профиля безопасно и без разрывов f-строк
                profile_text = (
                    f"🤖 Ваш ID: <b>{message.from_user.id}</b> \n \n"
                    f"💰 Ваш баланс: <b>{balance} 🪙</b>\n \n"
                    f"👥 Приглашено пользователей: <b>{referals}</b> \n \n"
                    f"🍬 Доход с рефералов: <b>{referal_profit}</b> | Уровень: <b>{referal_level}</b> \n \n"
                    f"🔗 Реферальная ссылка: \n \n <code>{ref}</code> - <b>кликни</b> {hide_link(url)}"
                )

                if message.chat.id in users:
                    await bot.send_message(message.chat.id, profile_text, reply_markup=admin_profile, parse_mode="HTML")

                elif message.chat.id in admin:
                    await bot.send_message(message.chat.id, profile_text, reply_markup=creator_profile, parse_mode="HTML")
                else:
                    await bot.send_message(chat_id, profile_text, reply_markup=user_profile, parse_mode="HTML")

            elif msg == 'Поддержка 🛎':

                url = 'https://telegra.ph/file/5579c411944bc187d554e.jpg'

                bt = InlineKeyboardButton('Написать в поддержку 🖊', url =f'tg://resolve?domain={support_name}')

                keyboard = InlineKeyboardMarkup(row_width=1).add(bt)
                await message.answer(f'{hide_link(url)}', reply_markup = keyboard, parse_mode='HTML')

            elif msg == 'FAQ 📖':

                url = 'https://telegra.ph/file/40d978777a2f90b868997.jpg'

                link = InlineKeyboardButton('Читать 📜', callback_data='rules', url = 'https://telegra.ph/Informaciya-05-21-6')
                link_kb = InlineKeyboardMarkup(row_width=2).add(link)

                await message.answer(f'{hide_link(url)}', reply_markup = link_kb, parse_mode='HTML')

            else:
                await bot.send_message(message.chat.id, "Я не знаю эту команду 🥺")

    else:
        await bot.send_message(chat_id, "Вы были забанены 🚫", reply_markup=kb_ban)

@dp.message_handler(state = TestStates.activate_voucher)
async def activate_voucher(message: types.Message, state: FSMContext):

    data = await state.get_data()
    data['promo'] = message.text

    data_bad = []

    for i in cursor.execute('SELECT voucher FROM voucher WHERE usage_actual < usage_max ').fetchall():
        data_bad.append(i)

    a = ''.join(''.join(str(elems)) for elems in data_bad).replace(',', ' ').replace('(', '').replace(')', '').replace("'", '')

    a = a.split()

    while True:

        if data['promo'] in a:

            await use_voucher(message.chat.id, message.text)
            await state.finish()
            break

        else:

            await bot.send_message(message.chat.id, 'Ваучер не обнаружен 🔎', reply_markup = cancel_voucher_kb1)
            break

@dp.message_handler(state = TestStates.activate_promo)
async def activate_voucher(message: types.Message, state: FSMContext):

    data = await state.get_data()
    data['promo'] = message.text

    data_bad = []

    for i in cursor.execute('SELECT promo FROM promocode WHERE usage_actual < usage_max ').fetchall():
        data_bad.append(i)

    a = ''.join(''.join(str(elems)) for elems in data_bad).replace(',', ' ').replace('(', '').replace(')', '').replace("'", '')

    a = a.split()

    while True:

        if data['promo'] in a:

            await use_promo(message.chat.id, message.text)
            await state.finish()
            break

        else:

            await bot.send_message(message.chat.id, 'Промокод не обнаружен 🔎', reply_markup = cancel_voucher_kb1)
            break

@dp.message_handler(state=TestStates.promo)
async def get_amount(message: types.Message, state: FSMContext):

    data = await state.get_data()
    data['promo'] = message.text

    data = data['promo'].split()

    while True:

        try:

            conn = sqlite3.connect('bebra.db', check_same_thread=False)
            cursor = conn.cursor()

            user_list = [data[0], data[1], 0, data[2]]

            cursor.execute("INSERT INTO promocode VALUES (?, ?, ?, ?) ;", user_list)
            conn.commit()

            cursor.close()

            await state.finish()
            await bot.send_message(message.chat.id, f'Промокод *{data[0]}* создан ✅', reply_markup= back_promocode_kb, parse_mode = 'Markdown')
            break

        except Exception as e:

            print(e)
            print(1)
            await bot.send_message(message.chat.id, 'Сообщение должно быть в формате ⚠ \n\n *BEBRA777 50 1000*', reply_markup = cancel_promo_kb, parse_mode = 'Markdown')
            break

@dp.message_handler(state=TestStates.delete_promo)
async def get_amount(message: types.Message, state: FSMContext):

    data = await state.get_data()
    data['promo'] = message.text

    data = data['promo']

    while True:

        try:

            await delete_promo(message.chat.id, data)
            await state.finish()
            break

        except Exception as e:

            print(e)
            print(2)
            await bot.send_message(message.chat.id, 'Сообщение должно быть в формате ⚠ \n\n *BEBRA777*', reply_markup = cancel_promo_kb, parse_mode = 'Markdown')
            break

@dp.message_handler(state=TestStates.voucher)
async def get_amount(message: types.Message, state: FSMContext):

    data = await state.get_data()
    data['promo'] = message.text

    data = data['promo'].split()

    while True:

        try:

            conn = sqlite3.connect('bebra.db', check_same_thread=False)
            cursor = conn.cursor()

            user_list = [data[0], data[1], 0, data[2]]

            cursor.execute("INSERT INTO voucher VALUES (?, ?, ?, ?) ;", user_list)
            conn.commit()

            cursor.close()

            await state.finish()
            await bot.send_message(message.chat.id, f'Ваучер *{data[0]}* создан ✅', reply_markup = back_voucher_kb, parse_mode = 'Markdown')
            break

        except:

            await bot.send_message(message.chat.id, 'Сообщение должно быть в формате ⚠ \n\n *BEBRA777 50 1000*', reply_markup = cancel_promo_kb, parse_mode = 'Markdown')
            break

@dp.message_handler(state=TestStates.delete_voucher)
async def get_amount(message: types.Message, state: FSMContext):

    data = await state.get_data()
    data['promo'] = message.text

    data = data['promo']

    while True:

        try:

            await delete_voucher(message.chat.id, data)
            await state.finish()
            break

        except:

            await bot.send_message(message.chat.id, 'Сообщение должно быть в формате ⚠ \n\n *BEBRA777*', parse_mode = 'Markdown')
            break

@dp.message_handler(state=TestStates.qiwi)
async def get_amount(message: types.Message, state: FSMContext):

    data = await state.get_data()
    data['amount'] = message.text

    while True:

        try:

            int(data['amount'])

            try:

                if int(data['amount']) != 0:

                    if int(data['amount']) >= 50:

                        await state.finish()
                        await create_payment_qiwi(data['amount'], message.chat.id)
                        break

                    else:

                        await bot.send_message(message.chat.id, 'Минимальная сумма пополнения = 50 ⚠', reply_markup = cancel_payment)
                        break
                else:

                    await bot.send_message(message.chat.id, 'Сумма платежа должна быть больше 0 ⚠', reply_markup = cancel_payment)
                    break

            except Exception as e:

                print(e)
                break

        except ValueError:

            await bot.send_message(message.chat.id, 'Отправьте сумму без лишних символов ⚠', reply_markup = cancel_payment)
            break

@dp.message_handler(state=TestStates.youmoney)
async def get_amount(message: types.Message, state: FSMContext):

    data = await state.get_data()
    data['amount'] = message.text

    while True:

        try:

            int(data['amount'])

            try:

                if int(data['amount']) != 0:

                    if int(data['amount']) >= 50:

                        await state.finish()
                        await create_payment_youmoney(data['amount'], message.chat.id)
                        break

                    else:

                        await bot.send_message(message.chat.id, 'Минимальная сумма пополнения = 50 ⚠', reply_markup = cancel_payment)
                        break

                else:

                    await bot.send_message(message.chat.id, 'Сумма платежа должна быть больше 0 ⚠', reply_markup = cancel_payment)
                    break

            except Exception as exc:

                print(exc)
                break

        except ValueError:

            await bot.send_message(message.chat.id, 'Отправьте сумму без лишних символов ⚠', reply_markup = cancel_payment)
            break

@dp.message_handler(state=TestStates.card)
async def get_amount(message: types.Message, state: FSMContext):

    data = await state.get_data()
    data['amount'] = message.text

    while True:

        try:

            int(data['amount'])

            try:

                if int(data['amount']) >= 50:

                    await state.finish()
                    await create_payment_qiwi(data['amount'], message.chat.id)
                    break

                else:

                    await bot.send_message(message.chat.id, 'Минимальная сумма пополнения = 50 ⚠', reply_markup=cancel_payment)
                    break

            except Exception as exc:

                print(exc)
                break

        except ValueError:

            await bot.send_message(message.chat.id, 'Отправьте сумму без лишних символов ⚠', reply_markup = cancel_payment)
            break

@dp.message_handler(state=TestStates.bitcoin)
async def get_amount(message: types.Message, state: FSMContext):

    data = await state.get_data()
    data['amount'] = message.text

    while True:

        try:

            int(data['amount'])

            try:

                if int(data['amount']) != 0:

                    if int(data['amount']) >= 50:

                        await state.finish()
                        await create_bill_btc(message.chat.id, message.chat.id, data['amount'], data['amount'])
                        break

                    else:

                        await bot.send_message(message.chat.id, 'Минимальная сумма пополнения = 50 ⚠', reply_markup = cancel_payment)
                        break

                else:

                    await bot.send_message(message.chat.id, 'Сумма платежа должна быть больше 0 ⚠', reply_markup = cancel_payment)
                    break

            except Exception as e:
                print(e)
                break

        except ValueError:

            await bot.send_message(message.chat.id, 'Отправьте сумму без лишних символов ⚠')
            break

@dp.message_handler(state=TestStates.crystalpay)
async def get_amount(message: types.Message, state: FSMContext):

    data = await state.get_data()
    data['amount'] = message.text

    while True:

        try:

            int(data['amount'])

            try:

                if int(data['amount']) != 0:

                    if int(data['amount']) >= 50:

                        await state.finish()
                        await create_payment_crystalpay(data['amount'], message.chat.id)
                        break

                    else:

                        await bot.send_message(message.chat.id, 'Минимальная сумма пополнения = 50 ⚠', reply_markup = cancel_payment)
                        break
                else:

                    await bot.send_message(message.chat.id, 'Сумма платежа должна быть больше 0 ⚠', reply_markup = cancel_payment)
                    break

            except Exception as e:

                print(e)
                break

        except ValueError:

            await bot.send_message(message.chat.id, 'Отправьте сумму без лишних символов ⚠', reply_markup = cancel_payment)
            break

@dp.message_handler(state=TestStates.mail)
async def mailing(message: types.Message, state: FSMContext):

    data = await state.get_data()
    data['mail'] = message.text

    cursor.execute('UPDATE users SET text = ? WHERE user_id = ?', (data['mail'], message.chat.id,))
    conn.commit()

    await bot.send_message(message.chat.id, 'Отправьте фото для рассылки 🖼')
    await TestStates.photo.set()

@dp.message_handler(content_types=['photo'], state=TestStates.photo)
async def photo_for_mailing(message: types.Message, state: FSMContext):
    await state.finish()

    data = await state.get_data()
    data['photo'] = message.photo[-1].file_id

    cursor.execute('UPDATE users SET photo_id = ? WHERE user_id = ?', (data['photo'], message.chat.id,))
    conn.commit()

    photo = cursor.execute('SELECT photo_id FROM users WHERE user_id = ?', (message.chat.id,)).fetchone()[0]
    text = cursor.execute('SELECT text FROM users WHERE user_id = ?', (message.chat.id,)).fetchone()[0]

    await bot.send_message(message.chat.id, 'Подтвердите сообщение для рассылки ⬇')
    await bot.send_photo(chat_id = message.chat.id, photo=photo, caption=text, parse_mode='Markdown', reply_markup=confirm)

@dp.message_handler(state=TestStates.user_ban)
async def ban_user(message: types.Message, state: FSMContext):

    data = await state.get_data()
    data['ban_user'] = message.text

    while True:

        if '@' in data['ban_user']:

            users = []

            for i in cursor.execute('SELECT nickname FROM info').fetchall():
                users.append('@' + i[0])

            if data['ban_user'] in users:

                await state.finish()
                await ban_user_action(message.chat.id, bot, data['ban_user'].replace('@', ''))
                break

            else:

                await bot.send_message(message.chat.id, 'Пользователь не найден ⚠' ,reply_markup = cancel_user_kb)
                break

        elif data['ban_user'].isnumeric() == True:

            users = []

            for i in cursor.execute('SELECT user_id FROM info').fetchall():
                users.append(i[0])

            if int(data['ban_user']) in users:

                await state.finish()
                await ban_user_action(message.chat.id, bot, data['ban_user'])
                break

            else:

                await bot.send_message(message.chat.id, 'Пользователь не найден ⚠' ,reply_markup = cancel_user_kb)

            break

        else:
            print(type(data['ban_user']))
            await bot.send_message(message.chat.id, 'Введите @никнейм или ID пользователя ⚠', reply_markup=cancel_user_kb)
            break

@dp.message_handler(state=TestStates.user_unban)
async def mailing(message: types.Message, state: FSMContext):

    data = await state.get_data()
    data['ban_user'] = message.text

    while True:

        if '@' in data['ban_user']:

            users = []

            for i in cursor.execute('SELECT nickname FROM info').fetchall():
                users.append('@' + i[0])

            if data['ban_user'] in users:

                await state.finish()
                await ban_user_action(message.chat.id, bot, data['ban_user'].replace('@', ''))
                break

            else:

                await bot.send_message(message.chat.id, 'Пользователь не найден ⚠' ,reply_markup = cancel_user_kb)
                break

        elif data['ban_user'].isnumeric() == True:

            users = []

            for i in cursor.execute('SELECT user_id FROM info').fetchall():
                users.append(i[0])

            if int(data['ban_user']) in users:

                await state.finish()
                await unban_user_action(message.chat.id, bot, data['ban_user'])
                break

            else:

                await bot.send_message(message.chat.id, 'Пользователь не найден ⚠' ,reply_markup = cancel_user_kb)

            break

        else:
            print(type(data['ban_user']))
            await bot.send_message(message.chat.id, 'Введите @никнейм или ID пользователя ⚠', reply_markup=cancel_user_kb)
            break


@dp.message_handler(state=TestStates.user_increase_balance)
async def increase(message: types.Message, state: FSMContext):

    data = await state.get_data()
    data['user'] = message.text

    while True:

        if len(data['user'].split(' ')) == 2:

            ides = []
            nicknames = []

            for i in cursor.execute('SELECT user_id FROM users').fetchall():
                ides.append(str(i[0]))

            for i in cursor.execute('SELECT nickname FROM users').fetchall():
                nicknames.append(i[0])

            if data['user'].split(' ')[0].replace('@', '') in nicknames:

                await state.finish()
                await user_increase_balance(message.chat.id, ((data['user'].split(' ')[0])).replace('@', ''), data['user'].split(' ')[1])
                break

            elif data['user'].split(' ')[0] in ides:

                await state.finish()
                await user_increase_balance(message.chat.id, data['user'].split(' ')[0], data['user'].split(' ')[1])
                break

            else:

                await bot.send_message(message.chat.id, 'Пользователь не найден ⚠', reply_markup=cancel_user_kb)
                break

        else:

            await bot.send_message(message.chat.id, 'Неправильный формат ⚠', reply_markup=cancel_user_kb)
            break

@dp.message_handler(state=TestStates.user_decrease_balance)
async def decrease(message: types.Message, state: FSMContext):

    data = await state.get_data()
    data['user'] = message.text

    while True:

        if len(data['user'].split(' ')) == 2:

            ides = []
            nicknames = []

            for i in cursor.execute('SELECT user_id FROM users').fetchall():
                ides.append(str(i[0]))

            for i in cursor.execute('SELECT nickname FROM users').fetchall():
                nicknames.append(i[0])

            if data['user'].split(' ')[0].replace('@', '') in nicknames:

                await state.finish()
                await user_decrease_balance(message.chat.id, ((data['user'].split(' ')[0])).replace('@', ''), data['user'].split(' ')[1])
                break

            elif data['user'].split(' ')[0] in ides:

                await state.finish()
                await user_decrease_balance(message.chat.id, data['user'].split(' ')[0], data['user'].split(' ')[1])
                break

            else:

                await bot.send_message(message.chat.id, 'Пользователь не найден ⚠', reply_markup=cancel_user_kb)
                break

        else:

            await bot.send_message(message.chat.id, 'Неправильный формат ⚠', reply_markup=cancel_user_kb)
            break


@dp.message_handler(state=TestStates.add_admin)
async def add_admin_action(message: types.Message, state: FSMContext):

    data = await state.get_data()
    data['user'] = message.text

    while True:

        user = data['user']

        if user.isnumeric() == True:

            users = []

            for i in cursor.execute('SELECT user_id FROM info').fetchall():
                users.append(i[0])

            if int(data['user']) in users:

                user_nickname = cursor.execute('SELECT nickname FROM users WHERE user_id = ?', (data['user'],)).fetchone()[0]

                if user_nickname is None:

                    await state.finish()
                    await add_admin(message.chat.id, data['user'])
                    break

                else:

                    await state.finish()
                    await add_admin(message.chat.id, user_nickname)
                    break

            else:

                await bot.send_message(message.chat.id, 'Пользователь не найден ⚠', reply_markup=cancel_admin_kb)
                break

        else:

            if '@' in data['user']:

                try:

                    a = cursor.execute('SELECT nickname FROM users WHERE nickname = ?', (data['user'].replace('@', ''),)).fetchone()[0]

                    if a != None:

                        if data['user'].replace('@', '') == a:

                            await state.finish()
                            await add_admin(message.chat.id, data['user'].replace('@', ''))
                            break

                        else:

                            await bot.send_message(message.chat.id, 'Пользователь не найден ⚠', reply_markup=cancel_user_kb)
                            break

                    elif a == None:

                        await bot.send_message(message.chat.id, 'Пользователь не найден ⚠', reply_markup=cancel_admin_kb)
                        break

                except Exception as e:

                    await bot.send_message(message.chat.id, 'Пользователь не найден ⚠', reply_markup=cancel_admin_kb)
                    break

            else:

                print(1)
                break

@dp.message_handler(state=TestStates.delete_admin)
async def delete_admin_action(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data['user'] = message.text

    while True:

        user = data['user']

        if user.isnumeric() == True:

            users = []

            for i in cursor.execute('SELECT user_id FROM info').fetchall():
                users.append(i[0])

            if int(data['user']) in users:

                user_nickname = cursor.execute('SELECT nickname FROM users WHERE user_id = ?', (data['user'],)).fetchone()[0]

                if user_nickname is None:

                    await state.finish()
                    await delete_admin(message.chat.id, data['user'])
                    break

                else:

                    await state.finish()
                    await delete_admin(message.chat.id, user_nickname)
                    break

            else:

                await bot.send_message(message.chat.id, 'Пользователь не найден ⚠', reply_markup=cancel_admin_kb)
                break

        else:

            if '@' in data['user']:

                try:

                    a = cursor.execute('SELECT nickname FROM users WHERE nickname = ?', (data['user'].replace('@', ''),)).fetchone()[0]

                    if a != None:

                        if data['user'].replace('@', '') == a:

                            await state.finish()
                            await delete_admin(message.chat.id, data['user'].replace('@', ''))
                            break

                        else:

                            await bot.send_message(message.chat.id, 'Пользователь не найден ⚠', reply_markup=cancel_user_kb)
                            break

                    elif a == None:

                        await bot.send_message(message.chat.id, 'Пользователь не найден ⚠', reply_markup=cancel_user_kb)
                        break

                except Exception as e:

                    print(e)
                    await bot.send_message(message.chat.id, 'Пользователь не найден ⚠', reply_markup=cancel_user_kb)
                    break

            else:

                await bot.send_message(message.chat.id, 'Пользователь не найден ⚠', reply_markup=cancel_user_kb)
                break

