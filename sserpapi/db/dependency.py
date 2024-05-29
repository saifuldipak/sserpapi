import logging
from sqlalchemy.exc import OperationalError, DBAPIError
from sserpapi.db.connection import SessionLocal

logger = logging.getLogger(__name__)

# Database connection
def get_db():
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        logger.error("get_db(): Database connection error: %s", e)
        raise e
    finally:
        db.close()
