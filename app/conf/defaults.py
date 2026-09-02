"""内置默认配置（优先级最低）。"""

DEFAULTS = {
    "ENV": "development",
    "DEBUG": False,
    "TESTING": False,
    "SECRET_KEY": "change-me-in-production",
    "HOST": "0.0.0.0",
    "PORT": 5000,
    "JSON_SORT_KEYS": False,
    "LOG_LEVEL": "INFO",
    "DATABASE": {
        "HOST": "127.0.0.1",
        "PORT": 5432,
        "NAME": "app",
        "USER": "app",
        "PASSWORD": "",
        "POOL_SIZE": 5,
    },
    "REDIS": {
        "HOST": "127.0.0.1",
        "PORT": 6379,
        "DB": 0,
        "PASSWORD": "",
    },
    "CORS": {
        "ENABLED": False,
        "ORIGINS": [],
    },
}
