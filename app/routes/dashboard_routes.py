from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from app.models.quiz import QuizAttempt
from app.models.game import GameProgress

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))
    return render_template("dashboard.html")


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    recent_attempts = (
        QuizAttempt.query
        .filter_by(user_id=current_user.id)
        .order_by(QuizAttempt.completed_at.desc())
        .limit(5)
        .all()
    )

    game_progress = GameProgress.query.filter_by(user_id=current_user.id).all()

    badges = []
    if current_user.points >= 1:
        badges.append("First Steps")
    if current_user.points >= 100:
        badges.append("Rights Explorer")
    if any(a.is_weekly_test for a in recent_attempts):
        badges.append("Weekly Challenger")
    if any(g.completed for g in game_progress):
        badges.append("Game Master")

    return render_template(
        "dashboard.html",
        user=current_user,
        recent_attempts=recent_attempts,
        game_progress=game_progress,
        badges=badges,
    )
