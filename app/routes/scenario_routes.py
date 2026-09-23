from flask import Blueprint, render_template, jsonify, request, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.models.scenario import ScenarioProgress
from app.services.scenario_engine import (
    ScenarioEngine,
    ScenarioNotFoundError,
    ScenarioChoiceError,
)

scenario_bp = Blueprint("scenario", __name__, url_prefix="/scenarios")
engine = ScenarioEngine()


def _get_or_create_progress(scenario_id: str, node_id: str) -> ScenarioProgress:
    progress = ScenarioProgress.query.filter_by(
        user_id=current_user.id, scenario_id=scenario_id
    ).first()

    if not progress:
        progress = ScenarioProgress(
            user_id=current_user.id,
            scenario_id=scenario_id,
            current_node_id=node_id,
        )
        db.session.add(progress)
        db.session.commit()

    return progress


@scenario_bp.route("/")
@login_required
def scenario_list_page():
    scenarios = engine.list_scenarios()
    return render_template("scenario_list.html", scenarios=scenarios)


@scenario_bp.route("/<scenario_id>", methods=["GET", "POST"])
@login_required
def scenario_page(scenario_id):
    try:
        scenario_data = engine.load(scenario_id)
    except ScenarioNotFoundError:
        abort(404)

    feedback = None

    if request.method == "POST":
        submitted_node_id = request.form.get("node_id")
        choice_id = request.form.get("choice_id")

        try:
            result = engine.choose(scenario_id, submitted_node_id, choice_id)
        except ScenarioChoiceError:
            abort(400)

        node = result["node"]
        node_id = result["node_id"]
        feedback = result["feedback"]

        progress = _get_or_create_progress(scenario_id, node_id)
        progress.current_node_id = node_id
        progress.points_earned = (progress.points_earned or 0) + result["points"]
        progress.completed = result["is_end"]
        db.session.commit()

        if result["points"]:
            current_user.add_points(result["points"])
            db.session.commit()

    else:
        start = engine.get_start_node(scenario_id)
        node = start["node"]
        node_id = start["node_id"]
        _get_or_create_progress(scenario_id, node_id)

    scenario_meta = {
        "id": scenario_id,
        "title": scenario_data.get("title"),
        "category": scenario_data.get("category"),
    }

    return render_template(
        "scenario.html",
        scenario=scenario_meta,
        node=node,
        node_id=node_id,
        feedback=feedback,
    )


# JSON API kept for any script-driven usage elsewhere in the app.
@scenario_bp.route("/api/list")
@login_required
def api_list():
    return jsonify(engine.list_scenarios())


@scenario_bp.route("/api/<scenario_id>/start")
@login_required
def api_start(scenario_id):
    try:
        node = engine.get_start_node(scenario_id)
    except ScenarioNotFoundError:
        return jsonify({"error": "Scenario not found"}), 404

    _get_or_create_progress(scenario_id, node["node_id"])
    return jsonify(node)


@scenario_bp.route("/api/<scenario_id>/choose", methods=["POST"])
@login_required
def api_choose(scenario_id):
    data = request.get_json() or {}
    node_id = data.get("node_id")
    choice_id = data.get("choice_id")

    try:
        result = engine.choose(scenario_id, node_id, choice_id)
    except (ScenarioNotFoundError, ScenarioChoiceError) as exc:
        return jsonify({"error": str(exc)}), 400

    progress = ScenarioProgress.query.filter_by(
        user_id=current_user.id, scenario_id=scenario_id
    ).first()

    if progress:
        progress.current_node_id = result["node_id"]
        progress.points_earned += result["points"]
        progress.completed = result["is_end"]
        db.session.commit()

    if result["points"]:
        current_user.add_points(result["points"])
        db.session.commit()

    return jsonify(result)