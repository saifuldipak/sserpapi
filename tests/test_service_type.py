#helper functions
def assert_service_type(service_type_response, new_service_type):
    assert service_type_response.status_code == 200
    assert service_type_response.json()[0]['name'] == new_service_type['name']
    assert service_type_response.json()[0]['description'] == new_service_type['description']

#test "add_service_type"
def test_add_service_type(add_service_type, new_service_type):
    add_service_type_response = add_service_type(new_service_type)
    assert add_service_type_response.status_code == 200
    assert add_service_type_response.json()['name'] == new_service_type['name']
    assert add_service_type_response.json()['description'] == new_service_type['description']

def test_add_service_type_duplicate(add_service_type, new_service_type):
    add_service_type_response = add_service_type(new_service_type)
    assert add_service_type_response.status_code == 200

    add_service_type_duplicate_response = add_service_type(new_service_type)
    assert add_service_type_duplicate_response.status_code == 400
    assert add_service_type_duplicate_response.json()['detail'] == 'Service type exists'

def test_add_service_type_missing_body(add_service_type):
    add_service_type_response = add_service_type({})
    assert add_service_type_response.status_code == 422

#test "get_service_types"
def test_get_service_types_by_name(add_service_type, new_service_type, client, auth_header):
    add_service_type_response = add_service_type(new_service_type)
    assert add_service_type_response.status_code == 200

    get_service_types_response = client.get(f"/service/types?type_name={new_service_type['name']}", headers=auth_header)
    assert_service_type(get_service_types_response, new_service_type)

def test_get_service_types_by_id(add_service_type, new_service_type, client, auth_header):
    add_service_type_response = add_service_type(new_service_type)
    assert add_service_type_response.status_code == 200

    get_service_types_response = client.get(f"/service/types?type_id={add_service_type_response.json()['id']}", headers=auth_header)
    assert_service_type(get_service_types_response, new_service_type)

def test_get_service_types_by_wrong_name(client, auth_header):
    get_service_types_response = client.get("/service/types?type_name='wrong_name'", headers=auth_header)
    assert get_service_types_response.status_code == 404
    assert get_service_types_response.json()['detail'] == 'No service types found'

def test_get_service_types_by_wrong_id(client, auth_header):
    get_service_types_response = client.get("/service/types?type_id=10001", headers=auth_header)
    assert get_service_types_response.status_code == 404
    assert get_service_types_response.json()['detail'] == 'No service types found'

def test_get_service_types(client, auth_header, add_service_type, new_service_type):
    add_service_type_response = add_service_type(new_service_type)
    assert add_service_type_response.status_code == 200

    get_service_types_response = client.get("/service/types", headers=auth_header)
    assert get_service_types_response.status_code == 200
    assert len(get_service_types_response.json()) > 0

#test "delete_service_type"
def test_delete_service_type(add_service_type, new_service_type, client, auth_header):
    add_service_type_response = add_service_type(new_service_type)
    assert add_service_type_response.status_code == 200

    delete_service_type_response = client.delete(f"/service/type/{add_service_type_response.json()['id']}", headers=auth_header)
    assert delete_service_type_response.status_code == 200
    assert delete_service_type_response.json()['message'] == 'Service type deleted'
    assert delete_service_type_response.json()['id'] == add_service_type_response.json()['id']

def test_delete_service_type_wrong_id(client, auth_header):
    delete_service_type_response = client.delete("/service/type/10001", headers=auth_header)
    assert delete_service_type_response.status_code == 400
    assert delete_service_type_response.json()['detail'] == 'Service type not found'

def test_delete_service_type_missing_id(client, auth_header):
    delete_service_type_response = client.delete("/service/type", headers=auth_header)
    assert delete_service_type_response.status_code == 422
