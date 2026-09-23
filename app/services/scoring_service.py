def calculate_quiz_score(questions, submitted_answers):
    score = 0
    results = []

    for question in questions:
        selected_answer = submitted_answers.get(str(question.id))
        correct = selected_answer == question.correct_answer

        if correct:
            score += 1

        results.append({
            "question_id": question.id,
            "selected_answer": selected_answer,
            "correct": correct,
            "correct_answer": question.correct_answer,
            "explanation": question.explanation
        })

    points = score * 10

    return {
        "score": score,
        "total": len(questions),
        "points": points,
        "results": results
    }
