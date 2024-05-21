from sqlalchemy.exc import IntegrityError, DBAPIError
from sqlalchemy import delete
import sserpapi.db.models
from sserpapi.db.connection import SessionLocal

def clear_tables():
    db = SessionLocal()

    table_list = ['Services', 'ServiceTypes', 'Pops', 'Vendors', 'Clients', 'ClientTypes']

    for table in table_list:
        stmt = delete(sserpapi.db.models.__dict__[table])
        try:
            db.execute(stmt)
            db.commit()
        except IntegrityError as e:
            raise IntegrityError(str(stmt), [], e) from e
        except Exception as e:
            raise DBAPIError(str(stmt), [], e) from e

