from app import create_app
from app.services.ai_service import generate_quiz_questions


def generate_weekly_quiz():
    app = create_app()

    with app.app_context():
        questions = generate_quiz_questions(
            category="Mixed Rights",
            country="General",
            number_of_questions=10
        )

        # Save questions to MySQL here.
        # Set reviewed=False until approved by an administrator.

        return len(questions)
