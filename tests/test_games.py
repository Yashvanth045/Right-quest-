from app.games.snakes_ladders import SnakesAndLadders
from app.games.real_or_myth import RealOrMythGame, STATEMENTS
from app.games.treasure_hunt import TreasureHuntGame, CLUES


def test_snakes_ladders_never_exceeds_100():
    game = SnakesAndLadders()
    for _ in range(200):
        result = game.move(current_position=95)
        assert result["position"] <= 100


def test_snakes_ladders_ladder_and_snake_mapping():
    game = SnakesAndLadders()
    # square 3 is a ladder to 22
    assert game.LADDERS[3] == 22
    # square 17 is a snake to 7
    assert game.SNAKES[17] == 7


def test_real_or_myth_correct_answer():
    game = RealOrMythGame()
    statement = STATEMENTS[0]
    result = game.check_answer(statement["id"], statement["answer"])
    assert result["correct"] is True
    assert result["points_earned"] == 10


def test_real_or_myth_incorrect_answer():
    game = RealOrMythGame()
    statement = STATEMENTS[0]
    wrong_answer = "myth" if statement["answer"] == "real" else "real"
    result = game.check_answer(statement["id"], wrong_answer)
    assert result["correct"] is False
    assert result["points_earned"] == 0


def test_treasure_hunt_progression():
    game = TreasureHuntGame()
    first_clue = CLUES[0]
    result = game.check_answer(0, first_clue["answer"])
    assert result["correct"] is True
    assert result["next_index"] == 1
    assert result["treasure_found"] is False


def test_treasure_hunt_final_clue_finds_treasure():
    game = TreasureHuntGame()
    last_index = len(CLUES) - 1
    last_clue = CLUES[last_index]
    result = game.check_answer(last_index, last_clue["answer"])
    assert result["correct"] is True
    assert result["treasure_found"] is True
