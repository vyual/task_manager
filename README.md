# Инструкция по запуску
## 1. Склонируйте репозиторий

`git clone https://github.com/vyual/task_manager`

## 2. Создайте venv

`cd task_manager/`
`python -m venv`

## 3. Установите зависимости

`pip install -r requirements.txt`

## 4. Укажите параметры подключения к базе

### 1. Переименуйте файл окружения `.env.dist` в `.env`
### 2. Измените `DATABASE_URL`
### 3. Укажите остальные параметры
POSTGRES_DB (название бд),

POSTGRES_USER (имя пользователя),

POSTGRES_PASSWORD (пароль пользователя)

# Important: есть возможность запустить базу с помощью Docker:

`docker compose build`

`docker compose up -d`
