import pytest
from fastapi.testclient import TestClient
from sserpapi.main import app
import json
import requests

client = TestClient(app)

data = {
    'username': 'saiful',
    'password': 'amisaiful'
}

new_client = {
    'name': 'test_client',
    'client_type_id': 1
}

client_data = {
    'client_name': 'test_client',
    'client_type': 'bank',
    'wrong_client_name': 'nothing',
    'wrong_client_type': 'nothing',
    'none_client_name': None,
    'none_client_type': None,
}

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
    token = read_token()
    if not token:
        get_access_token()
        token = read_token()

    return {'Authorization': f'Bearer {token}'}

# test "create_client"
def test_create_client(auth_header):
    response = client.post('/client', json=new_client, headers=auth_header)
    assert response.status_code == 200
    assert response.json()['name'] == new_client['name']
    assert response.json()['client_type_id'] == new_client['client_type_id']

def test_create_client_exists(auth_header):
    response = client.post('/client', json=new_client, headers=auth_header)
    assert response.status_code == 400
    assert response.json()['detail'] == 'Client exists'

def test_create_client_missing_data(auth_header):
    new_client_missing_data = dict(new_client)
    del new_client_missing_data['client_type_id']
    response = client.post('/client', json=new_client_missing_data, headers=auth_header)
    assert response.status_code == 422

def test_create_client_wrong_client_type(auth_header):
    new_client_wrong_client_type = dict(new_client)
    new_client_wrong_client_type['client_type_id'] = 100
    response = client.post('/client', json=new_client_wrong_client_type, headers=auth_header)
    assert response.status_code == 400
    assert response.json()['detail'] == 'Client type does not exist'

# test "get_clients"
def test_get_clients_by_name(auth_header):
    response = client.get(f'/clients?client_name={client_data["client_name"]}', headers=auth_header)
    assert response.status_code == 200

def test_get_clients_by_name_wrong_name(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.get(f'/clients?client_name={client_data["wrong_client_name"]}', headers=headers)
    assert response.status_code == 404

def test_get_clients_by_name_none_value(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.get(f'/clients?client_name={client_data["none_client_name"]}', headers=headers)
    assert response.status_code == 404

def test_get_clients_by_type(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.get(f'/clients?client_type={client_data["client_type"]}', headers=headers)
    assert response.status_code == 200

def test_get_clients_by_type_wrong_type(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.get(f'/clients?client_type={client_data["wrong_client_type"]}', headers=headers)
    assert response.status_code == 404

def test_get_clients_by_type_none_value(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.get(f'/clients?client_type={client_data["none_client_type"]}', headers=headers)
    assert response.status_code == 404

def test_get_clients_by_name_and_type(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.get(f'/clients?client_name={client_data["client_name"]}&client_type={client_data["client_type"]}', headers=headers)
    assert response.status_code == 200

def test_get_clients_by_name_and_type_wrong_name_and_type(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.get(f'/clients?client_name={client_data["wrong_client_name"]}&client_type={client_data["client_type"]}', headers=headers)
    assert response.status_code == 404
    response = client.get(f'/clients?client_name={client_data["client_name"]}&client_type={client_data["wrong_client_type"]}', headers=headers)
    assert response.status_code == 404
    response = client.get(f'/clients?client_name={client_data["wrong_client_name"]}&client_type={client_data["wrong_client_type"]}', headers=headers)
    assert response.status_code == 404

def test_get_clients_by_name_and_type_none_value(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = client.get(f'/clients?client_name={client_data["none_client_name"]}&client_type={client_data["client_type"]}', headers=headers)
    assert response.status_code == 404
    response = client.get(f'/clients?client_name={client_data["client_name"]}&client_type={client_data["none_client_type"]}', headers=headers)
    assert response.status_code == 404
    response = client.get(f'/clients?client_name={client_data["none_client_name"]}&client_type={client_data["none_client_type"]}', headers=headers)
    assert response.status_code == 404