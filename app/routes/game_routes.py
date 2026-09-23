from flask import Blueprint, render_template, jsonify, request
import secrets
import string
from flask_login import login_required, current_user

from app.extensions import db
from app.models.game import GameProgress
from app.models.quiz import QuizQuestion
from app.services import quiz_service
from app.games.snakes_ladders import SnakesAndLadders
from app.games.real_or_myth import RealOrMythGame
from app.games.treasure_hunt import TreasureHuntGame
game_bp = Blueprint("game", __name__, url_prefix="/games")

snakes_ladders_engine = SnakesAndLadders()
real_or_myth_engine = RealOrMythGame()
treasure_hunt_engine = TreasureHuntGame()

# Lightweight room store for local/hackathon multiplayer. Players in the same
# room share one board and take turns. Polling keeps this dependency-free, so
# the project does not require Flask-SocketIO/Node for the demo.
MULTIPLAYER_ROOMS = {}

def _new_room_code():
    alphabet = string.ascii_uppercase + string.digits
    while True:
        code = "".join(secrets.choice(alphabet) for _ in range(6))
        if code not in MULTIPLAYER_ROOMS:
            return code

def _room_public(room):
    return {
        "code": room["code"],
        "started": room["started"],
        "turn_index": room["turn_index"],
        "players": room["players"],
        "max_players": 4,
    }


def _get_or_create_progress(game_name: str) -> GameProgress:
    progress = GameProgress.query.filter_by(
        user_id=current_user.id, game_name=game_name
    ).first()

    if not progress:
        progress = GameProgress(
            user_id=current_user.id,
            game_name=game_name,
            position=1,
            points=0,
            extra_state={},
        )
        db.session.add(progress)
        db.session.commit()

    return progress


@game_bp.route("/")
@login_required
def games_page():
    return render_template("games.html")


# ---------------- Snakes & Ladders (quiz-gated dice rolls) ----------------
#
# True to the original board game -- you don't get to roll for free. Each
# turn, you're asked a rights question drawn from the reviewed quiz bank.
# Answer correctly and you earn your dice roll; answer incorrectly and you
# stay put, but get a fresh question to try again on your next attempt.

@game_bp.route("/api/snakes-ladders/question", methods=["GET"])
@login_required
def snakes_ladders_question():
    progress = _get_or_create_progress("snakes_ladders")

    if progress.completed:
        return jsonify({"completed": True, "message": "You already reached square 100!"})

    state = progress.extra_state or {}
    asked_ids = state.get("asked_ids", [])

    questions = quiz_service.get_reviewed_questions(limit=1, exclude_ids=asked_ids)
    question = questions[0] if questions else None

    # Every reviewed question has been asked this game -- start a fresh
    # rotation rather than getting stuck with no question at all.
    if not question:
        asked_ids = []
        questions = quiz_service.get_reviewed_questions(limit=1)
        question = questions[0] if questions else None

    if not question:
        return jsonify({"error": "No quiz questions are available yet. Seed the quiz bank first."}), 400

    state["pending_question_id"] = question.id
    state["asked_ids"] = asked_ids
    progress.extra_state = state
    db.session.commit()

    return jsonify(question.to_dict())


@game_bp.route("/api/snakes-ladders/roll", methods=["POST"])
@login_required
def snakes_ladders_roll():
    progress = _get_or_create_progress("snakes_ladders")

    if progress.completed:
        return jsonify({"message": "You already reached square 100!", "position": progress.position, "completed": True})

    data = request.get_json() or {}
    question_id = data.get("question_id")
    answer = data.get("answer", "")

    state = progress.extra_state or {}
    pending_id = state.get("pending_question_id")

    if not question_id or pending_id != question_id:
        return jsonify({"error": "Answer the current question before rolling."}), 400

    question = QuizQuestion.query.get(question_id)
    if not question:
        return jsonify({"error": "Question not found."}), 400

    correct = answer == question.correct_answer

    if not correct:
        return jsonify({
            "correct": False,
            "position": progress.position,
            "explanation": question.explanation,
            "correct_answer": question.correct_answer,
            "message": "Not quite -- no roll this turn. Try the next question.",
        })

    # Correct answer earns the dice roll.
    asked_ids = state.get("asked_ids", [])
    asked_ids.append(question.id)
    state["asked_ids"] = asked_ids
    state["pending_question_id"] = None

    result = snakes_ladders_engine.move(progress.position)
    quiz_bonus = 5

    progress.position = result["position"]
    progress.points += result["points_earned"] + quiz_bonus
    progress.completed = result["completed"]
    progress.extra_state = state
    db.session.commit()

    current_user.add_points(result["points_earned"] + quiz_bonus)
    db.session.commit()

    return jsonify({
        **result,
        "correct": True,
        "quiz_bonus": quiz_bonus,
        "quiz_explanation": question.explanation,
        "total_game_points": progress.points,
    })



# ---------------- Multiplayer Snakes & Ladders ----------------

@game_bp.post("/api/snakes-ladders/multiplayer/create")
@login_required
def multiplayer_create():
    code = _new_room_code()
    MULTIPLAYER_ROOMS[code] = {
        "code": code,
        "host_id": current_user.id,
        "started": False,
        "turn_index": 0,
        "pending_question_id": None,
        "asked_ids": [],
        "players": [{
            "user_id": current_user.id,
            "name": current_user.name,
            "position": 1,
            "points": 0,
        }],
    }
    return jsonify(_room_public(MULTIPLAYER_ROOMS[code]))


@game_bp.post("/api/snakes-ladders/multiplayer/join")
@login_required
def multiplayer_join():
    data = request.get_json() or {}
    code = str(data.get("code", "")).strip().upper()
    room = MULTIPLAYER_ROOMS.get(code)
    if not room:
        return jsonify({"error": "Room not found. Check the room code."}), 404
    if any(p["user_id"] == current_user.id for p in room["players"]):
        return jsonify(_room_public(room))
    if len(room["players"]) >= 4:
        return jsonify({"error": "This room is full (maximum 4 players)."}), 400
    if room["started"]:
        return jsonify({"error": "This game has already started."}), 400
    room["players"].append({
        "user_id": current_user.id,
        "name": current_user.name,
        "position": 1,
        "points": 0,
    })
    return jsonify(_room_public(room))


@game_bp.post("/api/snakes-ladders/multiplayer/start")
@login_required
def multiplayer_start():
    data = request.get_json() or {}
    room = MULTIPLAYER_ROOMS.get(str(data.get("code", "")).strip().upper())
    if not room:
        return jsonify({"error": "Room not found."}), 404
    if room["host_id"] != current_user.id:
        return jsonify({"error": "Only the room host can start the game."}), 403
    if len(room["players"]) < 2:
        return jsonify({"error": "Join with at least 2 players before starting."}), 400
    room["started"] = True
    room["turn_index"] = 0
    return jsonify(_room_public(room))


@game_bp.post("/api/snakes-ladders/multiplayer/restart")
@login_required
def multiplayer_restart():
    data = request.get_json() or {}
    room = MULTIPLAYER_ROOMS.get(str(data.get("code", "")).strip().upper())
    if not room:
        return jsonify({"error": "Room not found."}), 404
    if room["host_id"] != current_user.id:
        return jsonify({"error": "Only the room host can restart the game."}), 403

    for player in room["players"]:
        player["position"] = 1
        player["points"] = 0

    room["started"] = False
    room["turn_index"] = 0
    room["pending_question_id"] = None
    room["asked_ids"] = []

    return jsonify(_room_public(room))


@game_bp.get("/api/snakes-ladders/multiplayer/state/<code>")
@login_required
def multiplayer_state(code):
    room = MULTIPLAYER_ROOMS.get(code.upper())
    if not room:
        return jsonify({"error": "Room not found."}), 404
    return jsonify(_room_public(room))


@game_bp.get("/api/snakes-ladders/multiplayer/question/<code>")
@login_required
def multiplayer_question(code):
    room = MULTIPLAYER_ROOMS.get(code.upper())
    if not room:
        return jsonify({"error": "Room not found."}), 404
    if not room["started"]:
        return jsonify({"error": "Game has not started yet."}), 400
    player = room["players"][room["turn_index"]]
    if player["user_id"] != current_user.id:
        return jsonify({"waiting": True, "turn": player["name"], "state": _room_public(room)})

    if room["pending_question_id"]:
        question = QuizQuestion.query.get(room["pending_question_id"])
        if question:
            return jsonify(question.to_dict())

    asked = room.get("asked_ids", [])
    questions = quiz_service.get_reviewed_questions(limit=1, exclude_ids=asked)
    if not questions:
        room["asked_ids"] = []
        questions = quiz_service.get_reviewed_questions(limit=1)
    if not questions:
        return jsonify({"error": "No quiz questions are available. Restart the app after the quiz seed has run."}), 400
    question = questions[0]
    room["pending_question_id"] = question.id
    return jsonify(question.to_dict())


@game_bp.post("/api/snakes-ladders/multiplayer/answer/<code>")
@login_required
def multiplayer_answer(code):
    room = MULTIPLAYER_ROOMS.get(code.upper())
    if not room:
        return jsonify({"error": "Room not found."}), 404
    if not room["started"]:
        return jsonify({"error": "Game has not started yet."}), 400

    player = room["players"][room["turn_index"]]
    if player["user_id"] != current_user.id:
        return jsonify({"error": f"It is {player['name']}'s turn."}), 400

    data = request.get_json() or {}
    question_id = data.get("question_id")
    answer = data.get("answer", "")
    if question_id != room.get("pending_question_id"):
        return jsonify({"error": "Answer the current question first."}), 400

    question = QuizQuestion.query.get(question_id)
    if not question:
        return jsonify({"error": "Question not found."}), 400

    if answer != question.correct_answer:
        return jsonify({
            "correct": False,
            "message": "Incorrect answer. Your turn is lost.",
            "explanation": question.explanation,
            "correct_answer": question.correct_answer,
            "state": _room_public(room),
        })

    room["asked_ids"].append(question.id)
    room["pending_question_id"] = None
    result = snakes_ladders_engine.move(player["position"])
    player["position"] = result["position"]
    player["points"] += result["points_earned"] + 5

    winner = player["position"] == 100
    if not winner:
        room["turn_index"] = (room["turn_index"] + 1) % len(room["players"])
    else:
        room["started"] = False

    return jsonify({
        **result,
        "correct": True,
        "winner": winner,
        "player_name": player["name"],
        "state": _room_public(room),
        "quiz_explanation": question.explanation,
    })

# ---------------- Real or Myth ----------------

@game_bp.route("/api/real-or-myth/next", methods=["GET"])
@login_required
def real_or_myth_next():
    progress = _get_or_create_progress("real_or_myth")
    seen_ids = (progress.extra_state or {}).get("seen_ids", [])

    statement = real_or_myth_engine.get_random_statement(exclude_ids=seen_ids)
    return jsonify(statement)


@game_bp.route("/api/real-or-myth/answer", methods=["POST"])
@login_required
def real_or_myth_answer():
    data = request.get_json() or {}
    statement_id = data.get("id")
    answer = data.get("answer", "")

    result = real_or_myth_engine.check_answer(statement_id, answer)

    if "error" in result:
        return jsonify(result), 400

    progress = _get_or_create_progress("real_or_myth")
    state = progress.extra_state or {}
    seen_ids = state.get("seen_ids", [])
    seen_ids.append(statement_id)
    state["seen_ids"] = seen_ids
    progress.extra_state = state
    progress.points += result["points_earned"]
    db.session.commit()

    if result["points_earned"]:
        current_user.add_points(result["points_earned"])
        db.session.commit()

    return jsonify({**result, "total_game_points": progress.points})


# ---------------- Treasure Hunt ----------------

@game_bp.route("/api/treasure-hunt/current", methods=["GET"])
@login_required
def treasure_hunt_current():
    progress = _get_or_create_progress("treasure_hunt")
    index = (progress.extra_state or {}).get("clue_index", 0)

    clue = treasure_hunt_engine.get_clue(index)
    if not clue:
        return jsonify({"treasure_found": True, "message": "You already found the treasure!"})

    return jsonify({**clue, "total_clues": treasure_hunt_engine.total_clues()})


@game_bp.route("/api/treasure-hunt/answer", methods=["POST"])
@login_required
def treasure_hunt_answer():
    data = request.get_json() or {}
    answer = data.get("answer", "")

    progress = _get_or_create_progress("treasure_hunt")
    state = progress.extra_state or {}
    index = state.get("clue_index", 0)

    result = treasure_hunt_engine.check_answer(index, answer)

    if "error" in result:
        return jsonify(result), 400

    if result["correct"]:
        state["clue_index"] = result["next_index"]
        progress.extra_state = state
        progress.points += result["points_earned"]
        progress.completed = result["treasure_found"]
        db.session.commit()

        current_user.add_points(result["points_earned"])
        db.session.commit()

    return jsonify({**result, "total_game_points": progress.points})
