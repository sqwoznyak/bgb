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
            `json-config` TEXT NOT NULL UNIQUE,
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
            INSERT INTO `transaction-table` (tg_id, description, json-config)
            VALUES (?, ?, ?)
            ''', (tg_id, description, json_config))

    def get_transactions(self, tg_id):
        with self.connection:
            return self.cursor.execute(
                "SELECT `description`, `json-config` FROM `transaction-table` WHERE `tg_id` = ?",
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



    





