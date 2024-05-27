import pytest
from sserpapi.pydantic_schemas import ClientBase, ClientTypeBase

@pytest.fixture
def new_client_type():
    return {'name': 'test_client_type'}

@pytest.fixture
def new_client():
    return {'name' : 'test_client', 'client_type_id': 1}

@pytest.fixture
def add_client_type(new_client_type, auth_header, client):
    add_client_type_response = client.post('/client/type', json=new_client_type, headers=auth_header)
    assert add_client_type_response.status_code == 200
    return add_client_type_response

@pytest.fixture
def add_client(auth_header, client, add_client_type, new_client):
    client_type_data = add_client_type.json()
    new_client['client_type_id'] = client_type_data['id']
    add_client_response = client.post('/client', json=new_client, headers=auth_header)
    assert add_client_response.status_code == 200
    return add_client_response

def test_add_client(add_client, new_client):
    new_client_data = add_client
    assert new_client_data.status_code == 200
    assert new_client_data.json()['name'] == new_client['name']
    assert new_client_data.json()['client_type_id'] == new_client['client_type_id']

def test_add_duplicate_client(auth_header, client, add_client, new_client):
    client_data = add_client
    add_duplicate_client = client.post('/client', json=new_client, headers=auth_header)
    assert add_duplicate_client.status_code == 400
    assert add_duplicate_client.json()['detail'] == 'Client exists'

def test_add_client_wrong_client_type(auth_header, client, new_client):
    new_client['client_type_id'] = 10001
    add_client_wrong_client_type = client.post('/client', json=new_client, headers=auth_header)
    assert add_client_wrong_client_type.status_code == 400
    assert add_client_wrong_client_type.json()['detail'] == 'Client type does not exist'

def test_add_client_blank_body(auth_header, client):
    add_client_blank_body = client.post('/client', json={}, headers=auth_header)
    assert add_client_blank_body.status_code == 422

def test_add_client_missing_body(auth_header, client):
    add_client_missing_body = client.post('/client', headers=auth_header)
    assert add_client_missing_body.status_code == 422

def test_get_clients_by_name(auth_header, client, add_client):
    client_data = add_client.json()
    get_clients = client.get(f"/clients?client_name={client_data['name']}", headers=auth_header)
    assert get_clients.status_code == 200
    assert get_clients.json()[0]['name'] == client_data['name']

def test_get_clients_by_partial_name(auth_header, client, add_client):
    client_data = add_client.json()
    partial_client_name = client_data['name'][:3]
    get_clients = client.get(f"/clients?client_name={partial_client_name}", headers=auth_header)
    assert get_clients.status_code == 200
    assert get_clients.json()[0]['name'] == client_data['name']

def test_get_clients_by_id(auth_header, client, add_client):
    client_data = add_client.json()
    get_clients = client.get(f"/clients?client_id={client_data['id']}", headers=auth_header)
    assert get_clients.status_code == 200
    assert get_clients.json()[0]['name'] == client_data['name']

def test_get_clients_missing_parameters(auth_header, client):
    get_clients = client.get('/clients', headers=auth_header)
    assert get_clients.status_code == 400
    assert get_clients.json()['detail'] == 'You must give at least one query parameter, please see API documentation'
