def assert_get_client_types_response(get_client_types_response, client_type):
    assert get_client_types_response.status_code == 200
    assert get_client_types_response.json()[0]['name'] == client_type['name']

def test_add_client_type(new_client_type, add_client_type):
    add_client_type_response = add_client_type(new_client_type)
    assert add_client_type_response.status_code == 200
    assert add_client_type_response.json()['name'] == new_client_type['name']

def test_add_duplicate_client_type(new_client_type, add_client_type, auth_header):
    add_client_type_response = add_client_type(new_client_type)
    assert add_client_type_response.status_code == 200

    add_duplicate_client_type_response = add_client_type(new_client_type)
    assert add_duplicate_client_type_response.status_code == 400
    assert add_duplicate_client_type_response.json()['detail'] == 'Client type exists'

def test_add_client_type_blank_data(auth_header, client):
    add_client_type_missing_data = client.post('/client', json={}, headers=auth_header)
    assert add_client_type_missing_data.status_code == 422

def test_add_client_type_missing_body(auth_header, client):
    add_client_type_missing_body = client.post('/client', headers=auth_header)
    assert add_client_type_missing_body.status_code == 422

def test_get_client_type_by_name(new_client_type, auth_header, client, add_client_type):
    add_client_type_response = add_client_type(new_client_type)
    assert add_client_type_response.status_code == 200

    get_client_types_response = client.get(f"/client/types?type_name={new_client_type['name']}", headers=auth_header)
    assert_get_client_types_response(get_client_types_response, new_client_type)

def test_get_client_type_by_partial_name(new_client_type, auth_header, client, add_client_type):
    add_client_type_response = add_client_type(new_client_type)
    assert add_client_type_response.status_code == 200

    partial_client_type_name = new_client_type['name'][:3]
    get_client_types_response = client.get(f"/client/types?type_name={partial_client_type_name}", headers=auth_header)
    assert_get_client_types_response(get_client_types_response, new_client_type)

def test_get_client_type_by_id(new_client_type, auth_header, client, add_client_type):
    add_client_type_response = add_client_type(new_client_type)
    assert add_client_type_response.status_code == 200

    get_client_types_response = client.get(f"/client/types?type_id={add_client_type_response.json()['id']}", headers=auth_header)
    assert_get_client_types_response(get_client_types_response, new_client_type)


def test_get_client_type_by_wrong_name(new_client_type, auth_header, client, add_client_type):
    add_client_type_response = add_client_type(new_client_type)
    assert add_client_type_response.status_code == 200

    get_client_types = client.get("/client/types?type_name='wrong_name'", headers=auth_header)
    assert get_client_types.status_code == 404

def test_get_client_type_list(new_client_type, another_new_client_type, auth_header, client, add_client_type):
    add_client_type_response = add_client_type(new_client_type)
    assert add_client_type_response.status_code == 200

    add_another_client_type_response = add_client_type(another_new_client_type)
    assert add_another_client_type_response.status_code == 200

    get_client_types = client.get('/client/types', headers=auth_header)
    assert get_client_types.status_code == 200
    assert len(get_client_types.json()) == 2
    assert get_client_types.json()[0]['name'] == new_client_type['name']
    assert get_client_types.json()[1]['name'] == another_new_client_type['name']

def test_delete_client_type(new_client_type, auth_header, client, add_client_type):
    add_client_type_response = add_client_type(new_client_type)
    assert add_client_type_response.status_code == 200

    delete_client_type = client.delete(f'/client/type/{add_client_type_response.json()["id"]}', headers=auth_header)
    assert delete_client_type.status_code == 200
    assert delete_client_type.json()['message'] == 'Client type deleted'

def test_delete_client_type_wrong_id(auth_header, client):
    delete_client_type_wrong_id = client.delete('/client/type/0', headers=auth_header)
    assert delete_client_type_wrong_id.status_code == 400
    assert delete_client_type_wrong_id.json()['detail'] == 'Client type not found'

def test_delete_client_type_missing_id(auth_header, client):
    delete_client_type_missing_id = client.delete('/client/type/', headers=auth_header)
    assert delete_client_type_missing_id.status_code == 422

def test_delete_client_type_with_client(new_client_type, auth_header, client, add_client_type, new_client, add_client):
    add_client_type_response = add_client_type(new_client_type)
    assert add_client_type_response.status_code == 200

    new_client['client_type_id'] = add_client_type_response.json()['id']
    add_client_response = add_client(new_client)
    assert add_client_response.status_code == 200

    delete_client_type = client.delete(f'/client/type/{add_client_type_response.json()["id"]}', headers=auth_header)
    assert delete_client_type.status_code == 400
    assert delete_client_type.json()['detail'] == 'Cannot delete client type with active clients'