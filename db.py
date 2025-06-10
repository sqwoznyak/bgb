###################################################################
# Проверить здешний бэкэнд
###################################################################
# Начать добавлять челиков со старта и навешивать потом атры
# Те для тех кто потраил фришную версию, спамитть что купи полную
###################################################################
# Мб есть смысл скачать какую то sqlstudio
# ДЛя наглядного смотрения че в табе после наших рук
##########################################№№№№№####################
# Брал отсюда 
# переделал бд под новый дизайн. убрал маты паши
###################################################################

import sqlite3
from datetime import datetime, timedelta

class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def close(self):
        self.connection.close()

    def create_tables(self):
        # создаём таблицу без server — базовая версия
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                tg_id INTEGER PRIMARY KEY,
                username TEXT,
                key TEXT,
                key_name TEXT,
                duration_days INTEGER,
                activation_date TEXT
            )
        ''')
        self.connection.commit()

        # проверим, есть ли колонка server
        self.cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in self.cursor.fetchall()]
        print("[DEBUG] Existing columns in users:", columns)

        if "server" not in columns:
            print("[DEBUG] Adding column server to users table...")
            self.cursor.execute("ALTER TABLE users ADD COLUMN server TEXT")
            self.connection.commit()

        # создаём все остальные таблицы
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS `Servers-tabels` (
                `server_id` INTEGER PRIMARY KEY NOT NULL UNIQUE,
                `cluster` TEXT NOT NULL,
                `server_status` INTEGER NOT NULL CHECK(server_status IN (0, 1)),
                `server_ip` TEXT NOT NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Client_table (
                tg_id INTEGER PRIMARY KEY,
                username TEXT,
                role TEXT DEFAULT 'start',
                referal_id INTEGER,
                created_time INTEGER
            )
        ''')
    
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS `key_table` (
                `tg_id` INTEGER NOT NULL,
                `key_name` TEXT NOT NULL,
                `start_date` INTEGER NOT NULL,
                `end_date` INTEGER NOT NULL,
                `key` TEXT PRIMARY KEY NOT NULL UNIQUE,
                `active` INTEGER NOT NULL CHECK(active IN (0, 1)),
                FOREIGN KEY(`tg_id`) REFERENCES `Client_table`(`tg_id`)
            );
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS `Transaction_table` (
                `tg_id` INTEGER NOT NULL,
                `description` TEXT NOT NULL,
                `json_config` TEXT NOT NULL UNIQUE,
                FOREIGN KEY(`tg_id`) REFERENCES `Client_table`(`tg_id`)
            )
        ''')
        self.connection.commit()

    # Client_table methods
    def add_user(self, tg_id, username, role="start", referal_id=0):
        created_time = int(datetime.now().timestamp())
        with self.connection:
            self.cursor.execute('''
            INSERT INTO `Client_table` (tg_id, username, role, referal_id, created_time)
            VALUES (?, ?, ?, ?, ?)
            ''', (tg_id, username, role, referal_id, created_time))

    def user_exists(self, tg_id):
        with self.connection:
            result = self.cursor.execute(
                "SELECT * FROM `Client_table` WHERE `tg_id` = ?",
                (tg_id,)
            ).fetchone()
            return result is not None

    def get_user_role(self, tg_id):
        with self.connection:
            result = self.cursor.execute(
                "SELECT `role` FROM `Client_table` WHERE `tg_id` = ?",
                (tg_id,)
            ).fetchone()
            return result[0] if result else None
        
    # Обновляем роль у пользователя в Client_table по tg_id
    def set_user_role(self, tg_id, role):
        self.cursor.execute(
            "UPDATE Client_table SET role = ? WHERE tg_id = ?",
            (role, tg_id)
        )
        self.connection.commit()

    # Проверка уникальности выданного ключа
    def key_exists(self, key_value):
        with self.connection:
            result = self.cursor.execute(
                "SELECT COUNT(*) FROM 'key_table' WHERE key = ?", (key_value,)
            ).fetchone()[0]
            return result > 0

    # key_table methods
    def add_key(self, tg_id, key_name, key, duration_days):
        while self.key_exists(key):
            from utils import generate_key
            key = generate_key()
        start_date = int(datetime.now().timestamp())
        end_date = int((datetime.now() + timedelta(days=duration_days)).timestamp())
        with self.connection:
            self.cursor.execute('''
            INSERT INTO `key_table` (tg_id, `key_name`, `start_date`, `end_date`, `key`, `active`)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (tg_id, key_name, start_date, end_date, key, 1))

    def get_user_key(self, tg_id):
        with self.connection:
            result = self.cursor.execute(
                "SELECT `key` FROM `key_table` WHERE `tg_id` = ? AND `active` = 1",
                (tg_id,)
            ).fetchone()
            return result[0] if result else None

    def deactivate_key(self, tg_id):
        with self.connection:
            self.cursor.execute(
                "UPDATE `key_table` SET `active` = 0 WHERE `tg_id` = ?",
                (tg_id,)
            )

    # Transaction_table methods
    def add_transaction(self, tg_id, description, json_config):
        with self.connection:
            self.cursor.execute('''
            INSERT INTO `Transaction_table` (tg_id, description, json_config)
            VALUES (?, ?, ?)
            ''', (tg_id, description, json_config))

    def get_transactions(self, tg_id):
        with self.connection:
            return self.cursor.execute(
                "SELECT `description`, `json_config` FROM `Transaction_table` WHERE `tg_id` = ?",
                (tg_id,)
            ).fetchall()

    # Servers_table methods
    def add_server(self, server_id, cluster, server_status, server_ip):
        with self.connection:
            self.cursor.execute('''
            INSERT INTO `Servers-tabels` (server_id, cluster, `server_status`, `server_ip`)
            VALUES (?, ?, ?, ?)
            ''', (server_id, cluster, server_status, server_ip))

    def get_server_status(self, server_id):
        with self.connection:
            result = self.cursor.execute(
                "SELECT `server_status` FROM `Servers-tabels` WHERE `server_id` = ?",
                (server_id,)
            ).fetchone()
            return result[0] if result else None
 # NEW methods 28.02.2025
 # Обновление статуса сервера
    def update_server_status(self, server_id, new_status):
        with self.connection:
            self.cursor.execute(
                "UPDATE `Servers-tabels` SET `server_status` = ? WHERE `server_id` = ?",
                (new_status, server_id)
            )

    # Удаление пользователя
    def delete_user(self, tg_id):
        with self.connection:
            self.cursor.execute("DELETE FROM `Client_table` WHERE `tg_id` = ?", (tg_id,))

    # Получение всех активных ключей
    def get_active_keys(self):
        with self.connection:
            return self.cursor.execute(
                "SELECT `tg_id`, `key_name`, `key` FROM `key_table` WHERE `active` = 1"
            ).fetchall()    

    # Обновление роли пользователя
    def update_user_role(self, tg_id, new_role):
        with self.connection:
            self.cursor.execute(
                "UPDATE `Client_table` SET `role` = ? WHERE `tg_id` = ?",
                (new_role, tg_id)
            )

    # Получение списка всех серверов
    def get_all_servers(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `Servers-tabels`").fetchall()
 # NEW methods 22.05.2025. Добавление старых методов
 # Получение всех пользователей с их ролями
    def get_users(self):
        with self.connection:
            return self.cursor.execute(
                "SELECT `tg_id`, `role` FROM `Client_table`"
            ).fetchall()

    # Получение даты окончания подписки активного ключа
    def get_user_end_sub(self, tg_id):
        with self.connection:
            result = self.cursor.execute(
                "SELECT `end_date` FROM `key_table` WHERE `tg_id` = ? AND `active` = 1",
                (tg_id,)
            ).fetchone()
            return result[0] if result else None

    # Подсчёт пользователей с активными ключами
    def get_count_users(self):
        with self.connection:
            result = self.cursor.execute(
                "SELECT COUNT(*) FROM `key_table` WHERE `key` IS NOT NULL AND `active` = 1"
            ).fetchone()
            return result[0]

    # Добавление подписки с учётом продления
    def add_sub(self, tg_id, key_name, key, duration_days):
        with self.connection:
            now = int(datetime.now().timestamp())
            self.cursor.execute(
                "SELECT MAX(`end_date`) FROM `key_table` WHERE `tg_id` = ? AND `end_date` > ?",
                (tg_id, now)
            )
            result = self.cursor.fetchone()
            if result and result[0]:
                start_date = result[0] + 86400  # на следующий день
            else:
                start_date = now

            end_date = start_date + duration_days * 86400

            self.cursor.execute('''
                INSERT INTO `key_table` (tg_id, `key_name`, `start_date`, `end_date`, `key`, `active`)
                VALUES (?, ?, ?, ?, ?, 1)
            ''', (tg_id, key_name, start_date, end_date, key))

    # Деактивация всех просроченных ключей
    def remove_expired_keys(self):
        now = int(datetime.now().timestamp())
        with self.connection:
            self.cursor.execute(
                "UPDATE `key_table` SET `active` = 0 WHERE `end_date` < ? AND `active` = 1",
                (now,)
            )

    # Назначение администратора по нику
    def set_admin_priv(self, username):
        allowed_nicknames = ["sqrt38", "hythe7"]
        if username in allowed_nicknames:
            with self.connection:
                self.cursor.execute(
                    "UPDATE `Client_table` SET `role` = 'admin' WHERE `username` = ?",
                    (username,)
                )
                print(f"Role 'admin' successfully set for {username}")
        else:
            print(f"Access denied: {username} is not allowed to be an admin.")

    





