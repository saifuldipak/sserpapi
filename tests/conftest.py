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

#username and password for access token
credential = {
        'username': 'saiful',
        'password': 'amisaiful',
    }
headers = {'Content-Type': 'application/x-www-form-urlencoded'}

#-- Create client object for each test module --#
@pytest.fixture(scope='module')
def client():
    with TestClient(app) as c:
        yield c

#-- Create authentication header for each test module --#
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
    db = next(get_db())

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

@pytest.fixture
def new_pop():
    return {'name': 'test_pop', 'owner': 1, 'extra_info': 'test_extra_info'}

@pytest.fixture
def updated_pop():
    return {'id': 0, 'name': 'updated_test_pop', 'owner': 1, 'extra_info': 'updated_test_extra_info'}

@pytest.fixture
def add_pop(auth_header, client):
    def _add_pop(pop: dict):
        add_pop_response = client.post('/pop', json=pop, headers=auth_header)
        return add_pop_response
    return _add_pop

@pytest.fixture
def add_vendor_and_pop(add_vendor, new_vendor, add_pop, new_pop):
    add_vendor_response = add_vendor(new_vendor)
    assert add_vendor_response.status_code == 200

    new_pop['owner'] = add_vendor_response.json()['id']
    add_pop_response = add_pop(new_pop)
    assert add_pop_response.status_code == 200
    
    return add_pop_response

@pytest.fixture
def new_client_type():
    return {'name': 'test_client_type'}

@pytest.fixture
def another_new_client_type():
    return {'name': 'another_test_client_type'}

@pytest.fixture
def add_client_type(auth_header, client):
    def _add_client_type(client_type: dict):
        add_client_type_response = client.post('/client/type', json=client_type, headers=auth_header)
        return add_client_type_response
    return _add_client_type

@pytest.fixture
def new_client():
    return {'name': 'test_client', 'client_type_id': 0}

@pytest.fixture
def updated_client():
    return {'id': 0, 'name': 'updated_test_client', 'client_type_id': 0}

@pytest.fixture
def add_client(auth_header, client):
    def _add_client(client_data: dict):
        add_client_response = client.post('/client', json=client_data, headers=auth_header)
        return add_client_response
    return _add_client

@pytest.fixture
def add_client_type_and_client(add_client_type, new_client_type, add_client, new_client):
    add_client_type_response = add_client_type(new_client_type)
    assert add_client_type_response.status_code == 200

    new_client['client_type_id'] = add_client_type_response.json()['id']
    add_client_response = add_client(new_client)
    assert add_client_response.status_code == 200

    return add_client_response, new_client

@pytest.fixture
def update_client(auth_header, client):
    def _update_client(client_data: dict):
        add_client_response = client.put('/client', json=client_data, headers=auth_header)
        return add_client_response
    return _update_client

@pytest.fixture
def new_service_type():
    return {'name': 'test_service_type', 'description': 'test_description'}

@pytest.fixture
def add_service_type(auth_header, client):
    def _add_service_type(service_type: dict):
        add_service_type_response = client.post('/service/type', json=service_type, headers=auth_header)
        return add_service_type_response
    return _add_service_type