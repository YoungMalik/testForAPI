import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# Тестовая база данных SQLite
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Переопределяем зависимость get_db
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def test_client():
    Base.metadata.create_all(bind=engine)  # Создаем таблицы для тестов
    client = TestClient(app)
    yield client
    Base.metadata.drop_all(bind=engine)  # Очищаем после тестов

@pytest.fixture
def mock_redis(mocker):
    # Мокируем redis_client в модуле cashe
    mock = mocker.patch("app.cashe.redis_client", autospec=True)
    mock.get.return_value = None  # По умолчанию кэш пуст
    mock.setex.return_value = None  # Мокаем setex
    mock.delete.return_value = None  # Мокаем delete
    yield mock