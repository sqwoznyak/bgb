import sqlite3
import time
import json
import requests

class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def close(self):
        self.connection.close()

    def create_tables(self):
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
        self.connection.commit()

    def is_key_valid(self, key_value):
        now = int(time.time())
        with self.connection:
            result = self.cursor.execute(
                "SELECT `end_date` FROM `key_table` WHERE `key` = ?",
                (key_value,)
            ).fetchone()

        if result is None:
            return False

        end_date = result[0]
        return end_date > now

    def load_balancer(self):
        # Тут надо обращаться к БД, парсить сервера из таблиц
        # В API есть экспериментальный метод https://ApiUrl/experimental/server/metrics
        # Но его в нашей версии по всей видимости пока выкинули
        # Думаю, что тут можно организовать пока без метрик с активными сессиями
        # А просто балансировать количество человек на машине
        # Типа если 2 сервера и на первом 10, а на втором 9, то будем давать ключ на тот сервак, где 9 человек. чет такое.
        self.cursor.execute('''
            SELECT server_ip FROM "servers-tabels"
            WHERE server_status = 1
        ''')
        rows = self.cursor.fetchall()

        candidates = []

        for (server_ip,) in rows:
            try:
                data = json.loads(server_ip)
                api_url = data["apiUrl"]
                cert_sha = data["certSha256"]
            except (json.JSONDecodeError, KeyError):
                continue

            try:
                response = requests.get(
                    f"{api_url}/access-keys",
                    headers={"Shadowbox-Cert-Sha256": cert_sha},
                    timeout=10,
                    verify=False
                )
                response.raise_for_status()
                key_count = len(response.json().get("accessKeys", []))
                candidates.append((key_count, api_url, cert_sha))
            except Exception as e:
                print(f"[!] Сервер {api_url} недоступен: {e}")
                continue

        if not candidates:
            return None
        _, best_url, best_cert = min(candidates, key=lambda x: x[0])
        return {"apiUrl": best_url, "certSha256": best_cert}


db = Database("/home/sbuyanov/Documents/git/bgb/webapp/users.db")

#print(db.load_balancer())
