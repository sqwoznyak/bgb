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
        if not db.user_exists(message.from_user.id):
            db.add_user(message.from_user.id, message.from_user.username, referrer_id=None)
            db.set_admin_priv(message.from_user.username)
        status = db.get_user_status(message.from_user.id)
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

@router.callback_query(F.data == "one_month")
async def call_buy_one_month_subscription(call: types.CallbackQuery):
    bill= await run_payment(item_1m)
    buy_button = payment.create_pay_button(bill.confirmation.confirmation_url, bill.id)
    await call.message.edit_text(kb.TEXT_BILL_ONE_MONTH, reply_markup=buy_button)

@router.callback_query(F.data == "three_month")
async def call_buy_one_month_subscription(call: types.CallbackQuery):
    pass

@router.callback_query(F.data == "one_year")
async def call_buy_one_month_subscription(call: types.CallbackQuery):
    pass

@router.callback_query(lambda F: F.data and F.data.startswith('buying'))
async def process_callback(callback_query: types.CallbackQuery):
    data = callback_query.data.split(",")
    action = data[0]
    payment_id = data[1]

    # Ищим платеж
    payment = Payment.find_one(payment_id)
    
    # Сообщаем, что проверяем статус оплаты
    await callback_query.message.bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=f"Проверка статуса оплаты. Пожалуйста, подождите..."
    )

    while payment.status == 'pending':
        # Подождем перед следующей проверкой
        await asyncio.sleep(3)
        
        # Обновляем статус платежа
        payment = Payment.find_one(payment_id)

        # Сообщаем тикущий статус (например, раз в несколько циклов, чтобы избежать спама)
        await callback_query.message.bot.send_message(
            chat_id=callback_query.message.chat.id,
            text=f"Статус оплаты: {payment.status}"
        )

    # После выхода из цикла отправляем финальное сообщение в зависимости от статуса
    if payment.status == 'succeeded':
        # Добавление в БД и тп и тд
        db.add_sub(callback_query.message.chat.id, payment.id, payment.description, "000", "000" )
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
    #TEXT_GET_KEY =  db.get_user_key(message.from_user.id) пример будущего использования БД
    await message.answer(TEXT_GET_KEY)

@router.message(F.text.lower() == "статус")
async def buySubscription(message: types.Message):

    #date = db.get_user_end_sub(message.from_user.id)
    TEXT_SUBSCRIPTION_ACTIVE = (
        f"🌟 Ваша подписка активна!\n"
        f"Срок действия: до {date}\n"
        f"Продлите подписку, чтобы сохранить доступ к сервису."
    )
    await message.answer(TEXT_SUBSCRIPTION_ACTIVE)

@router.message(F.text.startswith("Отправить"))
async def sendall(message: types.Message):
    if message.chat.type == 'private':
        if message.from_user.id == 353666482:
            text = message.text[9:]
            users = db.get_users()
            
            for row in users:
                try:
                    await message.bot.send_message(row[0], text)
                    if int(row[1]) != 1:
                        db.set_active(row[0], 1)  # Mark user as active if sent
                except:
                    db.set_active(row[0], 0)  # Mark user as inactive if fails
            
            await message.bot.send_message(message.from_user.id, "Успешная рассылка")  # Send confirmation to admin

@router.message(F.text.lower() == "")
async def buySubscription(message: types.Message):
    await message.answer(kb.TEXT_TEST_MESS)
    
@router.message(F.text.lower() == "")
async def buySubscription(message: types.Message):
    await message.answer(kb.TEXT_TEST_MESS)
