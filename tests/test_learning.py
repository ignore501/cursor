import pytest
from datetime import datetime, timedelta
from src.learning.learning import Learning
from src.database.database import Database

@pytest.fixture
def db():
    return Database(":memory:")

@pytest.fixture
def learning(db):
    return Learning(db)

def test_get_current_topic(learning, db):
    # Тест на получение текущей темы
    today = datetime.now().strftime("%Y-%m-%d")
    topic = learning.get_current_topic()
    assert topic is not None
    assert topic["name"] == "Введение в Data Science"

def test_get_next_topic(learning, db):
    # Тест на получение следующей темы
    next_topic = learning.get_next_topic()
    assert next_topic is not None
    assert next_topic["name"] == "Предобработка данных"

def test_get_topic_tasks(learning, db):
    # Тест на получение задач для темы
    topic_name = "Введение в Data Science"
    tasks = learning.get_topic_tasks(topic_name)
    assert len(tasks) > 0
    assert "Изучение основных концепций Data Science" in tasks

def test_update_progress(learning, db):
    # Тест на обновление прогресса
    user_id = 1
    topic_name = "Введение в Data Science"
    completed_tasks = 2
    db.add_user(user_id, "test_user", "Test", "User")

    assert learning.update_progress(user_id, topic_name, completed_tasks) is True
    progress = learning.get_progress(user_id, topic_name)
    assert progress["completed_tasks"] == completed_tasks

def test_get_user_progress(learning, db):
    # Тест на получение прогресса пользователя
    user_id = 1
    db.add_user(user_id, "test_user", "Test", "User")
    
    # Добавляем прогресс по нескольким темам
    topics = ["Введение в Data Science", "Предобработка данных"]
    for topic in topics:
        learning.update_progress(user_id, topic, 2)

    progress = learning.get_user_progress(user_id)
    assert len(progress) == 2
    for topic_progress in progress:
        assert topic_progress["completed_tasks"] == 2

def test_get_topic_votes(learning, db):
    # Тест на получение голосов за темы
    user_ids = [1, 2, 3]
    topic_name = "Feature Engineering"
    
    # Добавляем пользователей и их голоса
    for user_id in user_ids:
        db.add_user(user_id, f"user{user_id}", "Test", "User")
        learning.add_topic_vote(user_id, topic_name)

    votes = learning.get_topic_votes()
    assert len(votes) > 0
    for vote in votes:
        if vote["name"] == topic_name:
            assert vote["votes"] == 3

def test_add_topic_vote(learning, db):
    # Тест на добавление голоса за тему
    user_id = 1
    topic_name = "Feature Engineering"
    db.add_user(user_id, "test_user", "Test", "User")

    assert learning.add_topic_vote(user_id, topic_name) is True
    votes = learning.get_topic_votes()
    for vote in votes:
        if vote["name"] == topic_name:
            assert vote["votes"] == 1

def test_get_metrics(learning, db):
    # Тест на получение метрик
    user_id = 1
    db.add_user(user_id, "test_user", "Test", "User")
    
    # Добавляем тестовые метрики
    metrics = {
        "accuracy": 0.95,
        "loss": 0.05,
        "f1": 0.94
    }
    for name, value in metrics.items():
        learning.add_metric(user_id, name, value)

    user_metrics = learning.get_metrics(user_id)
    assert len(user_metrics) == 3
    for metric in user_metrics:
        assert metric["metric_name"] in metrics
        assert metric["metric_value"] == metrics[metric["metric_name"]]

def test_add_metric(learning, db):
    # Тест на добавление метрики
    user_id = 1
    metric_name = "accuracy"
    metric_value = 0.95
    db.add_user(user_id, "test_user", "Test", "User")

    assert learning.add_metric(user_id, metric_name, metric_value) is True
    metrics = learning.get_metrics(user_id)
    assert len(metrics) == 1
    assert metrics[0]["metric_name"] == metric_name
    assert metrics[0]["metric_value"] == metric_value

def test_get_learning_plan(learning):
    # Тест на получение плана обучения
    plan = learning.get_learning_plan()
    assert len(plan["topics"]) > 0
    assert len(plan["schedule"]) > 0

def test_get_topic_by_date(learning):
    # Тест на получение темы по дате
    today = datetime.now().strftime("%Y-%m-%d")
    topic = learning.get_topic_by_date(today)
    assert topic is not None
    assert topic["name"] == "Введение в Data Science" 