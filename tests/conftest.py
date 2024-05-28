import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError, DBAPIError
from fastapi.testclient import TestClient
import pytest
from sserpapi.db import models
from sserpapi.main import app
from sserpapi.db.dependency import get_db

# Setup database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db.sqlite"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#username and password for access token
credential = {
        'username': 'saiful',
        'password': 'amisaiful',
    }
headers = {'Content-Type': 'application/x-www-form-urlencoded'}

# Dependency override
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

#-- Create client object for each test module --#
@pytest.fixture(scope='module')
def client():
    with TestClient(app) as c:
        yield c
   
def get_access_token():
    app_obj = TestClient(app)
    response = app_obj.post("/token", data=credential, headers=headers)
    response_data = response.json()
    with open('token.txt', 'w', encoding='utf-8') as f:
        f.write(response_data['access_token'])

def read_token():
    with open('token.txt', 'r', encoding='utf-8') as f:
        token = f.read()
    return token

#-- Create authentication header for each test module --#
@pytest.fixture(scope='module')
def auth_header():
    if os.path.exists('token.txt'):
        token = read_token()
    else:
        token = ''

    if not token:
        get_access_token()
        token = read_token()

    return {'Authorization': f'Bearer {token}'}

#-- Clear all tables before each test --#
@pytest.fixture(autouse=True)
def clear_tables():
    db = TestingSessionLocal()

    table_list = ['Services', 'ServiceTypes', 'Pops', 'Vendors', 'Clients', 'ClientTypes']

    for table in table_list:
        stmt = delete(models.__dict__[table])
        try:
            db.execute(stmt)
            db.commit()
        except IntegrityError as e:
            raise IntegrityError(str(stmt), [], e) from e
        except Exception as e:
            raise DBAPIError(str(stmt), [], e) from e

@pytest.fixture
def new_vendor():
    return {'name': 'test_vendor', 'type': 'LSP'}

@pytest.fixture
def add_vendor(auth_header, client):
    def _add_vendor(vendor: dict):
        add_vendor_response = client.post('/vendor', json=vendor, headers=auth_header)
        return add_vendor_response
    return _add_vendor