import json
import os
import requests

from app.data.reference_material import get_reference_text

GEMINI_API_KEY="AQ.Ab8RN6KiXyb6bx1V5TCuXJZ96qqyDlftYhr8Y6ew33JDbUCM5Q"
os.getenv("GEMINI_API_KEY")

GEMINI_URL="https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"



def generate_quiz_questions(
    category: str,
    country: str,
    number_of_questions: int = 5,
    existing_questions: list = None,
) -> list:
    """Generate multiple-choice questions grounded in the reference material
    for `category`, avoiding repeats of anything in `existing_questions`.

    `existing_questions` should be the question text of every question
    already stored for this category, so the model doesn't generate
    near-duplicates of content already in the bank.
    """
    existing_questions = existing_questions or []
    reference_text = get_reference_text(category)

    # Cap how many prior questions we paste into the prompt so it stays a
    # reasonable size even once the bank has grown large.
    existing_block = "\n".join(f"- {q}" for q in existing_questions[-40:]) or "(none yet)"

    prompt = f"""
Generate {number_of_questions} educational multiple-choice questions about: {category}
Country or jurisdiction: {country}

Base every question strictly on the REFERENCE MATERIAL below. Do not invent
laws, rights, or section numbers that are not in it.

REFERENCE MATERIAL:
{reference_text}

QUESTIONS ALREADY IN THE BANK FOR THIS CATEGORY (do not repeat these, and do
not generate close rewordings of them -- every new question must be
distinct in what it tests, not just reworded):
{existing_block}

Return JSON in this format:
{{
  "questions": [
    {{
      "question": "Question text",
      "options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
      "correct_answer": "Option A",
      "explanation": "Educational explanation citing the relevant right or section",
      "difficulty": "easy"
    }}
  ]
}}

Rules:
1. Do not invent laws or facts beyond the reference material.
2. Mention when rules differ by country, if relevant.
3. Do not provide legal advice.
4. Use simple language.
5. Every question in this batch must be distinct from every other question
   in this batch, and from the list of existing questions above -- no two
   questions may test the same fact in different words.
6. Questions must teach fundamental, citizen, consumer, or digital rights.
"""

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0.4,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You create neutral civic education content grounded only "
                    "in the reference material you are given. "
                    "All legal content requires human review."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    result = json.loads(response.choices[0].message.content)
    questions = result.get("questions", [])

    # Defense in depth: drop any question whose text exactly matches one
    # already in the bank or is repeated within this same batch, in case the
    # model didn't fully honor rule 5.
    seen = {q.strip().lower() for q in existing_questions}
    distinct_questions = []
    for item in questions:
        text_key = item.get("question", "").strip().lower()
        if not text_key or text_key in seen:
            continue
        seen.add(text_key)
        distinct_questions.append(item)

    return distinct_questions
