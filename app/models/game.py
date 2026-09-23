from datetime import datetime

from app.extensions import db


class GameProgress(db.Model):
    """Tracks per-user progress across every mini game (Snakes & Ladders,
    Treasure Hunt, Real or Myth)."""

    __tablename__ = "game_progress"
    __table_args__ = (
        db.UniqueConstraint("user_id", "game_name", name="uix_user_game"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    game_name = db.Column(db.String(80), nullable=False)  # snakes_ladders | treasure_hunt | real_or_myth
    position = db.Column(db.Integer, default=1)
    points = db.Column(db.Integer, default=0)
    level_reached = db.Column(db.Integer, default=1)
    completed = db.Column(db.Boolean, default=False)
    extra_state = db.Column(db.JSON, default=dict)  # game-specific state (found clues, streak, etc.)

    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self) -> dict:
        return {
            "game_name": self.game_name,
            "position": self.position,
            "points": self.points,
            "level_reached": self.level_reached,
            "completed": self.completed,
            "extra_state": self.extra_state or {},
        }