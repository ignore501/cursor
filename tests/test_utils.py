import pytest
from src.utils.utils import (
    format_date,
    format_time,
    format_number,
    format_percentage,
    is_valid_email,
    is_valid_url,
)

def test_format_date():
    assert format_date("2024-03-20") == "20.03.2024"

def test_format_time():
    assert format_time("09:00:00") == "09:00"

def test_format_number():
    assert format_number(1234567) == "1 234 567"

def test_format_percentage():
    assert format_percentage(0.1234) == "12.34%"

def test_is_valid_email():
    assert is_valid_email("test@example.com")
    assert not is_valid_email("test@com")

def test_is_valid_url():
    assert is_valid_url("https://example.com")
    assert not is_valid_url("htp:/bad-url") 