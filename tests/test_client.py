#helper functions
def assert_client_response_json(client_response_json, new_client):
    assert client_response_json['name'] == new_client['name']
    assert client_response_json['client_type_id'] == new_client['client_type_id']

#test "add_client"
def test_add_client(new_client_type, add_client_type, add_client_only, new_client):
    add_client_type_response = add_client_type(new_client_type)
    assert add_client_type_response.status_code == 200

    new_client['client_type_id'] = add_client_type_response.json()['id']
    add_client_response = add_client_only(new_client)
    assert add_client_response.status_code == 200
    assert_client_response_json(add_client_response.json(), new_client)

def test_add_duplicate_client(new_client_type, add_client_type, add_client_only, new_client):
    add_client_type_response = add_client_type(new_client_type)
    assert add_client_type_response.status_code == 200

    new_client['client_type_id'] = add_client_type_response.json()['id']
    add_client_response = add_client_only(new_client)
    assert add_client_response.status_code == 200

    add_duplicate_client_response = add_client_only(new_client)
    assert add_duplicate_client_response.status_code == 400
    assert add_duplicate_client_response.json()['detail'] == 'Client exists'

def test_add_client_wrong_client_type(new_client, add_client_only):
    new_client['client_type_id'] = 10001
    add_client_response = add_client_only(new_client)
    assert add_client_response.status_code == 400
    assert add_client_response.json()['detail'] == 'Client type does not exist'

def test_add_client_blank_body(add_client_only):
    add_client_response = add_client_only({})
    assert add_client_response.status_code == 422

def test_add_client_missing_body(auth_header, client):
    add_client_missing_body = client.post('/client', headers=auth_header)
    assert add_client_missing_body.status_code == 422

#test "get_clients"
def test_get_clients_by_name(auth_header, client, add_client, new_client):
    add_client_response = add_client(new_client)
    assert add_client_response.status_code == 200

    get_clients_response = client.get(f"/clients?client_name={new_client['name']}", headers=auth_header)
    assert_client_response_json(get_clients_response.json()[0], new_client)

def test_get_clients_by_partial_name(auth_header, client, add_client, new_client):
    add_client_response = add_client(new_client)
    assert add_client_response.status_code == 200

    partial_client_name = new_client['name'][:3]
    get_clients_response = client.get(f"/clients?client_name={partial_client_name}", headers=auth_header)
    assert_client_response_json(get_clients_response.json()[0], new_client)

def test_get_clients_by_id(auth_header, client, add_client, new_client):
    add_client_response = add_client(new_client)
    assert add_client_response.status_code == 200

    get_clients_response = client.get(f"/clients?client_id={add_client_response.json()['id']}", headers=auth_header)
    assert_client_response_json(get_clients_response.json()[0], new_client)

def test_get_clients_missing_parameters(auth_header, client):
    get_clients = client.get('/clients', headers=auth_header)
    assert get_clients.status_code == 400
    assert get_clients.json()['detail'] == 'You must give at least one query parameter(client_name, client_type, client_id)'

#test "update_client"
def test_update_client(new_client, add_client, update_client, updated_client):
    add_client_response = add_client(new_client)
    assert add_client_response.status_code == 200

    updated_client['id'] = add_client_response.json()['id']
    updated_client['client_type_id'] = new_client['client_type_id']
    update_client_response = update_client(updated_client)
    assert update_client_response.status_code == 200
    assert_client_response_json(update_client_response.json(), updated_client)

def test_update_client_same_data(new_client, add_client, update_client, updated_client):
    add_client_response = add_client(new_client)
    assert add_client_response.status_code == 200

    updated_client['id'] = add_client_response.json()['id']
    updated_client['client_type_id'] = new_client['client_type_id']
    updated_client['name'] = new_client['name']
    update_client_response = update_client(updated_client)
    assert update_client_response.status_code == 400
    assert update_client_response.json()['detail'] == 'Existing client data and submitted client data same'

def test_update_client_wrong_id(update_client, updated_client):
    updated_client['id'] = 1000001
    updated_client['client_type_id'] = 1234567
    update_client_response = update_client(updated_client)
    assert update_client_response.status_code == 400
    assert update_client_response.json()['detail'] == 'Client id not found'

def test_update_client_wrong_client_type(new_client, add_client, update_client, updated_client):
    add_client_response = add_client(new_client)
    assert add_client_response.status_code == 200

    updated_client['id'] = add_client_response.json()['id']
    updated_client['client_type_id'] = 100001
    update_client_response = update_client(updated_client)
    assert update_client_response.status_code == 400
    assert update_client_response.json()['detail'] == 'Client type not found'

def test_update_client_missing_data(update_client):
    update_client_response = update_client({})
    assert update_client_response.status_code == 422

#test "delete_client"
def test_delete_client(new_client, add_client, auth_header, client):
    add_client_response = add_client(new_client)
    assert add_client_response.status_code == 200

    delete_client_response = client.delete(f"/client/{add_client_response.json()['id']}", headers=auth_header)
    assert delete_client_response.status_code == 200
    assert delete_client_response.json()['message'] == 'Client deleted'
    assert delete_client_response.json()['id'] == add_client_response.json()['id']

    get_clients_response = client.get(f"/clients?client_id={add_client_response.json()['id']}", headers=auth_header)
    assert get_clients_response.status_code == 404

def test_delete_client_wrong_id(auth_header, client):
    delete_client_response = client.delete("/client/1000001", headers=auth_header)
    assert delete_client_response.status_code == 400
    assert delete_client_response.json()['detail'] == 'Client not found'

def test_delete_client_missing_id(auth_header, client):
    delete_client_response = client.delete("/client/", headers=auth_header)
    assert delete_client_response.status_code == 405