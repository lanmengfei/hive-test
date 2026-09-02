"""多层配置加载器。

优先级（由低到高，后者覆盖前者）：
1. 代码默认值 defaults.DEFAULTS
2. base.yaml
3. {ENV}.yaml（development / production / testing 等）
4. local.yaml（本机覆盖，通常不入库）
5. 环境变量（前缀 APP_，嵌套用双下划线，如 APP_DATABASE__HOST）
"""

from __future__ import annotations

import copy
import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

from app.conf.defaults import DEFAULTS

CONF_DIR = Path(__file__).resolve().parent / "files"
ENV_PREFIX = "APP_"
NESTED_SEP = "__"


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """递归合并字典，override 覆盖 base；不修改入参。"""
    result = copy.deepcopy(base)
    for key, value in override.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"配置文件必须是映射对象: {path}")
    return data


def _coerce_env_value(raw: str) -> Any:
    lowered = raw.strip().lower()
    if lowered in {"true", "yes", "on"}:
        return True
    if lowered in {"false", "no", "off"}:
        return False
    if lowered in {"null", "none", ""}:
        return None
    try:
        if raw.strip().isdigit() or (
            raw.strip().startswith("-") and raw.strip()[1:].isdigit()
        ):
            return int(raw.strip())
    except ValueError:
        pass
    try:
        if "." in raw:
            return float(raw.strip())
    except ValueError:
        pass
    return raw


def _set_nested(target: dict[str, Any], keys: list[str], value: Any) -> None:
    cursor = target
    for part in keys[:-1]:
        node = cursor.setdefault(part, {})
        if not isinstance(node, dict):
            node = {}
            cursor[part] = node
        cursor = node
    cursor[keys[-1]] = value


def load_env_overrides(prefix: str = ENV_PREFIX) -> dict[str, Any]:
    """从环境变量解析覆盖项。

    示例：
      APP_DEBUG=true
      APP_DATABASE__HOST=db.internal
      APP_DATABASE__PORT=5433
    """
    overrides: dict[str, Any] = {}
    for key, raw in os.environ.items():
        if not key.startswith(prefix):
            continue
        path = key[len(prefix) :]
        if not path:
            continue
        parts = [p for p in path.split(NESTED_SEP) if p]
        if not parts:
            continue
        _set_nested(overrides, parts, _coerce_env_value(raw))
    return overrides


def resolve_env_name(explicit: str | None = None) -> str:
    """解析运行环境名：参数 > APP_ENV > FLASK_ENV > defaults。"""
    if explicit:
        return explicit
    return (
        os.environ.get("APP_ENV")
        or os.environ.get("FLASK_ENV")
        or str(DEFAULTS.get("ENV", "development"))
    )


def load_config(
    env: str | None = None,
    conf_dir: Path | str | None = None,
    load_dotenv_file: bool = True,
) -> dict[str, Any]:
    """按多层优先级加载并合并配置，返回可写入 Flask app.config 的字典。"""
    if load_dotenv_file:
        # 项目根目录 .env；已存在的系统环境变量优先，不被覆盖
        root = Path(__file__).resolve().parents[2]
        load_dotenv(root / ".env", override=False)

    conf_path = Path(conf_dir) if conf_dir else CONF_DIR
    env_name = resolve_env_name(env)

    config = copy.deepcopy(DEFAULTS)
    config = deep_merge(config, _load_yaml(conf_path / "base.yaml"))
    config = deep_merge(config, _load_yaml(conf_path / f"{env_name}.yaml"))
    config = deep_merge(config, _load_yaml(conf_path / "local.yaml"))
    config = deep_merge(config, load_env_overrides())

    config["ENV"] = env_name
    # Flask 约定键
    config.setdefault("DEBUG", bool(config.get("DEBUG", False)))
    config.setdefault("TESTING", env_name == "testing" or bool(config.get("TESTING")))
    return config


def get_nested(config: dict[str, Any], dotted_key: str, default: Any = None) -> Any:
    """按点号路径取值，如 database.host。大小写不敏感时先尝试原样再大写。"""
    cursor: Any = config
    for part in dotted_key.split("."):
        if not isinstance(cursor, dict):
            return default
        if part in cursor:
            cursor = cursor[part]
        elif part.upper() in cursor:
            cursor = cursor[part.upper()]
        else:
            return default
    return cursor
