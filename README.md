# BGB

## Описание проекта:

Проект представляет собой сервис для предоставления доступа к VPN через Telegram-бот, который выдает динамические ключи пользователям. Эти ключи обеспечивают подключение к VPN-серверу, выбираемому на основе выбранного сервера/текущей нагрузки.

## Основные компоненты архитектуры:

### Динамический ключ:
Динамический ключ cоздается для повышения гибкости VPN-соединений. 
В отличие от статичных ключей, которые фиксируются на одном сервере, динамические ключи генерируются для каждого пользователя индивидуально и могут меняться автоматически при каждом подключении. Это позволяет администратору менять серверные данные без необходимости вмешательства пользователя. 

### Telegram-бот:

Пользователь взаимодействует с ботом в Telegram для получения динамического ключа доступа к VPN.
Бот генерирует динамические ключи Outline для пользователей.
### Веб-сервер:

Получив запрос от клиента с динамическим ключом, веб-сервер проксирует его на веб-приложение.
### Веб-приложение:

Веб-приложение проверяет корректность динамического ключа и на основе текущей нагрузки серверов выбирает оптимальный сервер для подключения.
В ответ приложение отправляет данные для подключении пользователя к серверу.
### VPN-сервера:

Серверы VPN принимают пользователей на основе данных, предоставленных веб-приложением.

## Архитектура сервиса и модель базы данных
![alt text](image.png)


## Cтек технологий:
 - Linux
 - Shadowsocks
 - NGINX: Веб-сервер для перенаправления запросов к веб-приложению.
 - FastAPI: для обработки запросов и распределения пользователей по VPN-серверам.
 - Aiogram: библиотека для работы с Telegram API, используемая для создания телеграм-бота
 - Python3: для генерации динамических ключей и взаимодействия с инфраструктурой.
 - sqlite3: для взаимодействия с БД

## Исполнители
- Буянов Семён, студент группы С01-019, КБ ФРКТ МФТИ
- Галманов Павел, студент группы С01-019, КБ ФРКТ МФТИ
- Белугин Егор, студент группы С01-019, КБ ФРКТ МФТИ


