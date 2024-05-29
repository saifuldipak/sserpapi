import logging
from sqlalchemy.exc import OperationalError, DBAPIError
from sserpapi.db.connection import SessionLocal

logger = logging.getLogger(__name__)

# Database connection
def get_db():
    try:
        db = SessionLocal()
        yield db
    except OperationalError as e:
        logger.error('Database connection error: %s', e)
        raise DBAPIError(str(e), [], e) from e
    except Exception as e:
        logger.error('Database connection error: %s', e)
        raise DBAPIError(str(e), [], e) from e
    finally:
        db.close()
