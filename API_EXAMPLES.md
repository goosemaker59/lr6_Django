# Примеры использования API

## Быстрый старт

### 1. Создание пользователя и получение токена

Сначала создайте пользователя через Django admin или используйте команду:

```bash
python manage.py createsuperuser
```

### 2. Получение JWT токена

```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'
```

Ответ:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 3. Использование токена в запросах

```bash
curl -X GET http://localhost:8000/api/trainers/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Примеры CRUD операций

### Тренеры

#### Создание тренера
```bash
POST /api/trainers/
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": 1,
  "specialization": "Силовые тренировки",
  "experience_years": 5,
  "phone": "+7 999 123 45 67",
  "bio": "Опытный тренер по силовым тренировкам"
}
```

#### Получение списка тренеров
```bash
GET /api/trainers/
Authorization: Bearer <token>
```

#### Получение тренера по ID
```bash
GET /api/trainers/1/
Authorization: Bearer <token>
```

#### Обновление тренера
```bash
PATCH /api/trainers/1/
Authorization: Bearer <token>
Content-Type: application/json

{
  "experience_years": 6
}
```

#### Удаление тренера
```bash
DELETE /api/trainers/1/
Authorization: Bearer <token>
```

### Участники

#### Создание участника
```bash
POST /api/members/
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": 2,
  "phone": "+7 999 765 43 21",
  "date_of_birth": "1990-05-20",
  "address": "Москва, ул. Тестовая, д. 10",
  "emergency_contact": "+7 999 111 22 33"
}
```

#### Получение абонементов участника
```bash
GET /api/members/1/memberships/
Authorization: Bearer <token>
```

### Абонементы

#### Создание абонемента
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

#### Получение активных абонементов
```bash
GET /api/memberships/active/
Authorization: Bearer <token>
```

#### Фильтрация абонементов
```bash
# По участнику
GET /api/memberships/?member_id=1
Authorization: Bearer <token>

# По статусу
GET /api/memberships/?status=active
Authorization: Bearer <token>

# По типу
GET /api/memberships/?membership_type=premium
Authorization: Bearer <token>

# Комбинированные фильтры
GET /api/memberships/?member_id=1&status=active
Authorization: Bearer <token>
```

## Использование в JavaScript (Fetch API)

```javascript
// Получение токена
const response = await fetch('http://localhost:8000/api/auth/token/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'your_username',
    password: 'your_password'
  })
});

const { access, refresh } = await response.json();

// Использование токена
const trainersResponse = await fetch('http://localhost:8000/api/trainers/', {
  headers: {
    'Authorization': `Bearer ${access}`,
    'Content-Type': 'application/json',
  }
});

const trainers = await trainersResponse.json();
console.log(trainers);
```

## Использование в Python (requests)

```python
import requests

# Получение токена
response = requests.post(
    'http://localhost:8000/api/auth/token/',
    json={
        'username': 'your_username',
        'password': 'your_password'
    }
)

data = response.json()
access_token = data['access']

# Использование токена
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

# Получение списка тренеров
trainers_response = requests.get(
    'http://localhost:8000/api/trainers/',
    headers=headers
)

trainers = trainers_response.json()
print(trainers)
```

## Пагинация

Все списковые эндпоинты поддерживают пагинацию:

```bash
# Первая страница (по умолчанию)
GET /api/trainers/
Authorization: Bearer <token>

# Вторая страница
GET /api/trainers/?page=2
Authorization: Bearer <token>
```

Ответ включает информацию о пагинации:
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/trainers/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": {...},
      "specialization": "...",
      ...
    }
  ]
}
```
