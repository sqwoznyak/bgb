from aiogram import types
import asyncio



TEXT_TEST_MESS = (
    "✅ Данная кнопка работает корректно."
) 

TEXT_FIELD_PLACEHOLDER = "Никаких блокировок😈"

START_MESSAGE = (
    "👋🏻 Привет!\n\n"
    "Этот Telegram-бот предназначен для выдачи доступа к нашим серверам."
)

BUY_MESSAGE = (
    "💳 К оплате принимаются карты РФ:\n"
    "Visa, MasterCard, МИР.\n"
    "Для полного доступа выберите удобный для вас тариф:\n\n"
    "⚠️ Нажимая кнопку 'Оплатить', вы принимаете наше Пользовательское соглашение."
)


HELP_MESSAGE = "🆘 Помощь"

TEXT_BILL_ONE_MONTH = (
    "🎉 Благодарим за доверие!\n"
    "Ваш заказ: подписка на 1 месяц\n"
    "Итого к оплате: 269₽"
)

TEXT_BILL_THREE_MONTH = (
    "🎉 Благодарим за доверие!\n"
    "Ваш заказ: подписка на 3 месяца\n"
    "Итого к оплате: 699₽"
)

TEXT_BILL_ONE_YEAR = (
    "🎉 Благодарим за доверие!\n"
    "Ваш заказ: подписка на 1 год\n"
    "Итого к оплате: 2299₽"
)

TEXT_USER_MAIN = (
    '🌐 Добро пожаловать в RemoteReaperBot! 🤖\n\n'
    '🔍 Статус подписки: Проверьте срок действия вашей подписки, узнайте информацию о текущем тарифе и другие детали прямо здесь!\n\n'
    '🔑 Ваш ключ: Нажмите, чтобы получить ваш уникальный ключ доступа.\n\n'
    '🆘 Помощь: Здесь вы найдете FAQ и контакты поддержки. Если у вас возникли вопросы или проблемы, мы всегда готовы помочь!\n\n'
    '🔄 Чтобы продолжить, выберите соответствующий раздел в меню или напишите команду, которую хотите выполнить.'
)

TEXT_SUCCESS_PAY = (
    "✅ **Оплата успешно проведена!**\n"
)

TEXT_FAIL_PAY = (
    "⚠️ **Оплата не была завершена успешно.**\n"
    "Пожалуйста, проверьте введенные данные и попробуйте еще раз. "
    "Если проблема сохраняется, свяжитесь с нашей поддержкой для получения помощи."
)

TEXT_REFERRAL_PROGRAM = (
    "🌟 **Присоединяйтесь к нашей реферальной программе!**\n"
)

TEXT_TRIAL_PERIOD = (
    "🎉 **Начните с бесплатного тестового периода на 3 дня!**\n"
)

start_kb = [
        [
            types.KeyboardButton(text="Купить"), types.KeyboardButton(text="Тестовый доступ")
        ],
        [
            types.KeyboardButton(text="Пользовательское соглашение")
        ],
    ]



main_kb = [
        [
            types.KeyboardButton(text="Главное меню")
        ],
    ]

buy_kb = [
        [
            types.InlineKeyboardButton(text="Подписка на 1 месяц: 299₽", callback_data="one_month")
        ],
        [
            types.InlineKeyboardButton(text="Подписка на 3 месяца: 699₽", callback_data="three_month")
        ],
        [
            types.InlineKeyboardButton(text="Подписка на 1 год: 2299₽", callback_data="one_year")
        ],
    ]

user_kb = [
        [
            types.KeyboardButton(text="Статус"), types.KeyboardButton(text="Купить")
        ],
        [
            types.KeyboardButton(text="Ключ"), types.KeyboardButton(text="Помощь")
        ],
    ]

user_agr_kb = [
        [
            types.InlineKeyboardButton(text="Назад", callback_data="back")
        ],

    ]

user_test_period_kb = [
        [
            types.InlineKeyboardButton(text="Тестовый период", callback_data="test_period")
        ],

        [
            types.InlineKeyboardButton(text="Купить", callback_data="back")
        ],

    ]
