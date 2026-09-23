from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user

from app.extensions import db
from app.models.quiz import QuizQuestion
from app.services import quiz_service
from app.services.scoring_service import calculate_quiz_score
from app.services.ai_service import generate_quiz_questions

quiz_bp = Blueprint("quiz", __name__, url_prefix="/quiz")

CATEGORIES = ["Consumer Rights", "Citizen Rights", "Digital Rights", "Fundamental Rights"]


@quiz_bp.get("/")
@login_required
def get_quiz():
    """Renders the interactive quiz page. All question loading/submission
    happens client-side against the JSON API endpoints below."""
    return render_template("quiz.html", categories=CATEGORIES)


@quiz_bp.get("/api/questions")
@login_required
def api_get_questions():
    category = request.args.get("category") or None
    weekly = request.args.get("weekly", "false").lower() == "true"
    limit = request.args.get("limit", default=5, type=int)

    if weekly:
        questions = quiz_service.get_weekly_test_questions(limit=limit)
    else:
        questions = quiz_service.get_reviewed_questions(category=category, limit=limit)

    return jsonify([q.to_dict() for q in questions])


@quiz_bp.post("/api/submit")
@login_required
def api_submit_quiz():
    data = request.get_json() or {}
    answers = data.get("answers", {})
    category = data.get("category", "mixed")
    is_weekly = bool(data.get("is_weekly", False))

    if not answers:
        return jsonify({"error": "No answers submitted."}), 400

    question_ids = [int(qid) for qid in answers.keys()]
    questions = QuizQuestion.query.filter(QuizQuestion.id.in_(question_ids)).all()

    if not questions:
        return jsonify({"error": "Submitted questions could not be found."}), 400

    scored = calculate_quiz_score(questions, answers)

    quiz_service.record_attempt(
        user=current_user,
        category=category,
        score=scored["score"],
        total=scored["total"],
        points=scored["points"],
        is_weekly=is_weekly,
    )

    return jsonify(scored)


@quiz_bp.post("/generate")
@login_required
def generate_quiz():
    """Admin/utility endpoint: asks the AI to generate new questions grounded
    in the reference material, skipping anything that duplicates a question
    already in the bank for that category."""
    data = request.get_json() or {}

    category = data.get("category", "Consumer Rights")
    country = data.get("country", "India")
    count = data.get("count", 5)

    existing_questions = quiz_service.get_existing_question_texts(category)

    generated_questions = generate_quiz_questions(
        category,
        country,
        count,
        existing_questions=existing_questions,
    )

    saved = 0
    for item in generated_questions:
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
        )
        db.session.add(question)
        saved += 1

    db.session.commit()

    return jsonify({
        "message": "Questions generated and awaiting review",
        "count": saved,
    })
