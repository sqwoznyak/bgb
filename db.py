import time
import sqlite3
from datetime import datetime, timezone


# Функция для человеческого вида отметки времени
def format_timestamp(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def close(self):
        self.connection.close()

    def create_tables(self):
<<<<<<< HEAD

=======
        
        # создаём таблицы
>>>>>>> 9ef5fdc (поправил поле active)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS `Servers-tabels` (
                `server_id` INTEGER PRIMARY KEY NOT NULL UNIQUE,
                `cluster` TEXT NOT NULL,
<<<<<<< HEAD
                `server_status` INTEGER NOT NULL CHECK(server_status IN (0, 1)),
=======
                `server_status` INTEGER NOT NULL DEFAULT 1 CHECK(server_status IN (0, 1)),
>>>>>>> 9ef5fdc (поправил поле active)
                `server_ip` TEXT NOT NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Client_table (
                tg_id INTEGER PRIMARY KEY,
                username TEXT,
                role TEXT NOT NULL DEFAULT 'start',
                referal_id INTEGER,
                `active` INTEGER NOT NULL DEFAULT 0 CHECK(active IN (0, 1)),
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
        start_date = int(time.time())
        end_date = start_date + duration_days * 86400

        with self.connection:
            self.cursor.execute('''
            INSERT INTO `key_table` (tg_id, `key_name`, `start_date`, `end_date`, `key`)
            VALUES (?, ?, ?, ?, ?)
            ''', (tg_id, key_name, start_date, end_date, key))

    def get_user_key(self, tg_id):
        with self.connection:
            result = self.cursor.execute(
                "SELECT `key` FROM `key_table` WHERE `tg_id` = ?",
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
                "SELECT `tg_id`, `active` FROM `Client_table`"
            ).fetchall()

    # Получение даты окончания подписки активного ключа
    def get_user_end_sub(self, tg_id):
        with self.connection:
            result = self.cursor.execute(
                "SELECT `end_date` FROM `key_table` WHERE `tg_id` = ?",
                (tg_id,)
            ).fetchone()
            return format_timestamp(result[0]) if result else "У вас нет подписки"

    # Подсчёт пользователей
    def get_count_users(self):
        with self.connection:
            result = self.cursor.execute(
                "SELECT COUNT(DISTINCT tg_id) FROM key_table WHERE key IS NOT NULL AND key != ''"
            ).fetchone()
            return result[0]

    def add_sub(self, tg_id, description):
        with self.connection:
            now = int(time.time())

            match description:
                case '1 месяц':
                    duration_days = 30
                case '3 месяца':
                    duration_days = 90
                case '12 месяцев':
                    duration_days = 365

            self.cursor.execute(
                "SELECT MAX(`end_date`) FROM `key_table` WHERE `tg_id` = ? AND `end_date` > ?",
                (tg_id, now)
            )
            result = self.cursor.fetchone()

            if result:
                key = result[0]
                current_end_date = result[1]

                # Продлеваем от max(now, current_end_date)
                start_point = max(now, current_end_date)
                new_end_date = start_point + duration_days * 86400

                # Обновляем end_date
                self.cursor.execute(
                    '''
                    UPDATE `key_table`
                    SET `end_date` = ?
                    WHERE `tg_id` = ? AND `key` = ? AND `active` = 1
                    ''',
                    (new_end_date, tg_id, key)
                )

                # Обновляем роль, если была 'start' → ставим 'user'
                self.cursor.execute(
                    '''
                    UPDATE `client_table`
                    SET `role` = 'user'
                    WHERE `tg_id` = ? AND `role` = 'start'
                    ''',
                    (tg_id,)
                )

            else:
                # На случай если по какой-то причине ключа нет
                print(f'❗ Активный ключ для tg_id={tg_id} не найден.')



            self.cursor.execute('''
                INSERT INTO `key_table` (tg_id, `key_name`, `start_date`, `end_date`, `key`)
                VALUES (?, ?, ?, ?, ?)
            ''', (tg_id, key_name, start_date, end_date, key))

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


    def set_active(self, tg_id, active):
        with self.connection:
            return self.cursor.execute(
                "UPDATE `Client_table` SET `active` = ? WHERE `tg_id` = ?",
                (active, tg_id)
            )

    





