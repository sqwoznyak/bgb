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

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
	#БД часть
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
    pass

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

    
@router.message(F.text.lower() == "")
async def buySubscription(message: types.Message):
    await message.answer(kb.TEXT_TEST_MESS)
    
@router.message(F.text.lower() == "")
async def buySubscription(message: types.Message):
    await message.answer(kb.TEXT_TEST_MESS)
