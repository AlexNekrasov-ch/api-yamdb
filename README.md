<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Django-5.1-green?style=for-the-badge&logo=django&logoColor=white" alt="Django">
  <img src="https://img.shields.io/badge/DRF-3.15-red?style=for-the-badge&logo=django&logoColor=white" alt="DRF">
  <img src="https://img.shields.io/badge/JWT-simplejwt-orange?style=for-the-badge&logo=json-web-tokens&logoColor=white" alt="JWT">
  <img src="https://img.shields.io/badge/SQLite-lightgrey?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/license-MIT-brightgreen?style=for-the-badge" alt="License">
</p>

<h1 align="center">🎬 YaMDb API</h1>

<p align="center">
  <strong>Yet Another Movie Database</strong> — RESTful API для сбора отзывов на фильмы, книги и музыку.
  <br>
  Учебный проект курса <a href="https://practicum.yandex.ru/">Яндекс Практикум</a>.
</p>

---

## 📋 Содержание

- [О проекте](#-о-проекте)
- [Функционал](#-функционал)
- [Технологии](#-технологии)
- [Установка и запуск](#-установка-и-запуск)
- [API Endpoints](#-api-endpoints)
- [Модели данных](#-модели-данных)
- [Права доступа](#-права-доступа)
- [Тестирование](#-тестирование)
- [Лицензия](#-лицензия)

---

## 🎯 О проекте

**YaMDb** позволяет пользователям:

- Просматривать **произведения** (фильмы, книги, музыка), сгруппированные по **категориям** и **жанрам**
- Оставлять **рецензии** с оценкой от 1 до 10 на каждое произведение
- Комментировать рецензии других пользователей
- Видеть **агрегированный рейтинг** каждого произведения
- Регистрироваться через email с получением JWT-токена для доступа к защищённым ресурсам

### Архитектура проекта

```
api_yamdb/
├── api_yamdb/        # Конфигурация Django-проекта (settings, urls, wsgi)
├── api/              # DRF-приложение: views, serializers, permissions, urls
├── reviews/          # Бизнес-модели: User, Category, Genre, Title, Review, Comment
├── static/           # OpenAPI 3.0 спецификация (redoc.yaml) и seed-данные (CSV)
├── templates/        # HTML-шаблоны (ReDoc)
└── manage.py         # Точка входа Django
tests/                # Набор pytest-тестов (8 файлов)
```

---

## ✨ Функционал

| Возможность | Описание |
|---|---|
| 🔐 **Регистрация и аутентификация** | Регистрация по email с кодом подтверждения, получение JWT |
| 👥 **Управление пользователями** | CRUD для администратора, профиль `/me/` для любого авторизованного |
| 🏷️ **Категории и жанры** | Просмотр без токена, создание и удаление только админом |
| 🎥 **Произведения** | Фильтрация по жанру, категории, году и названию |
| ⭐ **Рецензии** | Одна рецензия на пользователя на произведение, оценка 1–10 |
| 💬 **Комментарии** | Обсуждение рецензий в ветках |
| 📊 **Рейтинг** | Автоматический расчёт среднего рейтинга для каждого произведения |

---

## 🛠 Технологии

| Компонент | Версия |
|---|---|
| **Python** | 3.12 |
| **Django** | 5.1 |
| **Django REST Framework** | 3.15 |
| **djangorestframework-simplejwt** | 5.4 |
| **djoser** | 2.3 |
| **PyJWT** | 2.10 |
| **SQLite** | (встроенная БД) |
| **Pytest** | 8.3 |
| **pytest-django** | 4.9 |
| **Flake8** | 7.1 |
| **Pillow** | 11.0 |

Полный список зависимостей — в файле [`requirements.txt`](requirements.txt).

---

## 🚀 Установка и запуск

### Предварительные требования

- Python 3.12 или выше
- pip (менеджер пакетов)
- virtualenv (рекомендуется)

### Пошаговая инструкция

#### 1. Клонирование репозитория

```bash
git clone https://github.com/AlexNekrasov-ch/api-yamdb.git
cd api-yamdb
```

#### 2. Создание и активация виртуального окружения

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

#### 4. Применение миграций

```bash
python api_yamdb/manage.py migrate
```

#### 5. (Опционально) Загрузка seed-данных

```bash
python api_yamdb/manage.py import_csv_data
```

#### 6. Запуск сервера разработки

```bash
python api_yamdb/manage.py runserver
```

API будет доступно по адресу: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

#### 7. (Опционально) Запуск через Postman

```bash
cd postman_collection
bash set_up_data.sh
```

---

## 📡 API Endpoints

> Все эндпоинты доступны с префиксом `/api/v1/`.
> Полная спецификация OpenAPI 3.0 доступна на странице [`/redoc/`](http://127.0.0.1:8000/redoc/).

### 🔑 Аутентификация

| Метод | Endpoint | Описание | Доступ |
|-------|----------|----------|--------|
| `POST` | `/auth/signup/` | Регистрация нового пользователя | Без токена |
| `POST` | `/auth/token/` | Получение JWT-токена | Без токена |

### 👤 Пользователи

| Метод | Endpoint | Описание | Доступ |
|-------|----------|----------|--------|
| `GET` | `/users/` | Список пользователей (с пагинацией и поиском) | Admin |
| `POST` | `/users/` | Создание пользователя | Admin |
| `GET` | `/users/{username}/` | Детальная информация | Admin |
| `PATCH` | `/users/{username}/` | Частичное обновление | Admin |
| `DELETE` | `/users/{username}/` | Удаление пользователя | Admin |
| `GET` | `/users/me/` | Свой профиль | Любой авторизованный |
| `PATCH` | `/users/me/` | Обновление своего профиля | Любой авторизованный |

### 🏷️ Категории

| Метод | Endpoint | Описание | Доступ |
|-------|----------|----------|--------|
| `GET` | `/categories/` | Список категорий (с пагинацией и поиском) | Без токена |
| `POST` | `/categories/` | Создание категории | Admin |
| `DELETE` | `/categories/{slug}/` | Удаление категории | Admin |

### 🎵 Жанры

| Метод | Endpoint | Описание | Доступ |
|-------|----------|----------|--------|
| `GET` | `/genres/` | Список жанров (с пагинацией и поиском) | Без токена |
| `POST` | `/genres/` | Создание жанра | Admin |
| `DELETE` | `/genres/{slug}/` | Удаление жанра | Admin |

### 🎬 Произведения

| Метод | Endpoint | Описание | Доступ |
|-------|----------|----------|--------|
| `GET` | `/titles/` | Список произведений (фильтрация по `genre`, `category`, `name`, `year`) | Без токена |
| `POST` | `/titles/` | Создание произведения | Admin |
| `GET` | `/titles/{id}/` | Детальная информация (включает рейтинг) | Без токена |
| `PATCH` | `/titles/{id}/` | Частичное обновление | Admin |
| `DELETE` | `/titles/{id}/` | Удаление произведения | Admin |

### ⭐ Рецензии (вложенные в произведения)

| Метод | Endpoint | Описание | Доступ |
|-------|----------|----------|--------|
| `GET` | `/titles/{title_id}/reviews/` | Список рецензий | Без токена |
| `POST` | `/titles/{title_id}/reviews/` | Создание рецензии | Авторизованный |
| `GET` | `/titles/{title_id}/reviews/{review_id}/` | Детальная информация | Без токена |
| `PATCH` | `/titles/{title_id}/reviews/{review_id}/` | Обновление рецензии | Автор / Модератор / Admin |
| `DELETE` | `/titles/{title_id}/reviews/{review_id}/` | Удаление рецензии | Автор / Модератор / Admin |

### 💬 Комментарии (вложенные в рецензии)

| Метод | Endpoint | Описание | Доступ |
|-------|----------|----------|--------|
| `GET` | `/titles/{title_id}/reviews/{review_id}/comments/` | Список комментариев | Без токена |
| `POST` | `/titles/{title_id}/reviews/{review_id}/comments/` | Создание комментария | Авторизованный |
| `GET` | `/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` | Детальная информация | Без токена |
| `PATCH` | `/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` | Обновление комментария | Автор / Модератор / Admin |
| `DELETE` | `/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/` | Удаление комментария | Автор / Модератор / Admin |

---

## 🗄 Модели данных

```
User (кастомная модель)
├── username, email, role (user/moderator/admin)
├── bio, first_name, last_name
└── confirmation_code

Category
├── name, slug (unique)

Genre
├── name, slug (unique)

Title
├── name, year, description
├── category (FK → Category)
└── genres (M2M → Genre)

Review
├── text, score (1–10), pub_date
├── author (FK → User)
├── title (FK → Title)
└── unique: (author, title)

Comment
├── text, pub_date
├── author (FK → User)
└── review (FK → Review)
```

---

## 🔐 Права доступа

| Роль | Описание |
|---|---|
| **Аноним** | Только чтение (GET-запросы к основным ресурсам) |
| **Аутентифицированный пользователь** (`user`) | Чтение + создание рецензий и комментариев |
| **Модератор** (`moderator`) | Права пользователя + редактирование/удаление любых рецензий и комментариев |
| **Администратор** (`admin`) | Полный CRUD на все ресурсы, управление пользователями |
| **Superuser** (Django) | Все права администратора |

---

## 🧪 Тестирование

### Запуск тестов

```bash
# Все тесты
pytest

# Конкретный файл
pytest tests/test_05_review.py

# Конкретный класс
pytest tests/test_05_review.py::Test05ReviewAPI

# С подробным выводом
pytest -vv
```

### Структура тестов

| Файл | Покрытие |
|------|----------|
| `test_00_user_registration.py` | Регистрация, получение токена, админское создание пользователя |
| `test_01_users.py` | CRUD пользователей, `/me/`, проверка ролей |
| `test_02_category.py` | Категории: пагинация, поиск, права доступа |
| `test_03_genre.py` | Жанры: пагинация, поиск, права доступа |
| `test_04_title.py` | Произведения: CRUD, фильтрация, рейтинг |
| `test_05_review.py` | Рецензии: CRUD, уникальность, оценка 1–10 |
| `test_06_comment.py` | Комментарии: CRUD, права доступа |
| `test_07_files.py` | Валидация структуры проекта |

### Линтинг

```bash
flake8                     # Вся кодовая база
flake8 api_yamdb/          # Только приложение (без тестов и миграций)
```

---

## 📄 Лицензия

Проект распространяется под лицензией **MIT**. Подробнее — в файле [LICENSE](LICENSE).

---

