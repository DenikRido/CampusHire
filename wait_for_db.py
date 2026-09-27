#!/usr/bin/env python
"""Wait until MySQL accepts connections. Used by Docker entrypoint."""
from __future__ import annotations

import os
import time

import pymysql


def main() -> None:
    if os.environ.get("DB_ENGINE", "mysql") == "sqlite":
        return
    host = os.environ.get("DB_HOST", "127.0.0.1")
    port = int(os.environ.get("DB_PORT", "3306"))
    user = os.environ.get("DB_USER", "campushire")
    password = os.environ.get("DB_PASSWORD", "")
    name = os.environ.get("DB_NAME", "campushire")
    for attempt in range(40):
        try:
            conn = pymysql.connect(host=host, port=port, user=user, password=password, database=name)
            conn.close()
            print("database ready")
            return
        except Exception as exc:
            print(f"waiting for database ({attempt + 1}/40): {exc}")
            time.sleep(2)
    raise SystemExit("database was not ready in time")


if __name__ == "__main__":
    main()
