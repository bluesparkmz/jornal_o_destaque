from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import settings
from models import Base

engine = create_engine(settings().database_url, pool_pre_ping=True, pool_recycle=1800)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def create_database_schema() -> None:
    """Cria as tabelas ausentes sem apagar dados existentes."""
    Base.metadata.create_all(bind=engine, checkfirst=True)
    # create_all não acrescenta colunas a tabelas existentes. Esta actualização é
    # idempotente e mantém as notícias que já estavam publicadas.
    with engine.begin() as connection:
        connection.execute(
            text(
                "ALTER TABLE articles "
                "ADD COLUMN IF NOT EXISTS views_count INTEGER NOT NULL DEFAULT 0"
            )
        )

def get_db():
    session = SessionLocal()
    try: yield session
    finally: session.close()


