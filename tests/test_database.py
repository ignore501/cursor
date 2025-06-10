import pytest
from datetime import datetime, timedelta
from src.database.database import Database

@pytest.fixture
def db():
    return Database(":memory:")

def test_add_user(db):
    # Тест на добавление пользователя
    user_id = 1
    username = "test_user"
    first_name = "Test"
    last_name = "User"

    assert db.add_user(user_id, username, first_name, last_name) is True
    user = db.get_user(user_id)
    assert user["user_id"] == user_id
    assert user["username"] == username
    assert user["first_name"] == first_name
    assert user["last_name"] == last_name
    assert user["is_banned"] is False
    assert user["warnings"] == 0

def test_update_user(db):
    # Тест на обновление пользователя
    user_id = 1
    db.add_user(user_id, "old_username", "Old", "User")
    
    new_username = "new_username"
    assert db.update_user(user_id, username=new_username) is True
    user = db.get_user(user_id)
    assert user["username"] == new_username

def test_add_message(db):
    # Тест на добавление сообщения
    user_id = 1
    chat_id = 1
    text = "Test message"

    assert db.add_message(user_id, chat_id, text) is True
    message = db.get_message(1)  # Первое сообщение имеет id=1
    assert message["user_id"] == user_id
    assert message["chat_id"] == chat_id
    assert message["text"] == text
    assert message["is_deleted"] is False

def test_delete_message(db):
    # Тест на удаление сообщения
    user_id = 1
    chat_id = 1
    text = "Test message"
    db.add_message(user_id, chat_id, text)

    assert db.delete_message(1) is True
    message = db.get_message(1)
    assert message["is_deleted"] is True

def test_add_topic(db):
    # Тест на добавление темы
    name = "Test Topic"
    description = "Test Description"

    assert db.add_topic(name, description) is True
    topic = db.get_topic(1)  # Первая тема имеет id=1
    assert topic["name"] == name
    assert topic["description"] == description
    assert topic["is_active"] is True

def test_add_topic_vote(db):
    # Тест на добавление голоса за тему
    user_id = 1
    topic_id = 1
    db.add_user(user_id, "test_user", "Test", "User")
    db.add_topic("Test Topic", "Test Description")

    assert db.add_topic_vote(user_id, topic_id) is True
    vote = db.get_topic_vote(1)  # Первый голос имеет id=1
    assert vote["user_id"] == user_id
    assert vote["topic_id"] == topic_id

def test_add_progress(db):
    # Тест на добавление прогресса
    user_id = 1
    topic_id = 1
    total_tasks = 5
    db.add_user(user_id, "test_user", "Test", "User")
    db.add_topic("Test Topic", "Test Description")

    assert db.add_progress(user_id, topic_id, total_tasks) is True
    progress = db.get_progress(1)  # Первый прогресс имеет id=1
    assert progress["user_id"] == user_id
    assert progress["topic_id"] == topic_id
    assert progress["completed_tasks"] == 0
    assert progress["total_tasks"] == total_tasks

def test_update_progress(db):
    # Тест на обновление прогресса
    user_id = 1
    topic_id = 1
    total_tasks = 5
    db.add_user(user_id, "test_user", "Test", "User")
    db.add_topic("Test Topic", "Test Description")
    db.add_progress(user_id, topic_id, total_tasks)

    completed_tasks = 3
    assert db.update_progress(1, completed_tasks) is True
    progress = db.get_progress(1)
    assert progress["completed_tasks"] == completed_tasks

def test_add_feedback(db):
    # Тест на добавление отзыва
    user_id = 1
    rating = 5
    comment = "Great bot!"
    db.add_user(user_id, "test_user", "Test", "User")

    assert db.add_feedback(user_id, rating, comment) is True
    feedback = db.get_feedback(1)  # Первый отзыв имеет id=1
    assert feedback["user_id"] == user_id
    assert feedback["rating"] == rating
    assert feedback["comment"] == comment

def test_add_metric(db):
    # Тест на добавление метрики
    user_id = 1
    metric_name = "accuracy"
    metric_value = 0.95
    db.add_user(user_id, "test_user", "Test", "User")

    assert db.add_metric(user_id, metric_name, metric_value) is True
    metric = db.get_metric(1)  # Первая метрика имеет id=1
    assert metric["user_id"] == user_id
    assert metric["metric_name"] == metric_name
    assert metric["metric_value"] == metric_value

def test_get_user_messages(db):
    # Тест на получение сообщений пользователя
    user_id = 1
    chat_id = 1
    db.add_user(user_id, "test_user", "Test", "User")
    
    messages = ["Message 1", "Message 2", "Message 3"]
    for text in messages:
        db.add_message(user_id, chat_id, text)

    user_messages = db.get_user_messages(user_id)
    assert len(user_messages) == 3
    for i, message in enumerate(user_messages):
        assert message["text"] == messages[i]

def test_get_topic_votes(db):
    # Тест на получение голосов за тему
    user_ids = [1, 2, 3]
    topic_id = 1
    db.add_topic("Test Topic", "Test Description")
    
    for user_id in user_ids:
        db.add_user(user_id, f"user{user_id}", "Test", "User")
        db.add_topic_vote(user_id, topic_id)

    votes = db.get_topic_votes(topic_id)
    assert len(votes) == 3
    for vote in votes:
        assert vote["topic_id"] == topic_id
        assert vote["user_id"] in user_ids 