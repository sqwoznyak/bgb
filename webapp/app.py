from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from urllib.parse import urlparse
import base64

app = FastAPI()

# Функция для декодирования base64
def decode_base64(data):
    # Добавляем недостающие '=' для корректного декодирования
    data += '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data).decode('utf-8')

# Функция для разбора Shadowsocks URL
def parse_ss_url(ss_url):
    parsed_url = urlparse(ss_url)
    if parsed_url.scheme != 'ss':
        print("Invalid URL scheme.")
        return None

    try:
        # Декодируем информацию пользователя из base64
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

# Функция для получения конфигурации по user_id
def get_config_by_id(user_id):
    # Пример URL, который обычно берется из БД
    ss_url = "ss://Y2hhY2hhMjAtaWV0Zi1wb2x5MTMwNTpIRWlobVQxdzBqTWNJalF3N3VNTmFR@109.206.241.37:56366/?outline=1"
    return parse_ss_url(ss_url)

# Добавляем поддержку CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def force_https(request: Request, call_next):
    if request.url.scheme != "https":
        url = request.url.replace(scheme="https", netloc=f"{request.url.hostname}:443")
        return RedirectResponse(url, status_code=307)
    return await call_next(request)

# Маршрут для корневого запроса
@app.get("/")
async def root():
    return {"message": "Hello World"}

# Маршрут для получения данных конфигурации
@app.get("/key")
async def get_connect_data():
    data = get_config_by_id(123)
    if data is None:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return data
