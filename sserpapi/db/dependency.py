import logging
from sqlalchemy.exc import OperationalError
from sserpapi.db.connection import SessionLocal

logger = logging.getLogger(__name__)

# Database connection
def get_db():
    """
    Creates a database session and yields it.

    Returns:
        A database session.

    Raises:
        OperationalError: If there is an error connecting to the database.

    """
    try:
        db = SessionLocal()
        yield db
    except OperationalError as e:
        logger.error("get_db(): Database connection error: %s", e)
        raise e
    finally:
        db.close()
