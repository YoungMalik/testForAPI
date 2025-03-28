# Сокращатель URL на FastAPI

Это сервис сокращения URL, построенный на FastAPI, с аутентификацией пользователей, управлением ссылками и кэшированием через Redis. Проект включает юнит-тесты, анализ покрытия кода и нагрузочные тесты с помощью Locust.

## Структура проекта

FastAPI_project/

├── app/

│   ├── init.py

│   ├── auth.py         # Логика аутентификации (JWT, хеширование паролей)

│   ├── cashe.py        # Утилиты для кэширования в Redis

│   ├── database.py     # Конфигурация базы данных SQLAlchemy

│   ├── main.py         # Приложение FastAPI и эндпоинты

│   ├── models.py       # Модели ORM SQLAlchemy

│   └── schemas.py      # Схемы Pydantic для валидации

├── tests/

│   ├── init.py

│   ├── conftest.py     # Фикстуры Pytest (SQLite, замокированный Redis)

│   ├── test_auth.py    # Тесты аутентификации

│   ├── test_links.py   # Тесты управления ссылками

│   ├── test_utils.py   # Тесты утилитарных функций

│   └── locustfile.py   # Нагрузочные тесты с Locust

├── .env                # Переменные окружения

├── Dockerfile          # Конфигурация Docker для веб-сервиса

├── docker-compose.yml  # Docker Compose для веб, PostgreSQL и Redis

├── requirements.txt    # Зависимости Python

└── README.md           # Этот файл


text

Свернуть

Перенос

Копировать

## Возможности
- Регистрация и вход пользователей с аутентификацией JWT
- Создание коротких URL, перенаправление, обновление и удаление
- Статистика по ссылкам (количество кликов)
- Кэширование коротких кодов в Redis
- SQLite для юнит-тестов, PostgreSQL для продакшена
- Юнит-тесты с Pytest
- Анализ покрытия кода с Coverage.py
- Нагрузочные тесты с Locust

## Требования
- Python 3.9+
- Docker и Docker Compose
- Virtualenv (опционально, но рекомендуется)

## Установка

### 1. Клонируйте репозиторий
```bash
git clone <URL-репозитория>
cd FastAPI_project
2. Создайте и активируйте виртуальное окружение
bash

Свернуть

Перенос

Копировать
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
3. Установите зависимости
bash

Свернуть

Перенос

Копировать
pip install -r requirements.txt
4. Настройте переменные окружения
Создайте файл .env в корне проекта со следующим содержимым:

text

Свернуть

Перенос

Копировать
DATABASE_URL=postgresql://postgres:postgres@db:5432/url_shortener
SECRET_KEY=ваш-секретный-ключ
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEFAULT_LINK_EXPIRY_DAYS=30
Замените ваш-секретный-ключ на безопасный ключ (например, сгенерируйте с помощью openssl rand -hex 32).
Запуск приложения
Через Docker
bash

Свернуть

Перенос

Копировать
docker-compose up --build -d
API доступен по адресу http://localhost:8080.
Остановка сервиса:
bash

Свернуть

Перенос

Копировать
docker-compose down
Локально (без Docker)
Убедитесь, что PostgreSQL и Redis запущены локально, обновите DATABASE_URL в .env на postgresql://postgres:postgres@localhost:5432/url_shortener.
Запустите сервер FastAPI:
bash

Свернуть

Перенос

Копировать
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
Тестирование
Юнит-тесты с Pytest
Юнит-тесты проверяют аутентификацию, управление ссылками и утилитарные функции. Для тестов используется SQLite вместо PostgreSQL.

Запуск тестов
Активируйте виртуальное окружение:
bash

Свернуть

Перенос

Копировать
.venv\Scripts\activate
Установите PYTHONPATH:
bash

Свернуть

Перенос

Копировать
set PYTHONPATH=C:\Users\USER\Desktop\jupyter\pricladnoyPython\FastAPI_project\app
Выполните тесты:
bash

Свернуть

Перенос

Копировать
pytest tests/ -v
Результаты юнит-тестов
text

Свернуть

Перенос

Копировать
==================== test session starts ====================
collected 8 items
tests/test_auth.py .. [ 25%]
tests/test_links.py ..... [ 87%]
tests/test_utils.py .. [100%]
==================== 8 passed in 1.50s ====================
Все 8 тестов успешно пройдены.
Анализ покрытия кода
Покрытие кода измеряется с помощью Coverage.py.

Запуск анализа покрытия
bash

Свернуть

Перенос

Копировать
coverage run -m pytest tests/
coverage report
coverage html
После выполнения откройте htmlcov/index.html в браузере для детального отчета.
Результаты покрытия
text

Свернуть

Перенос

Копировать
Name                  Stmts   Miss  Cover
-----------------------------------------
app\__init__.py           0      0   100%
app\auth.py              44      5    89%
app\cashe.py             18      8    56%
app\database.py          15      4    73%
app\main.py             110     43    61%
app\models.py            18      0   100%
app\schemas.py           34      0   100%
tests\__init__.py         0      0   100%
tests\conftest.py        28      0   100%
tests\test_auth.py       16      0   100%
tests\test_links.py      34      0   100%
tests\test_utils.py      11      0   100%
-----------------------------------------
TOTAL                   328     60    82%
Общее покрытие: 82%.
Низкое покрытие в cashe.py (56%) и main.py (61%) связано с непротестированными случаями ошибок и эндпоинтами (PUT, DELETE, GET /stats).
Нагрузочные тесты с Locust
Locust используется для проверки производительности сервиса под нагрузкой.

Запуск нагрузочных тестов
Запустите Docker-контейнеры:
bash

Свернуть

Перенос

Копировать
docker-compose up --build -d
Запустите Locust:
bash

Свернуть

Перенос

Копировать
locust -f tests/locustfile.py
Откройте веб-интерфейс Locust в браузере: http://localhost:8089.
Настройте параметры:
Number of users: Количество пользователей (например, 100).
Spawn rate: Скорость появления пользователей (например, 10 в секунду).
Host: http://localhost:8080.
Нажмите "Start swarming" для начала теста.
Результаты запуска
text

Свернуть

Перенос

Копировать
[2025-03-28 13:30:51,245] DESKTOP-9032-1/INFO/locust.main: Starting web interface at http://0.0.0.0:8089
[2025-03-28 13:30:51,251] DESKTOP-9032-1/INFO/locust.main: Starting Locust 2.16.1
Locust успешно запущен, готов к нагрузочному тестированию.
Проверка сервиса
Убедитесь, что API работает:
bash

Свернуть

Перенос

Копировать
curl http://localhost:8080
Просмотрите логи, если есть проблемы:
bash

Свернуть

Перенос

Копировать
docker-compose logs web
Рекомендации
Очистка базы между тестами:
Чтобы избежать 400 Bad Request при повторной регистрации, измените scope="module" на scope="function" в tests/conftest.py:
python

Свернуть

Перенос

Копировать
@pytest.fixture(scope="function")
def test_client():
    Base.metadata.create_all(bind=engine)
    client = TestClient(app)
    yield client
    Base.metadata.drop_all(bind=engine)
Перезапустите тесты: pytest tests/ -v.

Итог

Юнит-тесты: 100% пройдены (8/8).
Покрытие кода: 82%.
Нагрузочные тесты: Locust запущен, готов к тестированию производительности.
