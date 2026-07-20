import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from models.db_models import Base

logger = logging.getLogger("ats-optimizer")

engine = None

# 1. Try PostgreSQL if DATABASE_URL is explicitly configured
if settings.DATABASE_URL.strip():
    try:
        engine = create_engine(settings.DATABASE_URL)
        connection = engine.connect()
        connection.close()
        logger.info("Successfully connected to PostgreSQL database.")
    except Exception as e:
        logger.warning(f"PostgreSQL connection failed: {e}. Falling back to SQLite local database.")
        engine = None

# 2. Try writable temp directory SQLite
if engine is None:
    try:
        engine = create_engine(settings.SQLITE_DATABASE_URL, connect_args={"check_same_thread": False})
        connection = engine.connect()
        connection.close()
        logger.info(f"Connected to SQLite database at {settings.SQLITE_DATABASE_URL}")
    except Exception as e:
        logger.warning(f"SQLite temp database failed: {e}. Falling back to in-memory SQLite database.")
        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

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
