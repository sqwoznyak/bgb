from aiogram import types
from aiogram import Router, F
from aiogram import flags
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from payment import run_payment, item_1m, item_1y, item_3m
from yookassa import Configuration,Payment
import asyncio
import payment
import config
import kb
import utils
from db import Database

router = Router()
db = Database('users.db')

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    print("DEBUG: received /start from", message.from_user.id)
    if not db.user_exists(message.from_user.id):
        db.add_user(message.from_user.id, message.from_user.username, referal_id=None)
        unique_key = utils.generate_key()
        db.add_key(message.from_user.id, "Key", unique_key, duration_days=10000)  
        db.set_admin_priv(message.from_user.username) 
    
    status = db.get_user_role(message.from_user.id)
    match status:
        case "start":
            keyboard = types.ReplyKeyboardMarkup(keyboard=kb.start_kb,
                resize_keyboard=True,
                input_field_placeholder=kb.TEXT_FIELD_PLACEHOLDER
            )
            await message.answer(kb.START_MESSAGE, reply_markup=keyboard)
        case "user":
            keyboard = types.ReplyKeyboardMarkup(keyboard=kb.user_kb,
                resize_keyboard=True,
                input_field_placeholder=kb.TEXT_FIELD_PLACEHOLDER
            )
            await message.answer(kb.TEXT_USER_MAIN, reply_markup=keyboard)
        case "admin":
            keyboard = types.ReplyKeyboardMarkup(keyboard=kb.admin_kb,
                resize_keyboard=True,
                input_field_placeholder=kb.TEXT_FIELD_PLACEHOLDER
            )
            await message.answer(kb.START_MESSAGE, reply_markup=keyboard)

@router.message(F.text.lower() == "главное меню")
async def handle_main_menu(message: types.Message):
    await cmd_start(message)

@router.message(F.text.lower() == "купить")
async def buySubscription(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb.buy_kb)
    await message.answer(kb.BUY_MESSAGE, reply_markup=keyboard)

@router.message(F.text.lower() == "пользовательское соглашение")
async def buySubscription(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb.user_agr_kb)
    await message.answer(kb.TEXT_USER_AGREEMENT, reply_markup=keyboard)


@router.callback_query(F.data == "one_month")
async def call_buy_one_month_subscription(call: types.CallbackQuery):
    # значит будем делать всякую хуйню тут в плане юрл и прочих приколов
    # keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb.bill_1m) 
    # Тут теперь будет функция генерации клавиатуры 
    bill= await run_payment(item_1m)
    buy_button = payment.create_pay_button(bill.confirmation.confirmation_url, bill.id)
    await call.message.edit_text(kb.TEXT_BILL_ONE_MONTH, reply_markup=buy_button)

@router.callback_query(F.data == "three_month")
async def call_buy_one_month_subscription(call: types.CallbackQuery):
#    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb.bill_3m)
#    await call.message.edit_text(kb.TEXT_BILL_THREE_MONTH, reply_markup=keyboard)
    pass

@router.callback_query(F.data == "one_year")
async def call_buy_one_month_subscription(call: types.CallbackQuery):
#    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb.bill_1y)
#    await call.message.edit_text(kb.TEXT_BILL_ONE_YEAR, reply_markup=keyboard)
    pass

@router.callback_query(lambda F: F.data and F.data.startswith('buying'))
async def process_callback(callback_query: types.CallbackQuery):
    data = callback_query.data.split(",")
    action = data[0]  # "buying_1m"
    payment_id = data[1]  # "some_value"

    # Найдем платеж
    payment = Payment.find_one(payment_id)
    
    # Сообщаем пользователю, что проверяем статус оплаты
    await callback_query.message.bot.send_message(
        chat_id=callback_query.message.chat.id, 
        text=f"Проверка статуса оплаты. Пожалуйста, подождите...."
    )

    while payment.status == 'pending':
        # Подождем перед следующей проверкой
        await asyncio.sleep(3)
        
        # Обновляем статус платежа
        payment = Payment.find_one(payment_id)

        # Сообщаем пользователю текущий статус (например, раз в несколько циклов, чтобы избежать спама)
        await callback_query.message.bot.send_message(
            chat_id=callback_query.message.chat.id, 
            text=f"Статус оплаты: {payment.status}"
        )

    # После выхода из цикла отправляем финальное сообщение в зависимости от статуса
    if payment.status == 'succeeded':
        # Добавление в БД и тп и тд
        db.add_sub(callback_query.message.chat.id, payment.id, payment.description, utils.generate_key(), "000" )
        db.set_admin_priv(callback_query.message.chat.username)
        payment_details = (
            f"✅ **Платежная информация**\n"
            f"🔹 **ID транзакции:** {payment.id}\n"
            f"🔹 **Сумма:** {payment.amount['value']} {payment.amount['currency']}\n"
            f"🔹 **Срок подписки:** {payment.description}\n"
            f"🔹 **Дата создания:** {payment.created_at}\n"
            "\nДля доступа ко всем функциям нажмите кнопку **\"Главное меню\"**."
        )

        keyboard = types.ReplyKeyboardMarkup(keyboard=kb.main_kb,
            resize_keyboard=True,
            input_field_placeholder=kb.TEXT_FIELD_PLACEHOLDER
        )

        text = kb.TEXT_SUCCESS_PAY + payment_details
        await callback_query.message.bot.send_message(
            chat_id=callback_query.message.chat.id, 
            text=text, 
            reply_markup=keyboard, 
            parse_mode='Markdown'
        )
    else:
        await callback_query.message.bot.send_message(
            chat_id=callback_query.message.chat.id, 
            text=kb.TEXT_FAIL_PAY, 
            parse_mode='Markdown'
        )

@router.message(F.text.lower() == "usermode")
async def usermode(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb.user_kb,
        resize_keyboard=True,
        input_field_placeholder=kb.TEXT_FIELD_PLACEHOLDER
    )
    await message.answer(kb.TEXT_USER_MAIN, reply_markup=keyboard)

@router.callback_query(F.data == "back")
async def call_main_menu(call: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb.buy_kb)
    await call.message.edit_text(kb.BUY_MESSAGE, reply_markup=keyboard)


@router.message(F.text.lower() == "ключ")
async def buySubscription(message: types.Message):
    TEXT_GET_KEY = db.get_user_key(message.from_user.id)
    await message.answer(TEXT_GET_KEY)

@router.message(F.text.lower() == "статус")
async def buySubscription(message: types.Message):

    date = db.get_user_end_sub(message.from_user.id)
    TEXT_SUBSCRIPTION_ACTIVE = (
        f"🌟 Ваша подписка активна!\n"
        f"Срок действия: до {date}\n"
        f"Продлите подписку, чтобы сохранить доступ к сервису."
    )

    await message.answer(TEXT_SUBSCRIPTION_ACTIVE)

@router.message(F.text.lower() == "помощь")
async def buySubscription(message: types.Message):
    await message.answer(
        kb.TEXT_VPN_FAQ, 
        parse_mode='Markdown'
    )
#lambda F: F.data and F.data.startswith('отправить всем')

#F.text.lower() == "отправить всем"

@router.message(F.text.startswith("Отправить"))
async def sendall(message: types.Message):
    if message.chat.type == 'private':
        if message.from_user.id == 353666482:
            text = message.text[9:]  # Extracting the text after the command
            users = db.get_users()  # Getting the list of users from the database
            
            for row in users:
                try:
                    await message.bot.send_message(row[0], text)
                    # db.set_active(row[0], 1)  # Убираем, такого метода нет
                except:
                    pass  # db.set_active(row[0], 0)  # Убираем, такого метода нет
            
            await message.bot.send_message(message.from_user.id, "Успешная рассылка")  # Send confirmation to admin


'''
async def send_custom_message(message: types.Message):
    # Предположим, что команда вводится в формате: "отправить юзеру <user_id> <сообщение>"

    if len(command_parts) < 3:
        await message.answer("Пожалуйста, укажите ID пользователя и сообщение, например: 'отправить всем 123456789 Привет!'")
        return
    user_id = command_parts[1]
    custom_message = command_parts[2]

    # Отправляем сообщение
    try:
        await message.bot.send_message(user_id, custom_message)
        await message.answer("Сообщение отправлено.")
    except Exception as e:
        await message.answer(f"Не удалось отправить сообщение: {e}")
    '''

@router.message(F.text.lower() == "кейген")
async def show_chat_id(message: types.Message):
    # Получаем chat_id из объекта сообщения
    chat_id = message.chat.id
    # Отправляем сообщение пользователю с его chat_id
    await message.answer(f"Ваш Chat ID: {chat_id}")

@router.message(F.text.lower() == "кол-во")
async def buySubscription(message: types.Message):
    await message.answer(f"Количество активных пользователей:\n {db.get_count_users()}")

@router.message(F.text.lower() == "referral_link")
async def buySubscription(message: types.Message):
    await message.answer(kb.TEXT_TEST_MESS)


@router.message(F.text.lower() == "рефералка")
async def buySubscription(message: types.Message):
    await message.answer(
        kb.TEXT_REFERRAL_PROGRAM,
        parse_mode='Markdown'
        )

@router.message(F.text.lower() == "тестовый доступ")
async def buySubscription(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb.user_test_period_kb)
    await message.answer(
        kb.TEXT_TRIAL_PERIOD,
        reply_markup=keyboard,
        parse_mode='Markdown'
        )

@router.callback_query(F.data == "test_period")
async def call_test_period(call: types.CallbackQuery):
    db.get_user_key(call.message.from_user.id)
    await call.message.answer(kb.TEXT_TRIAL_PERIOD_STARTED)
    await call.message.answer(f"Твой ключ:\n {db.get_user_key(call.message.from_user.id)}")


@router.message(F.text.lower() == "")
async def buySubscription(message: types.Message):
    await message.answer(kb.TEXT_TEST_MESS)


@router.message(F.text.lower() == "")
async def buySubscription(message: types.Message):
    await message.answer(kb.TEXT_TEST_MESS)
    
@router.message(F.text.lower() == "")
async def buySubscription(message: types.Message):
    await message.answer(kb.TEXT_TEST_MESS)
    
@router.message(F.text.lower() == "")
async def buySubscription(message: types.Message):
    await message.answer(kb.TEXT_TEST_MESS)
