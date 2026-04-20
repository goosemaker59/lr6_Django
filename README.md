# 🏋️ Fitness Club API

RESTful API для управления фитнес-клубом, построенное на **Django REST Framework** с **JWT-аутентификацией**, **PostgreSQL** и задокументированное через **Swagger UI**.

---

## 📐 Архитектура базы данных

Проект содержит **5 связанных таблиц**:

```
User (встроенная Django)
 ├── Trainer          (OneToOne → User)   — профиль тренера
 └── MemberProfile    (OneToOne → User)   — профиль участника
      ├── Membership   (ForeignKey → MemberProfile)  — абонемент
      └── Booking      (ForeignKey → MemberProfile)  — запись на занятие
               └── TrainingClass (ForeignKey → Trainer) — групповое занятие
```

| Таблица         | Описание                                             |
|-----------------|------------------------------------------------------|
| `Trainer`       | Тренеры клуба: специализация, опыт, ставка           |
| `MemberProfile` | Профили участников: цель, параметры, контакты        |
| `Membership`    | Абонементы: тариф, статус, срок действия             |
| `TrainingClass` | Групповые занятия: расписание, вместимость, тренер   |
| `Booking`       | Записи участников на занятия + оценка и отзыв        |

---

## 🚀 Быстрый старт

### 1. Клонировать проект

```bash
git clone https://github.com/ваш-username/fitness-club-api.git
cd fitness-club-api/myproject
```

### 2. Создать файл `.env`

```bash
copy .env.example .env   # Windows
cp .env.example .env     # Linux / macOS
```

Отредактируйте `.env` при необходимости (по умолчанию всё работает «из коробки»).

### 3. Запустить Docker-контейнеры

```bash
docker compose up --build
```

### 4. Применить миграции

```bash
docker compose exec web python manage.py migrate
```

### 5. Создать суперпользователя

```bash
docker compose exec web python manage.py createsuperuser
```

### 6. Заполнить БД тестовыми данными (опционально)

```bash
docker compose exec web python manage.py seed_data
```

### 7. Готово! 🎉

| Адрес | Описание |
|---|---|
| http://localhost:8000/swagger/ | Swagger UI (документация + тест) |
| http://localhost:8000/redoc/ | ReDoc (альтернативная документация) |
| http://localhost:8000/admin/ | Django Admin |
| http://localhost:8000/api/ | Корень API |

---

## 🔐 Аутентификация через JWT

### Шаг 1 — Получить токен

```http
POST /api/token/
Content-Type: application/json

{
  "username": "member_петров",
  "password": "member123"
}
```

Ответ:

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Шаг 2 — Использовать токен

Добавьте заголовок ко всем запросам:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Шаг 3 — Обновить токен (после истечения 1 часа)

```http
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Использование авторизации в Swagger UI

1. Откройте http://localhost:8000/swagger/
2. Нажмите кнопку **Authorize** 🔒 (в верхнем правом углу)
3. В поле **Bearer** введите: `Bearer <ваш_access_токен>`
4. Нажмите **Authorize** → **Close**
5. Все запросы теперь отправляются с вашим токеном ✅

---

## 📡 Эндпоинты API

### Аутентификация

| Метод | URL | Описание | Авторизация |
|---|---|---|---|
| POST | `/api/register/` | Регистрация нового пользователя | ❌ |
| POST | `/api/token/` | Получить JWT токен | ❌ |
| POST | `/api/token/refresh/` | Обновить access токен | ❌ |
| POST | `/api/token/verify/` | Проверить токен | ❌ |
| GET/PUT/PATCH | `/api/me/` | Данные текущего пользователя | ✅ |

### Тренеры (`/api/trainers/`)

| Метод | URL | Описание | Права |
|---|---|---|---|
| GET | `/api/trainers/` | Список тренеров | Авторизованный |
| POST | `/api/trainers/` | Создать тренера | Администратор |
| GET | `/api/trainers/{id}/` | Профиль тренера | Авторизованный |
| PUT/PATCH | `/api/trainers/{id}/` | Обновить тренера | Администратор |
| DELETE | `/api/trainers/{id}/` | Удалить тренера | Администратор |
| GET | `/api/trainers/{id}/schedule/` | Расписание тренера | Авторизованный |

### Участники (`/api/members/`)

| Метод | URL | Описание | Права |
|---|---|---|---|
| GET | `/api/members/` | Мой профиль (или все — для admin) | Авторизованный |
| POST | `/api/members/` | Создать профиль | Авторизованный |
| GET | `/api/members/{id}/` | Профиль участника | Владелец / Admin |
| PUT/PATCH | `/api/members/{id}/` | Обновить профиль | Владелец / Admin |
| DELETE | `/api/members/{id}/` | Удалить профиль | Владелец / Admin |
| GET | `/api/members/{id}/bookings/` | Мои записи на занятия | Владелец / Admin |

### Абонементы (`/api/memberships/`)

| Метод | URL | Описание | Права |
|---|---|---|---|
| GET | `/api/memberships/` | Мои абонементы | Авторизованный |
| POST | `/api/memberships/` | Оформить абонемент | Авторизованный |
| GET | `/api/memberships/{id}/` | Детали абонемента | Авторизованный |
| PUT/PATCH | `/api/memberships/{id}/` | Обновить абонемент | Авторизованный |
| DELETE | `/api/memberships/{id}/` | Удалить абонемент | Администратор |

### Занятия (`/api/classes/`)

| Метод | URL | Описание | Права |
|---|---|---|---|
| GET | `/api/classes/` | Список занятий | Авторизованный |
| POST | `/api/classes/` | Создать занятие | Администратор |
| GET | `/api/classes/{id}/` | Детали занятия | Авторизованный |
| PUT/PATCH | `/api/classes/{id}/` | Обновить занятие | Администратор |
| DELETE | `/api/classes/{id}/` | Удалить занятие | Администратор |
| GET | `/api/classes/{id}/participants/` | Список участников | Администратор |

### Записи на занятия (`/api/bookings/`)

| Метод | URL | Описание | Права |
|---|---|---|---|
| GET | `/api/bookings/` | Мои записи | Авторизованный |
| POST | `/api/bookings/` | Записаться на занятие | Авторизованный |
| GET | `/api/bookings/{id}/` | Детали записи | Авторизованный |
| PUT/PATCH | `/api/bookings/{id}/` | Обновить запись (отзыв/оценка) | Авторизованный |
| DELETE | `/api/bookings/{id}/` | Удалить запись | Авторизованный |
| POST | `/api/bookings/{id}/cancel/` | Отменить запись | Авторизованный |

---

## 🔍 Фильтрация, поиск и сортировка

Все списковые эндпоинты поддерживают **пагинацию** (по 10 записей, `?page=2&page_size=5`).

### Занятия

```
GET /api/classes/?difficulty=3
GET /api/classes/?trainer=1
GET /api/classes/?is_cancelled=false
GET /api/classes/?scheduled_after=2024-01-01T00:00:00
GET /api/classes/?upcoming=true
GET /api/classes/?has_spots=true
GET /api/classes/?price_max=500
GET /api/classes/?search=йога
GET /api/classes/?ordering=scheduled_at
GET /api/classes/?ordering=-price
```

### Тренеры

```
GET /api/trainers/?specialization=yoga
GET /api/trainers/?is_active=true
GET /api/trainers/?search=Смирнов
GET /api/trainers/?ordering=-experience_years
```

### Записи

```
GET /api/bookings/?status=confirmed
GET /api/bookings/?training_class=3
```
---

## 🛠️ Полезные команды Docker

```bash
# Запустить всё
docker compose up --build

# Запустить в фоне
docker compose up -d

# Остановить (данные сохранятся)
docker compose down

# Перезапустить
docker compose restart

# Логи
docker compose logs -f web

# Войти в контейнер
docker compose exec web bash

# Применить миграции
docker compose exec web python manage.py migrate

# Создать суперпользователя
docker compose exec web python manage.py createsuperuser

# Создать миграции после изменения моделей
docker compose exec web python manage.py makemigrations
```

---

## 🏗️ Структура проекта

```
myproject/
├── config/                    # Настройки Django
│   ├── settings.py
│   ├── urls.py                # Главный роутер + Swagger
│   └── wsgi.py
├── fitness_club/              # Основное приложение
│   ├── models.py              # 5 моделей БД
│   ├── serializers.py         # DRF сериализаторы
│   ├── views.py               # ViewSets (CRUD)
│   ├── urls.py                # Роутер приложения
│   ├── permissions.py         # Кастомные права доступа
│   ├── filters.py             # Кастомные фильтры
│   ├── admin.py               # Django Admin
│   └── management/
│       └── commands/
│           └── seed_data.py   # Команда заполнения БД
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── manage.py
├── .env.example
└── README.md
```

## 📦 Стек технологий

| Технология | Версия | Назначение |
|---|---|---|
| Python | 3.11 | Язык программирования |
| Django | 4.2 | Веб-фреймворк |
| Django REST Framework | 3.15 | REST API |
| djangorestframework-simplejwt | 5.3 | JWT аутентификация |
| drf-yasg | 1.21 | Swagger / OpenAPI документация |
| django-filter | 23.5 | Фильтрация запросов |
| django-cors-headers | 4.3 | CORS для фронтенда |
| PostgreSQL | 15 | База данных |
| Docker + Compose | — | Контейнеризация |
