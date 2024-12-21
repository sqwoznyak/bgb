###################################################################
# Проверить здешний бэкэнд
###################################################################
# Начать добавлять челиков со старта и навешивать потом атры
# Так можно заебать бесплатчиков с рекламой
# Те для тех кто потраил фришную версию, спамитть что купи полную
###################################################################
# Мб есть смысл скачать какую то sqlstudio
# ДЛя наглядного смотрения че в табе после наших рук
##########################################№№№№№####################
# Брал отсюда 
# https://www.youtube.com/watch?v=_Zdoo4r0GVQ
###################################################################

import sqlite3
from datetime import datetime, timedelta

class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.create_table()

    def close(self):
        self.connection.close()

    def create_table(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY NOT NULL, 
            username TEXT,
            role TEXT NOT NULL, 
            created_time TEXT NOT NULL,
            transaction_id INTEGER,
            transaction_description TEXT,
            start_date TEXT,
            end_date TEXT,
            server_id INTEGER,
            server_status TEXT,
            key TEXT,
            referral_id INTEGER,
            active INTEGER 
        )
        ''')
        self.connection.commit()

    def user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
            return bool(len(result))

    def get_users(self):
        with self.connection:
            return self.cursor.execute(
                "SELECT `user_id`, `active` FROM `users`"
            ).fetchall()
    
    def get_user_status(self, user_id):
        with self.connection:
            result = self.cursor.execute(
                "SELECT `role` FROM `users` WHERE `user_id` = ?",
                (user_id,)
            ).fetchone()
            return result[0] if result else None
        
    def get_user_end_sub(self, user_id):
        with self.connection:
            result = self.cursor.execute(
                "SELECT `end_date` FROM `users` WHERE `user_id` = ?",
                (user_id,)
            ).fetchone()
            return result[0] if result else None   
        
    def get_key_my_test(self, user_id):
        return "abcdefg"

    def get_user_key(self, user_id): # Вот тут надо полить конечно, генерацию ключа, если его нет
        with self.connection:
            result = self.cursor.execute(
                "SELECT `key` FROM `users` WHERE `user_id` = ?",
                (user_id,)
            ).fetchone()
            return result[0] if result else None 
    
    def get_count_users(self):
        with self.connection:
            result = self.cursor.execute(
                "SELECT `key` FROM `users` WHERE `key` IS NOT NULL AND `key` != ''"
            ).fetchall()
            return len(result)

    def set_admin_priv(self, nickname):
        
        allowed_nicknames = ["sqrt38", "hythe7"] # тут должны быть наши ники

        if nickname in allowed_nicknames:
            with self.connection:
                self.cursor.execute(
                    "UPDATE `users` SET `role` = 'admin' WHERE `username` = ?",
                    (nickname,)
                ) # "UPDATE `users` SET `role` = 'admin' WHERE `username` = ?",
                self.connection.commit()
                print(f"Role 'admin' successfully set for {nickname}")
        else:
            print(f"Access denied: {nickname} is not allowed to be an admin.")


    def set_rwemove_key(user_id):
        pass # Удалять ключи, как ток чел не продлил подписку.

            
    def set_active(self, user_id, active):
        with self.connection:
            return self.cursor.execute(
                "UPDATE `users` SET `active` = ? WHERE `user_id` = ?",
                (active, user_id)
            )
        
    def add_user(self, user_id, username=None, referrer_id=None):
        created_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        role = "start"

        with self.connection:
            if referrer_id is not None:
                return self.cursor.execute("""
                                           INSERT INTO `users` 
                                           (`user_id`, `username`, `role`, `created_time`, `referrer_id` ) VALUES (?,?,?,?,?)""", 
                                           (user_id, username, role, created_time, referrer_id,)
                                           )
            else:
                return self.cursor.execute("""
                                           INSERT INTO `users` 
                                           (`user_id`, `username`, `role`, `created_time` ) VALUES (?,?,?,?)""", 
                                           (user_id, username, role, created_time,)
                                           )

    def add_sub(self, user_id, transaction_id, rate, key, server_id):
        role = "user"

        if rate == "1 месяц":
            rate = 30 
        elif rate == "3 месяца":
            rate = 90 
        elif rate == "12 месяцев":
            rate = 365 

        self.cursor.execute('''
        SELECT max(end_date) FROM `users` WHERE user_id = ? AND end_date > ?
        ''', (user_id, datetime.now().strftime("%Y-%m-%d")))
        result = self.cursor.fetchone()

        if result and result[0]:
            start_date = (datetime.strptime(result[0], "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            start_date = datetime.now().strftime("%Y-%m-%d")

        end_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=rate)).strftime("%Y-%m-%d")

        self.cursor.execute('''
        UPDATE `users`
        SET `role` = ?,
            `transaction_id` = ?,
            `start_date` = ?,
            `end_date` = ?,
            `server_id` = ?,
            `key` = ?
        WHERE `user_id` = ?
        ''', (role, transaction_id, start_date, end_date, server_id, key, user_id))
        self.connection.commit()
    


# Пример использования:
#db = Database('database.db')
#db.add_user(123456)
#user = db.get_user(123456)
#if user:
#    print("User ID:", user['user_id'], "Active:", bool(user['active']))



