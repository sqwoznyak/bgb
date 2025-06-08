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
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS `Client-table` (
            `tg_id` INTEGER PRIMARY KEY NOT NULL,
            `username` TEXT NOT NULL,
            `role` TEXT NOT NULL,
            `referal_id` INTEGER,
            `created_time` INTEGER NOT NULL
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS `Servers-tabels` (
            `server_id` INTEGER PRIMARY KEY NOT NULL UNIQUE,
            `cluster` TEXT NOT NULL,
            `server-status` INTEGER,
            `server-ip` TEXT NOT NULL
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS `key-table` (
            `tg_id` INTEGER NOT NULL,
            `key-name` TEXT NOT NULL,
            `start-date` INTEGER NOT NULL,
            `end-date` INTEGER NOT NULL,
            `key` INTEGER PRIMARY KEY NOT NULL UNIQUE,
            `active` INTEGER,
            FOREIGN KEY(`tg_id`) REFERENCES `Client-table`(`tg_id`)
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS `transaction-table` (
            `tg_id` INTEGER NOT NULL,
            `description` TEXT NOT NULL,
            `json_config` TEXT NOT NULL UNIQUE,
            FOREIGN KEY(`tg_id`) REFERENCES `Client-table`(`tg_id`)
        )
        ''')
        self.connection.commit()

    # Client-table methods
    def add_user(self, tg_id, username, role="start", referal_id=0):
        created_time = int(datetime.now().timestamp())
        with self.connection:
            self.cursor.execute('''
            INSERT INTO `Client-table` (tg_id, username, role, referal_id, created_time)
            VALUES (?, ?, ?, ?, ?)
            ''', (tg_id, username, role, referal_id, created_time))

    def user_exists(self, tg_id):
        with self.connection:
            result = self.cursor.execute(
                "SELECT * FROM `Client-table` WHERE `tg_id` = ?",
                (tg_id,)
            ).fetchone()
            return result is not None

    def get_user_role(self, tg_id):
        with self.connection:
            result = self.cursor.execute(
                "SELECT `role` FROM `Client-table` WHERE `tg_id` = ?",
                (tg_id,)
            ).fetchone()
            return result[0] if result else None

    # Key-table methods
    def add_key(self, tg_id, key_name, key, duration_days):
        start_date = int(datetime.now().timestamp())
        end_date = int((datetime.now() + timedelta(days=duration_days)).timestamp())
        with self.connection:
            self.cursor.execute('''
            INSERT INTO `key-table` (tg_id, `key-name`, `start-date`, `end-date`, `key`, `active`)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (tg_id, key_name, start_date, end_date, key, 1))

    def get_user_key(self, tg_id):
        with self.connection:
            result = self.cursor.execute(
                "SELECT `key` FROM `key-table` WHERE `tg_id` = ? AND `active` = 1",
                (tg_id,)
            ).fetchone()
            return result[0] if result else None

    def deactivate_key(self, tg_id):
        with self.connection:
            self.cursor.execute(
                "UPDATE `key-table` SET `active` = 0 WHERE `tg_id` = ?",
                (tg_id,)
            )

    # Transaction-table methods
    def add_transaction(self, tg_id, description, json_config):
        with self.connection:
            self.cursor.execute('''
            INSERT INTO `transaction-table` (tg_id, description, json_config)
            VALUES (?, ?, ?)
            ''', (tg_id, description, json_config))

    def get_transactions(self, tg_id):
        with self.connection:
            return self.cursor.execute(
                "SELECT `description`, `json_config` FROM `transaction-table` WHERE `tg_id` = ?",
                (tg_id,)
            ).fetchall()

    # Servers-table methods
    def add_server(self, server_id, cluster, server_status, server_ip):
        with self.connection:
            self.cursor.execute('''
            INSERT INTO `Servers-tabels` (server_id, cluster, `server-status`, `server-ip`)
            VALUES (?, ?, ?, ?)
            ''', (server_id, cluster, server_status, server_ip))

    def get_server_status(self, server_id):
        with self.connection:
            result = self.cursor.execute(
                "SELECT `server-status` FROM `Servers-tabels` WHERE `server_id` = ?",
                (server_id,)
            ).fetchone()
            return result[0] if result else None
 # NEW methods 28.02.2025
 # Обновление статуса сервера
    def update_server_status(self, server_id, new_status):
        with self.connection:
            self.cursor.execute(
                "UPDATE `Servers-tabels` SET `server-status` = ? WHERE `server_id` = ?",
                (new_status, server_id)
            )

    # Удаление пользователя
    def delete_user(self, tg_id):
        with self.connection:
            self.cursor.execute("DELETE FROM `Client-table` WHERE `tg_id` = ?", (tg_id,))

    # Получение всех активных ключей
    def get_active_keys(self):
        with self.connection:
            return self.cursor.execute(
                "SELECT `tg_id`, `key-name`, `key` FROM `key-table` WHERE `active` = 1"
            ).fetchall()

    # Обновление роли пользователя
    def update_user_role(self, tg_id, new_role):
        with self.connection:
            self.cursor.execute(
                "UPDATE `Client-table` SET `role` = ? WHERE `tg_id` = ?",
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
                "SELECT `tg_id`, `role` FROM `Client-table`"
            ).fetchall()

    # Получение даты окончания подписки активного ключа
    def get_user_end_sub(self, tg_id):
        with self.connection:
            result = self.cursor.execute(
                "SELECT `end-date` FROM `key-table` WHERE `tg_id` = ? AND `active` = 1",
                (tg_id,)
            ).fetchone()
            return result[0] if result else None

    # Подсчёт пользователей с активными ключами
    def get_count_users(self):
        with self.connection:
            result = self.cursor.execute(
                "SELECT COUNT(*) FROM `key-table` WHERE `key` IS NOT NULL AND `active` = 1"
            ).fetchone()
            return result[0]

    # Добавление подписки с учётом продления
    def add_sub(self, tg_id, key_name, key, duration_days):
        with self.connection:
            now = int(datetime.now().timestamp())
            self.cursor.execute(
                "SELECT MAX(`end-date`) FROM `key-table` WHERE `tg_id` = ? AND `end-date` > ?",
                (tg_id, now)
            )
            result = self.cursor.fetchone()
            if result and result[0]:
                start_date = result[0] + 86400  # на следующий день
            else:
                start_date = now

            end_date = start_date + duration_days * 86400

            self.cursor.execute('''
                INSERT INTO `key-table` (tg_id, `key-name`, `start-date`, `end-date`, `key`, `active`)
                VALUES (?, ?, ?, ?, ?, 1)
            ''', (tg_id, key_name, start_date, end_date, key))

    # Деактивация всех просроченных ключей
    def remove_expired_keys(self):
        now = int(datetime.now().timestamp())
        with self.connection:
            self.cursor.execute(
                "UPDATE `key-table` SET `active` = 0 WHERE `end-date` < ? AND `active` = 1",
                (now,)
            )

    # Назначение администратора по нику
    def set_admin_priv(self, username):
        allowed_nicknames = ["sqrt38", "hythe7"]
        if username in allowed_nicknames:
            with self.connection:
                self.cursor.execute(
                    "UPDATE `Client-table` SET `role` = 'admin' WHERE `username` = ?",
                    (username,)
                )
                print(f"Role 'admin' successfully set for {username}")
        else:
            print(f"Access denied: {username} is not allowed to be an admin.")

    





