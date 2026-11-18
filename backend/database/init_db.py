"""Manual setup: python backend/database/init_db.py

Creates all tables in the configured PostgreSQL database.
"""

import os
import sys

from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

load_dotenv()

from database import models  # noqa: E402,F401
from database.connection import Base, engine  # noqa: E402


def main() -> None:
    Base.metadata.create_all(engine)
    print("Tables created:", list(Base.metadata.tables.keys()))


if __name__ == "__main__":
    main()
