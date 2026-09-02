"""健康检查。"""

from flask import Blueprint, current_app, jsonify

bp = Blueprint("health", __name__)


@bp.get("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "env": current_app.config.get("ENV"),
        }
    )
