import config
import json
import uuid
from yookassa import Configuration,Payment
from config import youkassa_account_id, youkassa_secret_key
import asyncio
from aiogram import types

Configuration.account_id = youkassa_account_id
Configuration.secret_key = youkassa_secret_key

item_1m = {"description": "1 месяц", "quantity": 1, "value": "269.00", "vat_code": 1, "phone": "79291001001", "return_url": "https://t.me/remotereaperBot"}
item_3m = {"description": "3 месяца", "quantity": 1, "value": "699.00", "vat_code": 1, "phone": "79291001101", "return_url": "https://t.me/remotereaperBot"}
item_1y = {"description": "12 месяцев", "quantity": 1, "value": "2299.00", "vat_code": 1, "phone": "79291001001", "return_url": "https://t.me/remotereaperBot"}

async def payment(item):
    idempotence_key = str(uuid.uuid4())
    
    bill = Payment.create({
        "amount": {
            "value": item["value"],
            "currency": "RUB"
        },
        "payment_method_data": {
            "type": "bank_card"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": item["return_url"]
        },
        "capture": True,
        "description": item["description"],
        "receipt": {
            "items": [
                {
                    "description": item["description"],
                    "quantity": item["quantity"],
                    "amount": {
                        "value": item["value"],
                        "currency": "RUB"
                    },
                    "vat_code": item["vat_code"]
                }
            ],
            "customer": {
                "phone": item["phone"]
            }
        }
    }, idempotence_key)
    
    return bill


async def run_payment(item):
    try:
        payment_result = await payment(item)
        #return payment_result.confirmation.confirmation_url
        return payment_result
    except Exception as e:
        print(f"An error occurred: {e}")

#result = asyncio.run(run_payment(item_1m))
#print(result.confirmation.confirmation_url)
#print(result.id)
#print(result.status)

