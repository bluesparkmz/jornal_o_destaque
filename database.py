from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
engine = create_engine(settings().database_url, pool_pre_ping=True, pool_recycle=1800)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    session = SessionLocal()
    try: yield session
    finally: session.close()


