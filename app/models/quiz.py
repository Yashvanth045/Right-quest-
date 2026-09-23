from datetime import datetime

from app.extensions import db


class QuizQuestion(db.Model):
    __tablename__ = "quiz_questions"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False, index=True)
    country = db.Column(db.String(100), default="General")

    question = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON, nullable=False)
    correct_answer = db.Column(db.String(255), nullable=False)
    explanation = db.Column(db.Text, nullable=False)

    difficulty = db.Column(db.String(30), default="medium")
    source = db.Column(db.String(255))
    reviewed = db.Column(db.Boolean, default=False, index=True)

    week_of = db.Column(db.Date, nullable=True)  # used for weekly scenario tests

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self, include_answer: bool = False) -> dict:
        data = {
            "id": self.id,
            "category": self.category,
            "question": self.question,
            "options": self.options,
            "difficulty": self.difficulty,
        }
        if include_answer:
            data["correct_answer"] = self.correct_answer
            data["explanation"] = self.explanation
        return data


class QuizAttempt(db.Model):
    __tablename__ = "quiz_attempts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    category = db.Column(db.String(100))
    score = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=0)
    points_earned = db.Column(db.Integer, default=0)
    is_weekly_test = db.Column(db.Boolean, default=False)

    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category": self.category,
            "score": self.score,
            "total_questions": self.total_questions,
            "points_earned": self.points_earned,
            "is_weekly_test": self.is_weekly_test,
            "completed_at": self.completed_at.isoformat(),
        }