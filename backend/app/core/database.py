from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
from app.core.config import settings
from app.core.models import Base

logger = logging.getLogger("ats-optimizer")

# Dynamic DB engine creation: Check PostgreSQL first, fall back to SQLite
try:
    engine = create_engine(settings.DATABASE_URL)
    # Check connection
    connection = engine.connect()
    connection.close()
    logger.info("Successfully connected to PostgreSQL database.")
except Exception as e:
    logger.warning(f"PostgreSQL connection failed: {e}. Falling back to SQLite local database.")
    engine = create_engine(settings.SQLITE_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Database session generator dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initializes tables in database."""
    Base.metadata.create_all(bind=engine)
