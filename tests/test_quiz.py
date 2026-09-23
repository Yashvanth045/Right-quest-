import pytest

from app import create_app
from app.config import Config
from app.extensions import db
from app.models.user import User
from app.models.quiz import QuizQuestion
from app.services.scoring_service import calculate_quiz_score


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


@pytest.fixture
def app():
    application = create_app(TestConfig)
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


def test_calculate_quiz_score_all_correct(app):
    with app.app_context():
        q1 = QuizQuestion(
            category="Consumer Rights", question="Q1?", options=["A", "B"],
            correct_answer="A", explanation="because", reviewed=True,
        )
        q2 = QuizQuestion(
            category="Consumer Rights", question="Q2?", options=["C", "D"],
            correct_answer="D", explanation="because", reviewed=True,
        )
        db.session.add_all([q1, q2])
        db.session.commit()

        answers = {str(q1.id): "A", str(q2.id): "D"}
        result = calculate_quiz_score([q1, q2], answers)

        assert result["score"] == 2
        assert result["total"] == 2
        assert result["points"] == 20


def test_calculate_quiz_score_partial(app):
    with app.app_context():
        q1 = QuizQuestion(
            category="Citizen Rights", question="Q1?", options=["A", "B"],
            correct_answer="A", explanation="because", reviewed=True,
        )
        db.session.add(q1)
        db.session.commit()

        answers = {str(q1.id): "B"}
        result = calculate_quiz_score([q1], answers)

        assert result["score"] == 0
        assert result["points"] == 0
        assert result["results"][0]["correct"] is False


def test_user_add_points_and_level(app):
    with app.app_context():
        user = User(name="Test", email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        user.add_points(250)
        db.session.commit()

        assert user.points == 250
        assert user.level == 3  # 1 + 250 // 100
