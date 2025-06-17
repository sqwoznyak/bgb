# Установка и запуск Telegram-бота + FastAPI-прокси на VPS Ubuntu 20.04

## Требования
 - Ubuntu 20.04 VPS (минимум 512 МБ RAM)
 - Python 3.10+
 - Git установлен (если используете репозиторий)
 - Порты 443, 80, 8002, 8443, 22 открыты
 - SSL-сертификаты Let's Encrypt

## Структура проекта

```bash
/opt/bgb/
│                #Telegram-бот
├── main.py
├── db.py
├── handlers.py
├── ...
├── .env #для Telegram-бота
└── webapp/      #FastAPI-прокси
    ├── app.py
    ├── main.py
    ├── db.py
    ├── ...
    └── .env #для FastAPI-прокси

/var/lib/bgb/
└── users.db # Одна общая БД

```
 ## Установка системных пакетов
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv git sqlite3 -y
```
## Настройка виртуальных окружений

### Для Telegram-бота
```bash
mkdir -p /opt/bgb/
git clone https://github.com/sqwoznyak/bgb.git
cd /opt/bgb/
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### Создайте .env
С помощью текстого редактора nano создаем .env в корне проекта.
```bash
BOT_TOKEN=ваш_бот_токен
YOUKASSA_ACCOUNT_ID=ваш_yookassa_id
YOUKASSA_SECRET_KEY=ваш_yookassa_secret
DB_PATH=/opt/vpn-service/shared/users.db
```

### Для FastAPI-прокси
```bash
cd /opt/bgb/webapp
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
#### Создайте .env:
```bash
DB_PATH=/var/lib/bgb/users.db
```

## Запуск сервисов

### Бот
```bash
cd /opt/bgb/
source venv/bin/activate
python3 main.py
```
### Webapp
```bash
cd /opt/bgb/webapp
source venv/bin/activate
uvicorn app:create_app \
  --host 0.0.0.0 \
  --port 8080 \
  --factory
```
## Тагет systemd
Опционально

```bash
[Service]
WorkingDirectory=/opt/bgb/
ExecStart=/opt/bgb/venv/bin/python main.py
EnvironmentFile=/opt/bgb/.env
Restart=always
```

Аналогично — для webapp.

## Настройка nginx 

### Установите nginx на ваш VPS
```bash
sudo apt install nginx -y
```
### Получение SSL-сертификатов (для HTTPS)
Если у вас нет сертификатов, можно получить их с помощью Let’s Encrypt.
#### Получение сертификата для вашего домена:
```bash
sudo certbot --nginx -d yourdomain.com
```

Следуйте инструкциям на экране для подтверждения домена и получения сертификатов.

### Конфигурация nginx:

Создание или редактирование конфигурационного файла для webapp

sudo nano /etc/nginx/sites-available/webapp

Пример конфигурации nginx:
```bash
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Редирект с HTTP на HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers on;

    ssl_dhparam /etc/ssl/certs/dhparam.pem;

    # Логи для отладки
    access_log /var/log/nginx/yourdomain.access.log;
    error_log /var/log/nginx/yourdomain.error.log;

    location / {
        proxy_pass http://127.0.0.1:8002;  # Проксируем на FastAPI
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
Обрати внимание, что нужно указать внутри конфига свои данные!

### Генерация Diffie-Hellman параметров для SSL
```bash
sudo openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048
```

##  Проверка конфигурации nginx

Перед перезапуском nginx обязательно проверьте конфигурацию на наличие ошибок:
```bash
sudo nginx -t
```
Если всё в порядке, создайте символическую ссылку для активации вашего приложения:
```bash
sudo ln -s /etc/nginx/sites-available/yourdomain.com /etc/nginx/sites-enabled/
```
Перезапустите nginx:
```bash
sudo systemctl restart nginx
```
## Проверка
Перейдите в браузере по адресу https://yourdomain.com/.

Вы должны увидеть ответ Hello, world!

Далее следуйте инструкциям в Вашем телеграм боте!