import config
import json
import uuid
import asyncio
import random
import string

def get_user_status(user_id):
    return "admin"   #start/user/admin

def add_user(status, username, user_id, end_date, server):
    pass

def get_key(user_name):
    for key in config.client.get_keys():
        if key.name == user_name:
            result = key.access_url
            break
        else:
            result = 'Твоя подписка не активна:('
    return result

def generate_key(length=16):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
