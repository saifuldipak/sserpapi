import pytest
from fastapi.testclient import TestClient
from sserpapi.main import app
import os

client = TestClient(app)

data = {
    'username': 'saiful',
    'password': 'amisaiful'
}

new_client = {
    'name': 'test_client',
    'client_type_id': 1
}

another_new_client = {
    'name': 'another_test_client',
    'client_type_id': 1
}

updated_client = {
    'id': 0,
    'name': 'test_client_updated',
    'client_type_id': 2
}

client_type = 'bank'

def get_access_token():
    response = client.post('/token', data=data)
    response_data = response.json()
    with open('token.txt', 'w', encoding='utf-8') as f:
        f.write(response_data['access_token'])

def read_token():
    with open('token.txt', 'r', encoding='utf-8') as f:
        token = f.read()
    return token

@pytest.fixture
def auth_header():
    if os.path.exists('token.txt'):
        token = read_token()
    else:
        token = ''

    if not token:
        get_access_token()
        token = read_token()

    return {'Authorization': f'Bearer {token}'}

# test "create_client"
def test_create_client(auth_header):
    create_response = client.post('/client', json=new_client, headers=auth_header)
    assert create_response.status_code == 200
    assert create_response.json()['name'] == new_client['name']
    assert create_response.json()['client_type_id'] == new_client['client_type_id']
    client_id = create_response.json()['id']
    
    get_response = client.get(f'/clients?client_name={create_response.json()["name"]}', headers=auth_header)
    assert get_response.status_code == 200
    assert get_response.json()[0]['name'] == new_client['name']
    assert get_response.json()[0]['client_type_id'] == new_client['client_type_id']

    create_response = client.post('/client', json=new_client, headers=auth_header)
    assert create_response.status_code == 400
    assert create_response.json()['detail'] == 'Client exists'

    new_client_missing_data = dict(another_new_client)
    del new_client_missing_data['client_type_id']
    create_response = client.post('/client', json=new_client_missing_data, headers=auth_header)
    assert create_response.status_code == 422

    new_client_wrong_client_type = dict(new_client)
    new_client_wrong_client_type['client_type_id'] = 100
    create_response = client.post('/client', json=new_client_wrong_client_type, headers=auth_header)
    assert create_response.status_code == 400
    assert create_response.json()['detail'] == 'Client type does not exist'

    delete_response = client.delete(f'/client/{client_id}', headers=auth_header)
    assert delete_response.status_code == 200

#test "update_client"
def test_update_client(auth_header):
    create_client = client.post('/client', json=new_client, headers=auth_header)
    assert create_client.status_code == 200

    copy_updated_client = dict(updated_client)
    copy_updated_client['id'] = create_client.json()['id']
    update_client = client.put('/client', json=copy_updated_client, headers=auth_header)
    assert update_client.status_code == 200
    
    get_client = client.get(f"/clients?client_id={create_client.json()['id']}", headers=auth_header)
    assert get_client.status_code == 200
    assert get_client.json()[0]['name'] == copy_updated_client['name']
    assert get_client.json()[0]['client_type_id'] == copy_updated_client['client_type_id']

    update_client_same_data = client.put('/client', json=copy_updated_client, headers=auth_header)
    assert update_client_same_data.status_code == 400

    update_client_wrong_id = client.put('/client', json=updated_client, headers=auth_header)
    assert update_client_wrong_id.status_code == 404

    copy_updated_client = dict(updated_client)
    copy_updated_client['id'] = create_client.json()['id']
    del copy_updated_client['name']
    update_client_missing_name = client.put('/client', json=copy_updated_client, headers=auth_header)
    assert update_client_missing_name.status_code == 422

    delete_response = client.delete(f"client/{create_client.json()['id']}", headers=auth_header)
    assert delete_response.status_code == 200

#test "delete_client"
def test_delete_client(auth_header):
    create_client = client.post('/client', json=new_client, headers=auth_header)
    assert create_client.status_code == 200
    
    get_client = client.get(f'/clients?client_name={create_client.json()["name"]}', headers=auth_header)
    assert get_client.status_code == 200

    delete_client = client.delete(f'/client/{create_client.json()["id"]}', headers=auth_header)
    assert delete_client.status_code == 200
    assert delete_client.json()['message'] == 'Client deleted'
    assert delete_client.json()['id'] == create_client.json()['id']

    get_client = client.get(f'/clients?client_name={create_client.json()["name"]}', headers=auth_header)
    assert get_client.status_code == 404

    delete_client_not_found = client.delete(f'/client/{create_client.json()["id"]}', headers=auth_header)
    assert delete_client_not_found.status_code == 404

# test "get_clients"
def test_get_clients(auth_header):
    create_client = client.post('/client', json=new_client, headers=auth_header)
    assert create_client.status_code == 200

    get_clients_by_name = client.get(f'/clients?client_name={new_client["name"]}', headers=auth_header)
    assert get_clients_by_name.status_code == 200
    assert get_clients_by_name.json()[0]['name'] == new_client['name']
    assert get_clients_by_name.json()[0]['client_type_id'] == new_client['client_type_id']

    get_clients_by_id = client.get(f"/clients?client_id={create_client.json()['id']}", headers=auth_header)
    assert get_clients_by_id.status_code == 200
    assert get_clients_by_id.json()[0]['name'] == new_client['name']
    assert get_clients_by_id.json()[0]['client_type_id'] == new_client['client_type_id']

    get_clients_by_name_type = client.get(f"/clients?client_name={new_client['name']}&client_type={client_type}", headers=auth_header)
    assert get_clients_by_name_type.status_code == 200
    assert get_clients_by_name_type.json()[0]['name'] == new_client['name']
    assert get_clients_by_name_type.json()[0]['client_type_id'] == new_client['client_type_id']

    get_clients_by_name_wrong_type = client.get(f"/clients?client_name={new_client['name']}&client_type='wrong_type", headers=auth_header)
    assert get_clients_by_name_wrong_type.status_code == 404
    
    get_clients_by_id_name_type = client.get(f"/clients?client_id={create_client.json()['id']}&client_name={new_client['name']}&client_type={client_type}", headers=auth_header)
    assert get_clients_by_id_name_type.status_code == 200
    assert get_clients_by_id_name_type.json()[0]['name'] == new_client['name']
    assert get_clients_by_id_name_type.json()[0]['client_type_id'] == new_client['client_type_id']

    get_clients_missing_parameters = client.get('/clients', headers=auth_header)
    assert get_clients_missing_parameters.status_code == 400

    get_clients_wrong_parameters = client.get(f"/clients?clients_name={new_client['name']}", headers=auth_header)
    assert get_clients_wrong_parameters.status_code == 400

    delete_client = client.delete(f"/client/{create_client.json()['id']}", headers=auth_header)
    assert delete_client.status_code == 200

    get_clients_not_found = client.get(f"/clients?client_id={create_client.json()['id']}&client_name={new_client['name']}", headers=auth_header)
    assert get_clients_not_found.status_code == 404