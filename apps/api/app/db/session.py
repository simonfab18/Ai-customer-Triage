from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _sync_sqlite_dev_schema() -> None:
    if not settings.database_url.startswith("sqlite"):
        return

    ticket_columns = {
        "gmail_connection_id": "VARCHAR(36)",
        "gmail_message_id": "VARCHAR(160)",
        "gmail_thread_id": "VARCHAR(160)",
    }
    with engine.begin() as connection:
        existing_columns = {
            row[1] for row in connection.execute(text("PRAGMA table_info(tickets)")).all()
        }
        for column_name, column_type in ticket_columns.items():
            if column_name not in existing_columns:
                connection.execute(text(f"ALTER TABLE tickets ADD COLUMN {column_name} {column_type}"))


def init_db() -> None:
    if settings.app_env != "local":
        return

    from app import models  # noqa: F401
    from app.db.base import Base

    Base.metadata.create_all(bind=engine)
    _sync_sqlite_dev_schema()

