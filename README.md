# Fitness Club REST API

RESTful API для фитнес-клуба, разработанное с использованием Django Rest Framework.

## Возможности

- ✅ Полная поддержка CRUD операций для всех моделей
- ✅ JWT аутентификация (обязательная для всех эндпоинтов)
- ✅ Пагинация для всех списковых представлений
- ✅ Swagger документация с кнопкой "Authorize" для JWT токенов
- ✅ Связанные модели данных (Member, Membership, Trainer)
- ✅ Фильтрация и поиск
- ✅ Готово к интеграции с React/Vue.js или мобильными приложениями

## Структура базы данных

API использует 3 связанные таблицы:

1. **Trainer** (Тренер) - информация о тренерах
   - Связан с User (OneToOne)
   - Специализация, опыт работы, контакты

2. **Member** (Участник) - информация об участниках клуба
   - Связан с User (OneToOne)
   - Контактная информация, дата рождения

3. **Membership** (Абонемент) - информация об абонементах
   - Связан с Member (ForeignKey)
   - Связан с Trainer (ForeignKey, опционально)
   - Тип абонемента, даты, статус, цена

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Примените миграции:
```bash
python manage.py makemigrations
python manage.py migrate
```

3. Создайте суперпользователя (опционально):
```bash
python manage.py createsuperuser
```

4. Запустите сервер разработки:
```bash
python manage.py runserver
```

## Использование API

### Базовый URL
```
http://localhost:8000/api/
```

### Swagger документация
```
http://localhost:8000/api/docs/
```

### Redoc документация
```
http://localhost:8000/api/redoc/
```

## Аутентификация

### Получение JWT токена

Отправьте POST запрос на `/api/auth/token/` с учетными данными:

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

Ответ:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Использование токена

Добаpython manage.py createsuperuserвьте заголовок в каждый запрос:
```
Authorization: Bearer <access_token>
```

### Обновление токена

Отправьте POST запрос на `/api/auth/token/refresh/`:
```json
{
  "refresh": "your_refresh_token"
}
```

## Эндпоинты API

### Тренеры (Trainers)
- `GET /api/trainers/` - Список тренеров (с пагинацией)
- `GET /api/trainers/{id}/` - Детали тренера
- `POST /api/trainers/` - Создать тренера
- `PUT /api/trainers/{id}/` - Обновить тренера
- `PATCH /api/trainers/{id}/` - Частично обновить тренера
- `DELETE /api/trainers/{id}/` - Удалить тренера

**Фильтры:**
- `?specialization=название` - Фильтр по специализации

### Участники (Members)
- `GET /api/members/` - Список участников (с пагинацией)
- `GET /api/members/{id}/` - Детали участника
- `POST /api/members/` - Создать участника
- `PUT /api/members/{id}/` - Обновить участника
- `PATCH /api/members/{id}/` - Частично обновить участника
- `DELETE /api/members/{id}/` - Удалить участника
- `GET /api/members/{id}/memberships/` - Абонементы участника

### Абонементы (Memberships)
- `GET /api/memberships/` - Список абонементов (с пагинацией)
- `GET /api/memberships/{id}/` - Детали абонемента
- `POST /api/memberships/` - Создать абонемент
- `PUT /api/memberships/{id}/` - Обновить абонемент
- `PATCH /api/memberships/{id}/` - Частично обновить абонемент
- `DELETE /api/memberships/{id}/` - Удалить абонемент
- `GET /api/memberships/active/` - Список активных абонементов

**Фильтры:**
- `?member_id=id` - Фильтр по участнику
- `?trainer_id=id` - Фильтр по тренеру
- `?status=active|expired|suspended` - Фильтр по статусу
- `?membership_type=basic|premium|vip` - Фильтр по типу

## Использование Swagger UI

1. Откройте `http://localhost:8000/api/docs/` в браузере
2. Нажмите кнопку **"Authorize"** в правом верхнем углу
3. Введите JWT токен в формате: `Bearer <your_access_token>`
   - Или просто: `<your_access_token>` (Bearer будет добавлен автоматически)
4. Нажмите "Authorize"
5. Теперь вы можете отправлять авторизованные запросы прямо из браузера

## Примеры запросов

### Создание пользователя и участника

1. Создайте пользователя через Django admin или используйте существующего
2. Создайте участника:

```bash
POST /api/members/
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": 1,
  "phone": "+7 999 123 45 67",
  "date_of_birth": "1990-01-15",
  "address": "Москва, ул. Примерная, д. 1"
}
```

### Создание абонемента

```bash
POST /api/memberships/
Authorization: Bearer <token>
Content-Type: application/json

{
  "member_id": 1,
  "membership_type": "premium",
  "start_date": "2026-01-01",
  "end_date": "2026-12-31",
  "price": "50000.00",
  "status": "active",
  "trainer_id": 1
}
```

## Пагинация

Все списковые эндпоинты поддерживают пагинацию:
- Размер страницы: 10 элементов (по умолчанию)
- Параметры: `?page=1`, `?page=2`, и т.д.

Ответ включает:
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/trainers/?page=2",
  "previous": null,
  "results": [...]
}
```

## Технологии

- Django 5.0.1
- Django REST Framework 3.14.0
- djangorestframework-simplejwt 5.3.1 (JWT аутентификация)
- drf-spectacular 0.27.0 (Swagger/OpenAPI документация)
- django-cors-headers 4.3.1 (CORS поддержка)

## Разработка

Для разработки рекомендуется использовать виртуальное окружение:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

## Лицензия

Этот проект создан в образовательных целях.
