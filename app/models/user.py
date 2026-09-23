from datetime import datetime
from flask_login import UserMixin

from app.extensions import db, bcrypt


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    points = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    streak = db.Column(db.Integer, default=0)
    is_admin = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    quiz_attempts = db.relationship(
        "QuizAttempt", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    game_progress = db.relationship(
        "GameProgress", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    scenario_progress = db.relationship(
        "ScenarioProgress", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, raw_password: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(raw_password).decode("utf-8")

    def check_password(self, raw_password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, raw_password)

    def add_points(self, amount: int) -> None:
        self.points = (self.points or 0) + amount
        self.level = 1 + self.points // 100

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "points": self.points,
            "level": self.level,
            "streak": self.streak,
        }

    def __repr__(self):
        return f"<User {self.email}>"
