"""Flask 应用工厂。"""

from __future__ import annotations

from flask import Flask

from app.conf import load_config


def create_app(env: str | None = None, conf_dir=None) -> Flask:
    """创建并配置 Flask 应用。

    Args:
        env: 运行环境名（development / production / testing），默认读 APP_ENV。
        conf_dir: 可选，自定义配置文件目录（测试时注入临时目录）。
    """
    app = Flask(__name__)
    config = load_config(env=env, conf_dir=conf_dir)
    app.config.update(config)

    _register_blueprints(app)
    return app


def _register_blueprints(app: Flask) -> None:
    from app.blueprints.health import bp as health_bp
    from app.blueprints.config_view import bp as config_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(config_bp)
