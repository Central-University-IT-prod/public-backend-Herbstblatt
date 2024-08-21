import os

from .models import *

tortoise_config = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": os.environ.get("PGHOST", "localhost"),
                "port": os.environ.get("PGPORT", 5432),
                "user": os.environ.get("PGUSER", ""),
                "password": os.environ.get("PGPASSWORD", ""),
                "database": os.environ.get("PGDATABASE", "")
            }
        }
    },
    "apps": {
        "travel_agent": {
            "models": ["db.models", "aerich.models"]
        }
    }
}