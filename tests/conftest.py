import os
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

    table_list = ['Services', 'ServiceTypes', 'Pops', 'Vendors', 'Clients', 'ClientTypes', 'Contacts', 'Addresses']

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
def add_pop_only(auth_header, client):
    def _add_pop_only(pop: dict):
        add_pop_response = client.post('/pop', json=pop, headers=auth_header)
        return add_pop_response
    return _add_pop_only

@pytest.fixture
def add_pop(add_vendor, new_vendor, add_pop_only):
    def _add_pop(pop: dict):
        add_vendor_response = add_vendor(new_vendor)
        assert add_vendor_response.status_code == 200
        pop['owner'] = add_vendor_response.json()['id']
        add_pop_response = add_pop_only(pop)
        assert add_pop_response.status_code == 200
        return add_pop_response
    return _add_pop

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
def add_client_only(auth_header, client):
    def _add_client_only(client_data: dict):
        add_client_response = client.post('/client', json=client_data, headers=auth_header)
        return add_client_response
    return _add_client_only

@pytest.fixture
def add_client(add_client_type, new_client_type, add_client_only):
    def _add_client(client: dict):
        add_client_type_response = add_client_type(new_client_type)
        assert add_client_type_response.status_code == 200
        client['client_type_id'] = add_client_type_response.json()['id']
        add_client_response = add_client_only(client)
        assert add_client_response.status_code == 200
        return add_client_response
    return _add_client

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

@pytest.fixture
def new_service():
    return {'client_id': 0, 'point': 'test_service', 'service_type_id': 0, 'bandwidth': 100, 'pop_id': 0, 'extra_info': 'test_extra_info'}

@pytest.fixture
def add_service(add_service_type, new_service_type, add_client, new_client, add_pop, new_pop, client, auth_header):
    def _add_service(service: dict):
        add_service_type_response = add_service_type(new_service_type)
        assert add_service_type_response.status_code == 200
        add_client_response = add_client(new_client)
        assert add_client_response.status_code == 200
        add_pop_response = add_pop(new_pop)
        assert add_pop_response.status_code == 200
        service['client_id'] = add_client_response.json()['id']
        service['service_type_id'] = add_service_type_response.json()['id']
        service['pop_id'] = add_pop_response.json()['id']
        add_service_response = client.post('/service', json=service, headers=auth_header)
        return add_service_response
    return _add_service

@pytest.fixture
def add_service_only(auth_header, client):
    def _add_service_only(service: dict):
        add_service_only_response = client.post('/service', json=service, headers=auth_header)
        return add_service_only_response
    return _add_service_only

@pytest.fixture
def new_service_updated():
    return {'id': 0, 'client_id': 0, 'point': 'updated_test_service', 'service_type_id': 0, 'bandwidth': 200, 'pop_id': 0, 'extra_info': 'updated_test_extra_info'}

@pytest.fixture
def new_contact():
    return {'name': 'First_Name Last_Name', 'designation': 'Manager', 'type': 'Technical', 'phone1': '01713433900', 'email': 'email@somedomain.com'}

@pytest.fixture
def new_contact_updated():
    return {'id': 0, 'name': 'Updated_First_Name Updated_Last_Name', 'designation': 'Sr. Manager', 'type': 'Admin', 'phone1': '01713422900', 'email': 'myemail@somedomain.com'}

@pytest.fixture
def add_contact(auth_header, client):
    def _add_contact(contact: dict):
        add_contact_response = client.post('/contact', json=contact, headers=auth_header)
        return add_contact_response
    return _add_contact

@pytest.fixture
def new_address():
    return {'flat': 'A1', 'floor': '1st', 'holding': '999/9 Holding', 'street': 'Ghost street', 'area': 'Vampire housing society', 'thana': 'Horror thana', 'district': 'Dracula district', 'extra_info': 'test_extra_info'}

@pytest.fixture
def add_address(auth_header, client):
    def _add_address(address: dict):
        add_address_response = client.post('/address', json=address, headers=auth_header)
        return add_address_response
    return _add_address

@pytest.fixture
def new_address_updated():
        return {'id': 0, 'flat': 'A2', 'floor': '2nd', 'holding': '888/8 Holding', 'street': 'Dragon street', 'area': 'Vampire housing society', 'thana': 'Horror thana', 'district': 'Dracula castle district', 'extra_info': 'extra_info_updated'}

@pytest.fixture
def update_address(auth_header, client):
    def _update_address(address: dict):
        update_address_response = client.put('/address', json=address, headers=auth_header)
        return update_address_response
    return _update_address

@pytest.fixture
def delete_address(auth_header, client):
    def _delete_address(address_id: int):
        delete_address_response = client.delete(f'/address/{address_id}', headers=auth_header)
        return delete_address_response
    return _delete_address