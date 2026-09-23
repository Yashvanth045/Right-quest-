from flask import Flask
from app.config import Config
from app.extensions import db, login_manager, migrate


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.models import User, GameProgress, QuizQuestion, QuizAttempt, ScenarioProgress
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes.auth_routes import auth_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.quiz_routes import quiz_bp
    from app.routes.game_routes import game_bp
    from app.routes.scenario_routes import scenario_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(game_bp)
    app.register_blueprint(scenario_bp)

    # Bootstrap curated quiz questions for a fresh development database.
    with app.app_context():
        try:
            from app.services.quiz_seed_data import seed_if_empty
            seed_if_empty(db, QuizQuestion)
        except Exception:
            db.session.rollback()

    return app