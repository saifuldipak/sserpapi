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