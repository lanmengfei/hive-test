# Flask 多层配置管理示例

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

- 健康检查：`GET /health`
- 公开配置：`GET /api/config`（不含密钥）

## 配置优先级（低 → 高）

1. `app/conf/defaults.py` — 代码默认值
2. `app/conf/files/base.yaml` — 各环境共享
3. `app/conf/files/{ENV}.yaml` — 环境专属（development / production / testing）
4. `app/conf/files/local.yaml` — 本机覆盖（不入库，参考 `local.yaml.example`）
5. 环境变量 — 前缀 `APP_`，嵌套用 `__`，例如 `APP_DATABASE__HOST`

环境名解析：`APP_ENV` > `FLASK_ENV` > 默认 `development`。

## 测试

```bash
pytest test/ -q
```
