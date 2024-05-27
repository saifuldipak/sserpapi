from sserpapi.db.models import Base
from conftest import engine, TestingSessionLocal
from sserpapi.scripts.reset_db import user_add

user_data = {
        'username': 'saiful',
        'password': 'amisaiful',
        'email': 'saiful@somedoamin.com',
        'disabled': False,
        'scope': 'user'
    }

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

user_add(TestingSessionLocal(), user_data)

