from sserpapi.db import connection
from sserpapi.db import models

connection.Base.metadata.create_all(bind=connection.engine)
