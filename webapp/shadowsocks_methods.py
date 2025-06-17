import requests
from db import Database
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import utils
import secrets

def valid_user_on_server(server: dict, key_value: str) -> bool:
    #print(f"{server['apiUrl']}/access-keys")
    try:
        response = requests.get(
            f"{server['apiUrl']}/access-keys",
            headers={"Shadowbox-Cert-Sha256": server["certSha256"]},
            timeout=10,
            verify=False
        )
        response.raise_for_status()
        access_keys = response.json().get("accessKeys", [])
    except Exception as e:
        print(f"[!] Ошибка при запросе к серверу: {e}")
        return False

    for key in access_keys:
        #print(key)
        if key.get("name") == key_value:
            return True
    return False

def add_user_on_server(server: dict, key_name: str, method="chacha20-ietf-poly1305", password=None, port=None, limit_bytes=None) -> bool:
    """
    Создаёт нового access key на сервере Outline.

    Args:
        server (dict): {'apiUrl': ..., 'certSha256': ...}
        key_name (str): Имя ключа (name)
        method (str): Метод шифрования (по умолчанию chacha20-ietf-poly1305)
        password (str | None): Пароль. Если None — генерируется автоматически.
        port (int | None): Порт. Если None — сервер сам выберет.
        limit_bytes (int | None): Ограничение трафика (в байтах), если нужно.

    Returns:
        bool: True — если успешно создан, иначе False
    """
    url = f"{server['apiUrl']}/access-keys"
    headers = {"Shadowbox-Cert-Sha256": server["certSha256"]}
    
    if password is None:
        password = secrets.token_urlsafe(12)

    payload = {
        "name": key_name,
        "method": method,
        "password": password
    }

    if port:
        payload["port"] = port
    if limit_bytes:
        payload["limit"] = {"bytes": limit_bytes}

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=10,
            verify=False
        )
        response.raise_for_status()
        print(f"[+] Ключ '{key_name}' успешно создан")
        return True
    except Exception as e:
        print(f"[!] Ошибка при создании ключа '{key_name}': {e}")
        return False

def get_key_from_server(server: dict, key_name: str) -> str | None:
    """
    Возвращает accessUrl ключа с именем key_name.
    Если ключа нет — создаёт его. Если всё прошло успешно — возвращает accessUrl, иначе None.

    Args:
        server (dict): объект с apiUrl и certSha256
        key_name (str): имя ключа (поле name)

    Returns:
        str | None: accessUrl или None, если не удалось получить
    """
    if not server:
        print("❌ Нет доступных серверов")
        return None

    print(f"{server['apiUrl']}")

    # Проверка существования ключа
    if not valid_user_on_server(server, key_name):
        print(f"⚠️ Ключ '{key_name}' не найден, создаём...")
        if not add_user_on_server(server, key_name):
            print("❌ Ошибка при создании ключа")
            return None
        print("✅ Ключ создан")

    # Повторная проверка и получение URL
    try:
        response = requests.get(
            f"{server['apiUrl']}/access-keys",
            headers={"Shadowbox-Cert-Sha256": server["certSha256"]},
            timeout=10,
            verify=False
        )
        response.raise_for_status()
        access_keys = response.json().get("accessKeys", [])
        for key in access_keys:
            if key.get("name") == key_name:
                return key.get("accessUrl")
    except Exception as e:
        print(f"[!] Ошибка при получении ключей: {e}")
        return None

    print("❌ Ключ не найден даже после создания")
    return None

#print(db.load_balancer())
#server=db.load_balancer()
#server = db.load_balancer()
#access_url = get_key_from_server(server, "sqrt38")
#print(access_url)
#print(utils.parse_ss_url(access_url))

