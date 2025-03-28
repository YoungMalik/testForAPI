import pytest
from app.main import generate_short_code

def test_generate_short_code_length():
    short_code = generate_short_code(length=6)
    assert len(short_code) == 6

def test_generate_short_code_characters():
    short_code = generate_short_code()
    assert all(c.isalnum() for c in short_code)  # Только буквы и цифры

def test_generate_short_code_uniqueness():
    codes = {generate_short_code() for _ in range(100)}
    assert len(codes) == 100  # Проверяем уникальность