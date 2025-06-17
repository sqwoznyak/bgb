import base64
from urllib.parse import urlparse
#import shadowsocks_methods as ss


# Функция для декодирования base64
def decode_base64(data):
    data += '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data).decode('utf-8')

# Функция для разбора Shadowsocks URL
def parse_ss_url(ss_url):
    parsed_url = urlparse(ss_url)
    if parsed_url.scheme != 'ss':
        print("Invalid URL scheme.")
        return None

    try:
        decoded_user_info = decode_base64(parsed_url.username)
        method_cipher, password = decoded_user_info.split(':', 1)
    except (base64.binascii.Error, ValueError) as e:
        print(f"Error parsing user info: {e}")
        return None

    if not parsed_url.hostname or not parsed_url.port:
        print("Invalid host or port.")
        return None

    config = {
        "server": parsed_url.hostname,
        "server_port": parsed_url.port,
        "password": password,
        "method": method_cipher
    }

    return config
