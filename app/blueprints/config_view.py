"""配置查看接口（仅暴露非敏感信息，便于联调）。"""

from flask import Blueprint, current_app, jsonify

bp = Blueprint("config_view", __name__, url_prefix="/api")

# 允许对外展示的配置键（不含密钥类字段）
_PUBLIC_KEYS = (
    "ENV",
    "DEBUG",
    "TESTING",
    "HOST",
    "PORT",
    "LOG_LEVEL",
    "JSON_SORT_KEYS",
)


@bp.get("/config")
def public_config():
    cfg = current_app.config
    payload = {key: cfg.get(key) for key in _PUBLIC_KEYS}
    database = cfg.get("DATABASE") or {}
    payload["DATABASE"] = {
        "HOST": database.get("HOST"),
        "PORT": database.get("PORT"),
        "NAME": database.get("NAME"),
        "USER": database.get("USER"),
        "POOL_SIZE": database.get("POOL_SIZE"),
        # 故意不返回 PASSWORD
    }
    redis_cfg = cfg.get("REDIS") or {}
    payload["REDIS"] = {
        "HOST": redis_cfg.get("HOST"),
        "PORT": redis_cfg.get("PORT"),
        "DB": redis_cfg.get("DB"),
    }
    cors = cfg.get("CORS") or {}
    payload["CORS"] = {
        "ENABLED": cors.get("ENABLED"),
        "ORIGINS": cors.get("ORIGINS"),
    }
    return jsonify(payload)
