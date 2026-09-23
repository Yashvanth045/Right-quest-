"""Helper functions that sit between quiz routes and the database, so
routes stay thin and testable logic lives here."""

from datetime import date
from typing import List, Optional

from app.extensions import db
from app.models.quiz import QuizQuestion, QuizAttempt


def get_reviewed_questions(category: Optional[str] = None, limit: int = 10, exclude_ids: Optional[List[int]] = None) -> List[QuizQuestion]:
    query = QuizQuestion.query.filter_by(reviewed=True)

    if category:
        query = query.filter_by(category=category)

    if exclude_ids:
        query = query.filter(~QuizQuestion.id.in_(exclude_ids))

    return query.order_by(db.func.rand()).limit(limit).all()


def get_existing_question_texts(category: str) -> List[str]:
    """All question text already stored for a category -- used to ground AI
    generation and avoid producing duplicate/near-duplicate questions."""
    rows = (
        QuizQuestion.query.filter_by(category=category)
        .with_entities(QuizQuestion.question)
        .all()
    )
    return [row[0] for row in rows]


def get_weekly_test_questions(limit: int = 10) -> List[QuizQuestion]:
    """The weekly scenario test pulls from questions generated/reviewed
    for the current week; falls back to any reviewed question so the
    feature always has content during development."""
    today = date.today()
    query = QuizQuestion.query.filter_by(reviewed=True, week_of=today)
    questions = query.order_by(db.func.rand()).limit(limit).all()

    if not questions:
        questions = get_reviewed_questions(limit=limit)

    return questions


def save_generated_questions(items: List[dict], category: str, country: str, mark_week: bool = False) -> int:
    saved = 0
    for item in items:
        question = QuizQuestion(
            category=category,
            country=country,
            question=item["question"],
            options=item["options"],
            correct_answer=item["correct_answer"],
            explanation=item["explanation"],
            difficulty=item.get("difficulty", "medium"),
            source="AI-generated - pending review",
            reviewed=False,
            week_of=date.today() if mark_week else None,
        )
        db.session.add(question)
        saved += 1

    db.session.commit()
    return saved


def record_attempt(user, category: str, score: int, total: int, points: int, is_weekly: bool = False) -> QuizAttempt:
    attempt = QuizAttempt(
        user_id=user.id,
        category=category,
        score=score,
        total_questions=total,
        points_earned=points,
        is_weekly_test=is_weekly,
    )
    db.session.add(attempt)
    user.add_points(points)
    db.session.commit()
    return attempt
