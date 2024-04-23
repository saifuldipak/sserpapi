import logging
from sqlalchemy.exc import OperationalError
from sserpapi.db.connection import SessionLocal

logger = logging.getLogger(__name__)

# Database connection
def get_db():
    """
    Function to get a database connection.
    Yields a database session.
    Catches OperationalError and logs the error.
    Closes the database session in the end.
    """
    try:
        db = SessionLocal()
        yield db
    except OperationalError as e:
        logger.error('Database connection error: %s', e)
        raise e
    finally:
        db.close()
