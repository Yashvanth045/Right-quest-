"""
Seeds the quiz_questions table with curated, human-authored questions drawn
directly from source material (Consumer Protection Act 2019 / Ministry of
Consumer Affairs, the Citizen Rights Protection Council, and the Information
Technology Act, 2000), rather than relying solely on unreviewed AI generation.

These are inserted with reviewed=True and a real `source` citation, so they
are immediately eligible for /quiz/ without needing manual admin review.

Usage (from the "Right Quest" project root, with your virtualenv active and
DATABASE_URL / .env configured):

    python scripts/seed_quiz_questions.py

Safe to re-run: it skips any question whose text already exists in the table.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.quiz import QuizQuestion


SOURCE_CPA = "Consumer Protection Act, 2019 / Ministry of Consumer Affairs (consumeraffairs.gov.in)"
SOURCE_CRPC = "Citizen Rights Protection Council (crpc.in)"
SOURCE_IT_ACT = "The Information Technology Act, 2000"

from app.services.quiz_seed_data import QUESTIONS


def seed():
    app = create_app()

    with app.app_context():
        inserted = 0
        skipped = 0

        for item in QUESTIONS:
            exists = QuizQuestion.query.filter_by(question=item["question"]).first()
            if exists:
                skipped += 1
                continue

            question = QuizQuestion(
                category=item["category"],
                country=item["country"],
                question=item["question"],
                options=item["options"],
                correct_answer=item["correct_answer"],
                explanation=item["explanation"],
                difficulty=item["difficulty"],
                source=item["source"],
                reviewed=True,  # curated from primary sources, so pre-approved
            )
            db.session.add(question)
            inserted += 1

        db.session.commit()
        print(f"Seed complete: {inserted} inserted, {skipped} already present.")


if __name__ == "__main__":
    seed()
