import pytest
from src.utils.utils import (
    format_date,
    format_time,
    format_number,
    format_percentage,
    is_valid_email,
    is_valid_url,
    parse_date,
    sanitize_text,
    truncate_message,
    format_message,
    parse_command_args,
    validate_email,
    validate_phone,
    sanitize_filename,
    ensure_dir,
    generate_random_string,
    format_learning_result
)
import logging
from datetime import datetime

def test_format_date():
    """Тест форматирования даты."""
    # Тест с объектом datetime
    date = datetime(2024, 3, 15)
    assert format_date(date) == "15.03.2024"
    
    # Тест со строкой даты
    assert format_date("2024-03-15") == "15.03.2024"
    assert format_date("15.03.2024") == "15.03.2024"
    
    # Тест с некорректной датой
    with pytest.raises(ValueError):
        format_date("invalid_date")

def test_format_time():
    assert format_time("09:00:00") == "09:00"

def test_format_number():
    assert format_number(1234567) == "1 234 567"

def test_format_percentage():
    assert format_percentage(0.1234) == "12.34%"

def test_is_valid_email():
    assert is_valid_email("test@example.com")
    assert not is_valid_email("test@com")

def test_parse_date():
    """Тест парсинга даты."""
    # Тест с форматом DD.MM.YYYY
    assert parse_date("15.03.2024") == datetime(2024, 3, 15)
    
    # Тест с форматом YYYY-MM-DD
    assert parse_date("2024-03-15") == datetime(2024, 3, 15)
    
    # Тест с некорректной датой
    with pytest.raises(ValueError):
        parse_date("invalid_date")

def test_is_valid_url():
    """Тест валидации URL."""
    # Корректные URL
    assert is_valid_url("https://example.com")
    assert is_valid_url("http://example.com")
    assert is_valid_url("https://example.com/path")
    assert is_valid_url("https://example.com/path?param=value")
    
    # Некорректные URL
    assert not is_valid_url("not_a_url")
    assert not is_valid_url("ftp://example.com")
    assert not is_valid_url("https://")
    assert not is_valid_url("http://")

def test_sanitize_text():
    """Тест очистки текста."""
    # Тест с HTML-тегами
    assert sanitize_text("<p>Test</p>") == "Test"
    assert sanitize_text("<script>alert('test')</script>") == "alert('test')"
    
    # Тест с специальными символами
    assert sanitize_text("Test\n\r\t") == "Test"
    assert sanitize_text("  Test  ") == "Test"
    
    # Тест с эмодзи
    assert sanitize_text("Test 😊") == "Test 😊"
    
    # Тест с пустой строкой
    assert sanitize_text("") == ""
    assert sanitize_text(None) == ""

def test_truncate_text():
    """Тест обрезки текста."""
    # Тест с длинным текстом
    long_text = "This is a very long text that needs to be truncated"
    assert truncate_message(long_text, 20) == "This is a very long..."
    
    # Тест с коротким текстом
    short_text = "Short text"
    assert truncate_message(short_text, 20) == short_text
    
    # Тест с пустой строкой
    assert truncate_message("", 20) == ""
    assert truncate_message(None, 20) == ""
    
    # Тест с отрицательной длиной
    assert truncate_message(long_text, -1) == "..."

def test_generate_random_string():
    """Тест генерации случайной строки."""
    # Тест с разной длиной
    assert len(generate_random_string(10)) == 10
    assert len(generate_random_string(20)) == 20
    
    # Тест с разными наборами символов
    assert generate_random_string(10, "abc") == "".join(["a", "b", "c"][i % 3] for i in range(10))
    
    # Тест с пустым набором символов
    with pytest.raises(ValueError):
        generate_random_string(10, "")
    
    # Тест с отрицательной длиной
    with pytest.raises(ValueError):
        generate_random_string(-1)

def test_date_edge_cases():
    """Тест граничных случаев для дат."""
    # Тест с високосным годом
    assert format_date("2024-02-29") == "29.02.2024"
    
    # Тест с началом года
    assert format_date("2024-01-01") == "01.01.2024"
    
    # Тест с концом года
    assert format_date("2024-12-31") == "31.12.2024"
    
    # Тест с некорректной датой
    with pytest.raises(ValueError):
        format_date("2024-02-30")  # 30 февраля не существует

def test_url_edge_cases():
    """Тест граничных случаев для URL."""
    # Тест с поддоменами
    assert is_valid_url("https://sub.example.com")
    assert is_valid_url("https://sub.sub.example.com")
    
    # Тест с портом
    assert is_valid_url("https://example.com:8080")
    
    # Тест с параметрами
    assert is_valid_url("https://example.com?param1=value1&param2=value2")
    
    # Тест с якорем
    assert is_valid_url("https://example.com#section")
    
    # Тест с кириллицей
    assert is_valid_url("https://пример.рф")
    
    # Тест с пробелами
    assert not is_valid_url("https://example.com/path with spaces")

def test_text_edge_cases():
    """Тест граничных случаев для текста."""
    # Тест с HTML-сущностями
    assert sanitize_text("&lt;p&gt;Test&lt;/p&gt;") == "<p>Test</p>"
    
    # Тест с Unicode-символами
    assert sanitize_text("Test\u2028\u2029") == "Test"
    
    # Тест с длинным текстом
    long_text = "x" * 1000
    assert len(truncate_message(long_text, 100)) == 100
    
    # Тест с переносами строк
    assert sanitize_text("Line1\nLine2\r\nLine3") == "Line1Line2Line3"
    
    # Тест с табуляцией
    assert sanitize_text("Tab\tTab") == "TabTab"

def test_truncate_message():
    """Тест обрезки текста."""
    # Тест с длинным текстом
    long_text = "This is a very long text that needs to be truncated"
    assert truncate_message(long_text, 20) == "This is a very long..."
    
    # Тест с коротким текстом
    short_text = "Short text"
    assert truncate_message(short_text, 20) == short_text
    
    # Тест с пустой строкой
    assert truncate_message("", 20) == ""
    assert truncate_message(None, 20) == ""
    
    # Тест с отрицательной длиной
    assert truncate_message(long_text, -1) == "..."

def test_format_learning_result():
    """Тест форматирования результата обучения."""
    # Тест с положительным результатом
    assert format_learning_result(0.85) == "85%"
    assert format_learning_result(1.0) == "100%"
    
    # Тест с нулевым результатом
    assert format_learning_result(0.0) == "0%"
    
    # Тест с отрицательным результатом
    assert format_learning_result(-0.5) == "-50%"
    
    # Тест с некорректным значением
    with pytest.raises(ValueError):
        format_learning_result("invalid") 