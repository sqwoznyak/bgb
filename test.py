import unittest
from datetime import datetime
from db import Database

class TestDatabase(unittest.TestCase):

    def setUp(self):
        # Инициализация базы данных в памяти
        self.db = Database(':memory:')
        self.db.create_table()

    def tearDown(self):
        # Закрытие соединения с базой данных
        self.db.close()

    def test_add_user_and_user_exists(self):
        user_id = '1'
        username = 'user1'
        self.db.add_user(user_id, username)
        self.assertTrue(self.db.user_exists(user_id))
        self.assertFalse(self.db.user_exists('2'))

    def test_get_user_status(self):
        user_id = '2'
        username = 'user2'
        self.db.add_user(user_id, username)
        self.assertEqual(self.db.get_user_status(user_id), 'test')
        self.assertIsNone(self.db.get_user_status('3'))

    def test_set_admin_priv(self):
        username = 'sqrt38'
        user_id = '3'
        self.db.add_user(user_id, username)
        self.db.set_admin_priv(username)
        self.assertEqual(self.db.get_user_status(user_id), 'admin')

        # Проверка отказа доступа
        username2 = 'notallowed'
        user_id2 = '4'
        self.db.add_user(user_id2, username2)
        self.db.set_admin_priv(username2)
        self.assertNotEqual(self.db.get_user_status(user_id2), 'admin')

    def test_set_active(self):
        user_id = '5'
        username = 'user5'
        self.db.add_user(user_id, username)
        self.db.set_active(user_id, 1)
        active_status = self.db.get_users()
        self.assertIn((user_id, 1), active_status)

    def test_add_sub(self):
        user_id = '6'
        self.db.add_user(user_id, 'user6')
        self.db.add_sub(user_id, 1, "1 месяц", "key1", 1)
        user_info = self.db.cursor.execute("SELECT `start_date`, `end_date` FROM `users` WHERE `user_id`=?", (user_id,)).fetchone()
        self.assertIsNotNone(user_info)
        self.assertNotEqual(user_info[0], user_info[1])  # Проверка, что даты начала и конца подписки различаются

    def test_create_table(self):
        # Проверка, что таблица создается без ошибок и имеет правильные столбцы
        result = self.db.cursor.execute("PRAGMA table_info(users)").fetchall()
        self.assertTrue(any(x[1] == 'user_id' for x in result))
        self.assertTrue(any(x[1] == 'role' for x in result))

if __name__ == '__main__':
    unittest.main()
