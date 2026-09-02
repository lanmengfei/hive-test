"""多层配置加载器单元测试。"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

from app.conf.loader import deep_merge, get_nested, load_config, load_env_overrides


@pytest.fixture
def conf_dir(tmp_path: Path) -> Path:
    base = {
        "LOG_LEVEL": "INFO",
        "DATABASE": {"HOST": "base-host", "PORT": 5432, "NAME": "base_db"},
    }
    development = {
        "DEBUG": True,
        "DATABASE": {"HOST": "dev-host", "NAME": "dev_db"},
    }
    testing = {
        "TESTING": True,
        "DEBUG": False,
        "DATABASE": {"NAME": "test_db"},
    }
    local = {
        "PORT": 8080,
        "DATABASE": {"PASSWORD": "local-pass"},
    }
    (tmp_path / "base.yaml").write_text(yaml.dump(base), encoding="utf-8")
    (tmp_path / "development.yaml").write_text(
        yaml.dump(development), encoding="utf-8"
    )
    (tmp_path / "testing.yaml").write_text(yaml.dump(testing), encoding="utf-8")
    (tmp_path / "local.yaml").write_text(yaml.dump(local), encoding="utf-8")
    return tmp_path


def test_deep_merge_nested():
    base = {"A": 1, "NESTED": {"X": 1, "Y": 2}}
    override = {"NESTED": {"Y": 9, "Z": 3}, "B": 2}
    merged = deep_merge(base, override)
    assert merged == {"A": 1, "B": 2, "NESTED": {"X": 1, "Y": 9, "Z": 3}}
    # 不修改原对象
    assert base["NESTED"]["Y"] == 2


def test_load_config_layers(conf_dir: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("APP_DATABASE__HOST", raising=False)
    monkeypatch.delenv("APP_PORT", raising=False)
    cfg = load_config(env="development", conf_dir=conf_dir, load_dotenv_file=False)
    assert cfg["ENV"] == "development"
    assert cfg["DEBUG"] is True
    assert cfg["LOG_LEVEL"] == "INFO"  # 来自 base
    assert cfg["DATABASE"]["HOST"] == "dev-host"  # env 覆盖 base
    assert cfg["DATABASE"]["PORT"] == 5432  # base 保留
    assert cfg["DATABASE"]["NAME"] == "dev_db"
    assert cfg["DATABASE"]["PASSWORD"] == "local-pass"  # local 覆盖
    assert cfg["PORT"] == 8080  # local


def test_env_var_overrides_highest(
    conf_dir: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setenv("APP_DATABASE__HOST", "from-env")
    monkeypatch.setenv("APP_DATABASE__PORT", "6543")
    monkeypatch.setenv("APP_DEBUG", "false")
    cfg = load_config(env="development", conf_dir=conf_dir, load_dotenv_file=False)
    assert cfg["DATABASE"]["HOST"] == "from-env"
    assert cfg["DATABASE"]["PORT"] == 6543
    assert cfg["DEBUG"] is False
    # local 仍生效（未被 env 覆盖的键）
    assert cfg["PORT"] == 8080


def test_load_env_overrides_coercion(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("APP_FLAG", "true")
    monkeypatch.setenv("APP_COUNT", "12")
    monkeypatch.setenv("APP_RATIO", "1.5")
    monkeypatch.setenv("APP_NAME", "demo")
    overrides = load_env_overrides()
    assert overrides["FLAG"] is True
    assert overrides["COUNT"] == 12
    assert overrides["RATIO"] == 1.5
    assert overrides["NAME"] == "demo"


def test_get_nested():
    cfg = {"DATABASE": {"HOST": "h1"}, "LOG_LEVEL": "INFO"}
    assert get_nested(cfg, "DATABASE.HOST") == "h1"
    assert get_nested(cfg, "database.host") == "h1"
    assert get_nested(cfg, "missing.key", "x") == "x"


def test_testing_env(conf_dir: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("APP_DATABASE__HOST", raising=False)
    cfg = load_config(env="testing", conf_dir=conf_dir, load_dotenv_file=False)
    assert cfg["TESTING"] is True
    assert cfg["DATABASE"]["NAME"] == "test_db"
    assert cfg["DATABASE"]["HOST"] == "base-host"
