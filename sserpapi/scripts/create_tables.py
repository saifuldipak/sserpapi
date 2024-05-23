from sserpapi.db import connection
from sserpapi.db import models

connection.Base.metadata.drop_all(bind=connection.engine)
connection.Base.metadata.create_all(bind=connection.engine)
