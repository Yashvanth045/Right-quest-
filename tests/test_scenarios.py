import pytest

from app import create_app
from app.config import Config
from app.services.scenario_engine import (
    ScenarioEngine,
    ScenarioNotFoundError,
    ScenarioChoiceError,
)


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SCENARIO_DIRECTORY = "scenarios"


@pytest.fixture
def app():
    return create_app(TestConfig)


def test_list_scenarios_returns_all_files(app):
    with app.app_context():
        engine = ScenarioEngine()
        scenarios = engine.list_scenarios()
        ids = [s["id"] for s in scenarios]
        assert "consumer_refund" in ids
        assert "citizen_participation" in ids
        assert "fundamental_rights" in ids


def test_get_start_node(app):
    with app.app_context():
        engine = ScenarioEngine()
        node = engine.get_start_node("consumer_refund")
        assert node["node_id"] == "begin"
        assert len(node["node"]["choices"]) > 0


def test_choose_valid_path_awards_points(app):
    with app.app_context():
        engine = ScenarioEngine()
        result = engine.choose("consumer_refund", "begin", "evidence")
        assert result["points"] == 10
        assert result["node_id"] == "contact_seller"


def test_unknown_scenario_raises(app):
    with app.app_context():
        engine = ScenarioEngine()
        with pytest.raises(ScenarioNotFoundError):
            engine.load("does_not_exist")


def test_unknown_choice_raises(app):
    with app.app_context():
        engine = ScenarioEngine()
        with pytest.raises(ScenarioChoiceError):
            engine.choose("consumer_refund", "begin", "not_a_real_choice")
