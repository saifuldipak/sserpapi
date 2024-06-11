#helper function
def assert_address_response(address_response_json, new_address):
    assert address_response_json['flat'] == new_address['flat']
    assert address_response_json['floor'] == new_address['floor']
    assert address_response_json['holding'] == new_address['holding']
    assert address_response_json['street'] == new_address['street']
    assert address_response_json['area'] == new_address['area']
    assert address_response_json['thana'] == new_address['thana']
    assert address_response_json['district'] == new_address['district']

#test "add_address"
def test_add_address(add_address, new_address, add_service, new_service):
    add_service_response = add_service(new_service)
    assert add_service_response.status_code == 200

    new_address['service_id'] = add_service_response.json()['id']
    add_address_response = add_address(new_address)
    assert add_address_response.status_code == 200
    assert_address_response(add_address_response.json(), new_address)

def test_add_duplicate_address(add_address, new_address, add_service, new_service):
    add_service_response = add_service(new_service)
    assert add_service_response.status_code == 200

    new_address['service_id'] = add_service_response.json()['id']
    add_address_response = add_address(new_address)
    assert add_address_response.status_code == 200

    add_duplicate_address_response = add_address(new_address)
    assert add_duplicate_address_response.status_code == 400
    assert add_duplicate_address_response.json()['detail'] == 'Address exists'

def test_add_address_missing_required_items(add_address, new_address, add_service, new_service):
    add_service_response = add_service(new_service)
    assert add_service_response.status_code == 200

    new_address['service_id'] = add_service_response.json()['id']
    del new_address['holding']
    add_address_response = add_address(new_address)
    assert add_address_response.status_code == 422

def test_add_address_missing_client_service_vendor_ids(add_address, new_address):
    add_address_response = add_address(new_address)
    assert add_address_response.status_code == 400
    assert add_address_response.json()['detail'] == 'Must provide any of client_id, service_id, or vendor_id but not more than one'

def test_add_address_wrong_client_id(new_address, add_address):
    new_address['client_id'] = 1000001
    add_address_response = add_address(new_address)
    assert add_address_response.status_code == 400
    assert add_address_response.json()['detail'] == 'Client id not found'

def test_add_address_using_client_and_vendor_id(add_vendor, new_vendor, add_client, new_client, add_address, new_address):
    add_vendor_response = add_vendor(new_vendor)
    assert add_vendor_response.status_code == 200

    add_client_response = add_client(new_client)
    assert add_client_response.status_code == 200

    new_address['vendor_id'] = add_vendor_response.json()['id']
    new_address['client_id'] = add_client_response.json()['id']
    add_address_response = add_address(new_address)
    assert add_address_response.status_code == 400
    assert add_address_response.json()['detail'] == 'Must provide any of client_id, service_id, or vendor_id but not more than one'

def test_add_address_missing_body(add_address):
    add_address_response = add_address({})
    assert add_address_response.status_code == 422

#test "get_address"
def test_get_addresses_by_client_name(add_address, new_address, add_client, new_client, auth_header, client):
    add_client_response = add_client(new_client)
    assert add_client_response.status_code == 200

    new_address['client_id'] = add_client_response.json()['id']
    add_address_response = add_address(new_address)
    assert add_address_response.status_code == 200

    get_client_response = client.get(f"/clients?client_name={add_client_response.json()['name']}", headers=auth_header)
    assert get_client_response.status_code == 200

    get_address_response = client.get(f"/addresses?client_name={get_client_response.json()[0]['name']}", headers=auth_header)
    assert get_address_response.status_code == 200
    assert_address_response(get_address_response.json()[0], new_address)

def test_get_addresses_by_some_properties(add_service, new_service, add_address, new_address, auth_header, client):
    add_service_response = add_service(new_service)
    assert add_service_response.status_code == 200

    new_address['service_id'] = add_service_response.json()['id']
    add_address_response = add_address(new_address)
    assert add_address_response.status_code == 200

    get_address_response = client.get(f"/addresses?holding={new_address['holding']}&street={new_address['street']}&area={new_address['area']}", headers=auth_header)
    assert get_address_response.status_code == 200
    assert_address_response(get_address_response.json()[0], new_address)

def test_get_addresses_by_wrong_properties(auth_header, client):
    get_address_response = client.get("/addresses?holding=something&street=somestreet&area=somewhere", headers=auth_header)
    assert get_address_response.status_code == 404

def test_get_addresses_missing_parameters(auth_header, client):
    get_address_response = client.get("/addresses", headers=auth_header)
    assert get_address_response.status_code == 400
    assert get_address_response.json()['detail'] == 'Must provide at least one search parameter'

#test "update_address"
def test_update_address_wrong_id(new_address_updated, update_address):
    new_address_updated['id'] = 1000001
    update_address_response = update_address(new_address_updated)
    assert update_address_response.status_code == 400
    assert update_address_response.json()['detail'] == 'Address not found'

def test_update_address_missing_items(new_address_updated, update_address):
    del(new_address_updated['holding'])
    update_address_response = update_address(new_address_updated)
    assert update_address_response.status_code == 422

def test_update_address_wrong_data_type(new_address_updated, update_address):
    new_address_updated['holding'] = 123
    update_address_response = update_address(new_address_updated)
    assert update_address_response.status_code == 422
    assert update_address_response.json()['detail'][0]['msg'] == 'Input should be a valid string'

def test_update_address_wrong_client_id(new_client, add_client, new_address, add_address, new_address_updated, update_address):
    add_client_response = add_client(new_client)
    assert add_client_response.status_code == 200

    new_address['client_id'] = add_client_response.json()['id']
    add_address_response = add_address(new_address)
    assert add_address_response.status_code == 200

    new_address_updated['id'] = add_address_response.json()['id']
    new_address_updated['client_id'] = 1000001
    update_address_response = update_address(new_address_updated)
    assert update_address_response.status_code == 400
    assert update_address_response.json()['detail'] == 'Client id not found'

def test_update_address_missing_body(update_address):
    update_address_response = update_address({})
    assert update_address_response.status_code == 422

def test_update_address(new_service, add_service, new_address, add_address, new_address_updated, update_address):
    add_service_response = add_service(new_service)
    assert add_service_response.status_code == 200

    new_address['service_id'] = add_service_response.json()['id']
    add_address_response = add_address(new_address)
    assert add_address_response.status_code == 200

    new_address_updated['id'] = add_address_response.json()['id']
    new_address_updated['service_id'] = add_service_response.json()['id']
    update_address_response = update_address(new_address_updated)
    assert update_address_response.status_code == 200
    assert_address_response(update_address_response.json(), new_address_updated)

#test "delete_address"
def test_delete_address_wrong_id(delete_address):
    delete_address_response = delete_address(1000001)
    assert delete_address_response.status_code == 400
    assert delete_address_response.json()['detail'] == 'Address not found'

def test_delete_address_no_id(auth_header, client):
    delete_address_response = client.delete("/address", headers=auth_header)
    assert delete_address_response.status_code == 405

def test_delete_address(new_client, add_client, new_address, add_address, delete_address):
    add_client_response = add_client(new_client)
    assert add_client_response.status_code == 200

    new_address['client_id'] = add_client_response.json()['id']
    add_address_response = add_address(new_address)
    assert add_address_response.status_code == 200

    delete_address_response = delete_address(add_address_response.json()['id'])
    assert delete_address_response.status_code == 200
    assert delete_address_response.json()['message'] == "Address deleted"
    assert delete_address_response.json()['id'] == add_address_response.json()['id']
