from datetime import datetime

from app.extensions import db


class ScenarioProgress(db.Model):
    """Tracks which node of a branching scenario each user is on."""

    __tablename__ = "scenario_progress"
    __table_args__ = (
        db.UniqueConstraint("user_id", "scenario_id", name="uix_user_scenario"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    scenario_id = db.Column(db.String(120), nullable=False)
    current_node_id = db.Column(db.String(120), nullable=False)
    points_earned = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)

    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self) -> dict:
        return {
            "scenario_id": self.scenario_id,
            "current_node_id": self.current_node_id,
            "points_earned": self.points_earned,
            "completed": self.completed,
        }