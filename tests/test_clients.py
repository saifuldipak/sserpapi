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

new_client_type = {
    'name': 'test_client_type'
}

another_new_client_type = {}

new_vendor = {
    'name': 'Test Vendor',
    'type': 'LSP'
}

updated_new_vendor = {
    'id': 0,
    'name': 'Updated Test Vendor',
    'type': 'ISP'
}

blank_new_vendor = {}

new_pop = {
    'name': 'Test POP',
    'owner': 1,
    'extra_info': 'Test POP'
}

blank_new_pop = {}

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

#test "create_client_type"
def test_create_client_type(auth_header):
    create_client_type = client.post('/client/type', json=new_client_type, headers=auth_header)
    assert create_client_type.status_code == 200
    assert create_client_type.json()['name'] == new_client_type['name']
    
    get_client_types = client.get(f"/client/types?type_name={new_client_type['name']}", headers=auth_header)
    assert get_client_types.status_code == 200
    assert get_client_types.json()[0]['name'] == new_client_type['name']

    create_same_client_type = client.post('/client/type', json=new_client_type, headers=auth_header)
    assert create_same_client_type.status_code == 400
    assert create_same_client_type.json()['detail'] == 'Client type exists'

    create_client_type_missing_data = client.post('/client', json=another_new_client_type, headers=auth_header)
    assert create_client_type_missing_data.status_code == 422

    delete_client_type = client.delete(f"/client/type/{create_client_type.json()['id']}", headers=auth_header)
    assert delete_client_type.status_code == 200

#test "delete_client_type"
def test_delete_client_type(auth_header):
    create_client_type = client.post('/client/type', json=new_client_type, headers=auth_header)
    assert create_client_type.status_code == 200
    assert create_client_type.json()['name'] == new_client_type['name']
    
    delete_client_type = client.delete(f"/client/type/{create_client_type.json()['id']}", headers=auth_header)
    assert delete_client_type.status_code == 200

    get_client_types = client.get(f"/client/types?type_name={new_client_type['name']}", headers=auth_header)
    assert get_client_types.status_code == 404

    delete_client_type_wrong_id = client.delete("/client/type/0", headers=auth_header)
    assert delete_client_type_wrong_id.status_code == 400
    assert delete_client_type_wrong_id.json()['detail'] == 'Client type not found'

    delete_client_type_missing_id = client.delete("/client/type/", headers=auth_header)
    assert delete_client_type_missing_id.status_code == 422

#test "get_client_types"
def test_get_client_types(auth_header):
    create_client_type = client.post('/client/type', json=new_client_type, headers=auth_header)
    assert create_client_type.status_code == 200
    
    get_client_types = client.get('/client/types', headers=auth_header)
    assert get_client_types.status_code == 200
    assert get_client_types.json().__len__() > 1

    get_client_types_by_name = client.get(f"/client/types?type_name={new_client_type['name']}", headers=auth_header)
    assert get_client_types_by_name.status_code == 200
    assert get_client_types_by_name.json()[0]['name'] == new_client_type['name']

    get_client_types_by_id = client.get(f"/client/types?type_id={create_client_type.json()['id']}", headers=auth_header)
    assert get_client_types_by_id.status_code == 200
    assert get_client_types_by_id.json()[0]['name'] == new_client_type['name']
    assert get_client_types_by_id.json()[0]['id'] == create_client_type.json()['id']

    get_client_types_by_name_id = client.get(f"/client/types?type_name={new_client_type['name']}&type_id={create_client_type.json()['id']}", headers=auth_header)
    assert get_client_types_by_name_id.status_code == 200
    assert get_client_types_by_name_id.json()[0]['name'] == new_client_type['name']
    assert get_client_types_by_name_id.json()[0]['id'] == create_client_type.json()['id']

    get_client_types_by_wrong_name = client.get("/client/types?type_name='wrong_type_name'", headers=auth_header)
    assert get_client_types_by_wrong_name.status_code == 404
    
    get_client_types_by_wrong_id = client.get("/client/types?type_id=101", headers=auth_header)
    assert get_client_types_by_wrong_id.status_code == 404

    delete_client = client.delete(f"/client/type/{create_client_type.json()['id']}", headers=auth_header)
    assert delete_client.status_code == 200

#test "add_vendor"
def test_add_vendor(auth_header):
    create_vendor = client.post('/vendor', json=new_vendor, headers=auth_header)
    assert create_vendor.status_code == 200
    assert create_vendor.json()['name'] == new_vendor['name']
    assert create_vendor.json()['type'] == new_vendor['type']

    get_vendors = client.get(f"/vendors?vendor_name={new_vendor['name']}", headers=auth_header)
    assert get_vendors.status_code == 200
    assert get_vendors.json()[0]['name'] == new_vendor['name']
    assert get_vendors.json()[0]['type'] == new_vendor['type']

    create_same_vendor = client.post('/vendor', json=new_vendor, headers=auth_header)
    assert create_same_vendor.status_code == 400
    assert create_same_vendor.json()['detail'] == 'Vendor exists'

    create_vendor_no_data = client.post('/vendor', json=blank_new_vendor, headers=auth_header)
    assert create_vendor_no_data.status_code == 422

    delete_vendors = client.delete(f"/vendor/{create_vendor.json()['id']}", headers=auth_header)
    assert delete_vendors.status_code == 200

#test "update_vendor"
def test_update_vendor(auth_header):
    create_vendor = client.post('/vendor', json=new_vendor, headers=auth_header)
    assert create_vendor.status_code == 200

    updated_new_vendor['id'] = create_vendor.json()['id']
    update_vendor = client.put("/vendor", json=updated_new_vendor, headers=auth_header)
    assert update_vendor.status_code == 200

    get_vendors = client.get(f"/vendors?vendor_id={create_vendor.json()['id']}", headers=auth_header)
    assert get_vendors.status_code == 200
    assert get_vendors.json()[0]['name'] == updated_new_vendor['name']
    assert get_vendors.json()[0]['type'] == updated_new_vendor['type']

    updated_new_vendor['id'] = 1001
    update_vendor_wrong_id = client.put("/vendor", json=updated_new_vendor, headers=auth_header)
    assert update_vendor_wrong_id.status_code == 400

    blank_new_vendor['id'] = create_vendor.json()['id']
    update_vendor_missing_data = client.put("/vendor", json=blank_new_vendor, headers=auth_header)
    assert update_vendor_missing_data.status_code == 422

    update_vendor_missing_body = client.put("/vendor", headers=auth_header)
    assert update_vendor_missing_body.status_code == 422

    delete_vendors = client.delete(f"/vendor/{create_vendor.json()['id']}", headers=auth_header)
    assert delete_vendors.status_code == 200

#test "get_vendors"
def test_get_vendors(auth_header):
    create_vendor = client.post('/vendor', json=new_vendor, headers=auth_header)
    assert create_vendor.status_code == 200

    get_vendors_by_name = client.get(f"/vendors?vendor_name={new_vendor['name']}", headers=auth_header)
    assert get_vendors_by_name.status_code == 200
    assert get_vendors_by_name.json()[0]['name'] == new_vendor['name']
    assert get_vendors_by_name.json()[0]['type'] == new_vendor['type']

    get_vendors_by_type = client.get(f"/vendors?vendor_type={new_vendor['type']}", headers=auth_header)
    assert get_vendors_by_type.status_code == 200
    assert get_vendors_by_type.json()[0]['name'] == new_vendor['name']
    assert get_vendors_by_type.json()[0]['type'] == new_vendor['type']

    get_vendors_by_id = client.get(f"/vendors?vendor_id={create_vendor.json()['id']}", headers=auth_header)
    assert get_vendors_by_id.status_code == 200
    assert get_vendors_by_id.json()[0]['name'] == new_vendor['name']
    assert get_vendors_by_id.json()[0]['type'] == new_vendor['type']

    get_vendors_by_name_type_id = client.get(f"/vendors?vendor_name={new_vendor['name']}&vendor_type={new_vendor['type']}&vendor_id={create_vendor.json()['id']}", headers=auth_header)
    assert get_vendors_by_name_type_id.status_code == 200
    assert get_vendors_by_name_type_id.json()[0]['name'] == new_vendor['name']
    assert get_vendors_by_name_type_id.json()[0]['type'] == new_vendor['type']
    assert get_vendors_by_name_type_id.json()[0]['id'] == create_vendor.json()['id']

    get_vendors_by_wrong_name = client.get("/vendors?vendor_name='wrong_name'", headers=auth_header)
    assert get_vendors_by_wrong_name.status_code == 404

    get_vendors_by_wrong_type = client.get("/vendors?vendor_type='wrong_type", headers=auth_header)
    assert get_vendors_by_wrong_type.status_code == 404

    get_vendors_by_wrong_id = client.get("/vendors?vendor_id=10001", headers=auth_header)
    assert get_vendors_by_wrong_id.status_code == 404

    get_vendors_missing_query_parameters = client.get("/vendors", headers=auth_header)
    assert get_vendors_missing_query_parameters.status_code == 422

    delete_vendors = client.delete(f"/vendor/{create_vendor.json()['id']}", headers=auth_header)
    assert delete_vendors.status_code == 200

#test "delete_vendor"
def test_delete_vendor(auth_header):
    create_vendor = client.post('/vendor', json=new_vendor, headers=auth_header)
    assert create_vendor.status_code == 200

    delete_vendor = client.delete(f"/vendor/{create_vendor.json()['id']}", headers=auth_header)
    assert delete_vendor.status_code == 200
    assert delete_vendor.json()['id'] == create_vendor.json()['id']
    assert delete_vendor.json()['message'] == 'Vendor deleted'

    delete_same_vendor = client.delete(f"/vendor/{create_vendor.json()['id']}", headers=auth_header)
    assert delete_same_vendor.status_code == 400
    assert delete_same_vendor.json()['detail'] == 'Vendor not found'

    delete_vendor_missing_id = client.delete("/vendor", headers=auth_header)
    assert delete_vendor_missing_id.status_code == 405

#test "add_pop"
def test_add_pop(auth_header):
    add_vendor_response = client.post('/vendor', json=new_vendor, headers=auth_header)
    assert add_vendor_response.status_code == 200

    copy_new_pop = dict(new_pop)
    copy_new_pop['owner'] = add_vendor_response.json()['id']
    add_pop_response = client.post('/pop', json=copy_new_pop, headers=auth_header)
    assert add_pop_response.status_code == 200
    assert add_pop_response.json()['name'] == new_pop['name']
    assert add_pop_response.json()['owner'] == copy_new_pop['owner']
    assert add_pop_response.json()['extra_info'] == copy_new_pop['extra_info']

    add_same_pop_response = client.post('/pop', json=copy_new_pop, headers=auth_header)
    assert add_same_pop_response.status_code == 400
    assert add_same_pop_response.json()['detail'] == 'Pop exists'

    add_pop_missing_data_response = client.post('/pop', json=blank_new_pop, headers=auth_header)
    assert  add_pop_missing_data_response.status_code == 422

    add_pop_missing_body_response = client.post('/pop', headers=auth_header)
    assert add_pop_missing_body_response.status_code == 422

    delete_pop_response = client.delete(f"/pop/{add_pop_response.json()['id']}", headers=auth_header)
    assert delete_pop_response.status_code == 200

    delete_vendor_response = client.delete(f"/vendor/{add_vendor_response.json()['id']}", headers=auth_header)
    assert delete_vendor_response.status_code == 200
