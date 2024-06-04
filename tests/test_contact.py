#helper function
def assert_contact_response_json(contact_response_json, contact):
    assert contact_response_json['name'] == contact['name']
    assert contact_response_json['designation'] == contact['designation']
    assert contact_response_json['type'] == contact['type']
    assert contact_response_json['phone1'] == contact['phone1']
    if contact_response_json['phone2'] is not None:
        assert contact_response_json['phone2'] == contact['phone2']
    if contact_response_json['phone3'] is not None:
        assert contact_response_json['phone3'] == contact['phone3']
    if contact_response_json['email'] is not None:
        assert contact_response_json['email'] == contact['email']
    if contact_response_json['client_id'] is not None:
        assert contact_response_json['client_id'] == contact['client_id']
    if contact_response_json['vendor_id'] is not None:
        assert contact_response_json['vendor_id'] == contact['vendor_id']
    if contact_response_json['service_id'] is not None:
        assert contact_response_json['service_id'] == contact['service_id']

#test "add_contact"
def test_add_contact(add_service, new_service, add_contact, new_contact):
    add_service_response = add_service(new_service)
    assert add_service_response.status_code == 200

    new_contact['service_id'] = add_service_response.json()['id']
    add_contact_response = add_contact(new_contact)
    assert add_contact_response.status_code == 200
    assert_contact_response_json(add_contact_response.json(), new_contact)

def test_add_duplicate_contact(add_client, new_client, add_contact, new_contact):
    add_client_response = add_client(new_client)
    assert add_client_response.status_code == 200

    new_contact['client_id'] = add_client_response.json()['id']
    add_contact_response = add_contact(new_contact)
    assert add_contact_response.status_code == 200

    add_contact_response = add_contact(new_contact)
    assert add_contact_response.status_code == 400
    assert add_contact_response.json()['detail'] == 'Contact exists'

def test_add_contact_by_wrong_data(add_contact, new_contact):
    new_contact['service_id'] = 10001
    add_contact_response = add_contact(new_contact)
    assert add_contact_response.status_code == 400
    assert add_contact_response.json()['detail'] == 'Service not found'

