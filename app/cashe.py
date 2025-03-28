import redis
from typing import Optional

# Настройка клиента Redis
redis_client = redis.Redis(
    host="redis",  # Имя сервиса в Docker
    port=6379,
    db=0,
    decode_responses=True
)

def get_short_code(original_url: str) -> Optional[str]:
    """
    Получает short_code из кэша по оригинальному URL.
    Возвращает None, если кэш пуст.
    """
    try:
        return redis_client.get(f"url:{original_url}")
    except redis.RedisError:
        return None

def set_short_code(original_url: str, short_code: str) -> None:
    """
    Сохраняет short_code в кэш по оригинальному URL.
    """
    try:
        redis_client.setex(f"url:{original_url}", 3600, short_code)  # Кэш на 1 час
    except redis.RedisError:
        pass

def delete_short_code(original_url: str) -> None:
    """
    Удаляет short_code из кэша по оригинальному URL.
    """
    try:
        redis_client.delete(f"url:{original_url}")
    except redis.RedisError:
        pass