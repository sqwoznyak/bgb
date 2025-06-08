import os
import pytest
from db import Database

TEST_DB_PATH = 'test.db'

@pytest.fixture(scope="module")
def db_instance():
    # удаляем старую test.db
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    # создаём экземпляр Database
    db = Database(TEST_DB_PATH)
    yield db

    # teardown
    db.close()
    os.remove(TEST_DB_PATH)

### TESTS ###

def test_add_user(db_instance):
    db_instance.add_user(1111, 'test_user', 'user', 0)

    exists = db_instance.user_exists(1111)
    assert exists == True

def test_add_key_and_get_user_key(db_instance):
    db_instance.add_key(1111, 'test_key', 987654321, 30)
    key_value = db_instance.get_user_key(1111)
    assert key_value == 987654321

def test_deactivate_key(db_instance):
    db_instance.deactivate_key(1111)
    key_value = db_instance.get_user_key(1111)
    assert key_value == None

def test_add_transaction_and_get_transactions(db_instance):
    db_instance.add_transaction(1111, 'test_transaction', '{"amount":100}')
    transactions = db_instance.get_transactions(1111)
    assert len(transactions) == 1
    assert transactions[0][0] == 'test_transaction'

def test_add_server_and_get_server_status(db_instance):
    db_instance.add_server(1, 'Cluster-1', 1, '192.168.0.1')
    status = db_instance.get_server_status(1)
    assert status == 1

def test_update_server_status(db_instance):
    db_instance.update_server_status(1, 0)
    status = db_instance.get_server_status(1)
    assert status == 0

def test_get_active_keys(db_instance):
    db_instance.add_sub(1111, 'sub_test', 123456789, 7)
    active_keys = db_instance.get_active_keys()
    assert any(key[0] == 1111 for key in active_keys)
