#helper function
def assert_contact_response_json(contact_response_json, contact, name = None):
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
        if name:
            assert contact_response_json['clients']['name'] == name
    if contact_response_json['vendor_id'] is not None:
        assert contact_response_json['vendor_id'] == contact['vendor_id']
        if name:
            assert contact_response_json['vendors']['name'] == name
    if contact_response_json['service_id'] is not None:
        assert contact_response_json['service_id'] == contact['service_id']
        if name:
            assert contact_response_json['services']['point'] == name

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
    assert add_contact_response.json()['detail'] == 'Service id not found'

def test_add_contact_missing_body(add_contact):
    add_contact_response = add_contact({})
    assert add_contact_response.status_code == 422

#test "get_contacts"
def test_get_contacts_by_id(add_service, new_service, add_contact, new_contact, client, auth_header):
    add_service_response = add_service(new_service)
    assert add_service_response.status_code == 200
    
    new_contact['service_id'] = add_service_response.json()['id']
    add_contact_response = add_contact(new_contact)
    assert add_contact_response.status_code == 200

    get_contacts_response = client.get(f"/contacts?contact_id={add_contact_response.json()['id']}", headers=auth_header)
    assert get_contacts_response.status_code == 200
    assert_contact_response_json(get_contacts_response.json()[0], new_contact, add_service_response.json()['point'])

def test_get_contacts_by_name(add_vendor, new_vendor, add_contact, new_contact, client, auth_header):
    add_vendor_response = add_vendor(new_vendor)
    assert add_vendor_response.status_code == 200
    
    new_contact['vendor_id'] = add_vendor_response.json()['id']
    add_contact_response = add_contact(new_contact)
    assert add_contact_response.status_code == 200

    get_contacts_response = client.get(f"/contacts?contact_name={new_contact['name']}", headers=auth_header)
    assert get_contacts_response.status_code == 200
    assert_contact_response_json(get_contacts_response.json()[0], new_contact, add_vendor_response.json()['name'])

def test_get_contacts_by_designation(add_service, new_service, add_contact, new_contact, client, auth_header):
    add_service_response = add_service(new_service)
    assert add_service_response.status_code == 200
    
    new_contact['service_id'] = add_service_response.json()['id']
    add_contact_response = add_contact(new_contact)
    assert add_contact_response.status_code == 200

    get_contacts_response = client.get(f"/contacts?designation={new_contact['designation']}&service_id={new_contact['service_id']}", headers=auth_header)
    assert get_contacts_response.status_code == 200
    assert_contact_response_json(get_contacts_response.json()[0], new_contact, add_service_response.json()['point'])

def test_get_contacts_by_type(add_client, new_client, add_contact, new_contact, client, auth_header):
    add_client_response = add_client(new_client)
    assert add_client_response.status_code == 200
    
    new_contact['client_id'] = add_client_response.json()['id']
    add_contact_response = add_contact(new_contact)
    assert add_contact_response.status_code == 200

    get_contacts_response = client.get(f"/contacts?type={new_contact['type']}&client_id={new_contact['client_id']}", headers=auth_header)
    assert get_contacts_response.status_code == 200
    assert_contact_response_json(get_contacts_response.json()[0], new_contact, add_client_response.json()['name'])

def test_get_contacts_by_phone1(add_client, new_client, add_contact, new_contact, client, auth_header):
    add_client_response = add_client(new_client)
    assert add_client_response.status_code == 200
    
    new_contact['client_id'] = add_client_response.json()['id']
    add_contact_response = add_contact(new_contact)
    assert add_contact_response.status_code == 200

    get_contacts_response = client.get(f"/contacts?phone1={new_contact['phone1']}", headers=auth_header)
    assert get_contacts_response.status_code == 200
    assert_contact_response_json(get_contacts_response.json()[0], new_contact, add_client_response.json()['name'])

def test_get_contacts_by_email(add_client, new_client, add_contact, new_contact, client, auth_header):
    add_client_response = add_client(new_client)
    assert add_client_response.status_code == 200
    
    new_contact['client_id'] = add_client_response.json()['id']
    add_contact_response = add_contact(new_contact)
    assert add_contact_response.status_code == 200

    get_contacts_response = client.get(f"/contacts?email={new_contact['email']}", headers=auth_header)
    assert get_contacts_response.status_code == 200
    assert_contact_response_json(get_contacts_response.json()[0], new_contact, add_client_response.json()['name'])

def test_get_contacts_by_client_id(add_client, new_client, add_contact, new_contact, client, auth_header):
    add_client_response = add_client(new_client)
    assert add_client_response.status_code == 200
    
    new_contact['client_id'] = add_client_response.json()['id']
    add_contact_response = add_contact(new_contact)
    assert add_contact_response.status_code == 200

    get_contacts_response = client.get(f"/contacts?client_id={new_contact['client_id']}", headers=auth_header)
    assert get_contacts_response.status_code == 200
    assert_contact_response_json(get_contacts_response.json()[0], new_contact, add_client_response.json()['name'])

def test_get_contacts_by_service_id(add_service, new_service, add_contact, new_contact, client, auth_header):
    add_service_response = add_service(new_service)
    assert add_service_response.status_code == 200
    
    new_contact['service_id'] = add_service_response.json()['id']
    add_contact_response = add_contact(new_contact)
    assert add_contact_response.status_code == 200

    get_contacts_response = client.get(f"/contacts?service_id={new_contact['service_id']}", headers=auth_header)
    assert get_contacts_response.status_code == 200
    assert_contact_response_json(get_contacts_response.json()[0], new_contact, add_service_response.json()['point'])

def test_get_contacts_by_vendor_id(add_vendor, new_vendor, add_contact, new_contact, client, auth_header):
    add_vendor_response = add_vendor(new_vendor)
    assert add_vendor_response.status_code == 200
    
    new_contact['vendor_id'] = add_vendor_response.json()['id']
    add_contact_response = add_contact(new_contact)
    assert add_contact_response.status_code == 200

    get_contacts_response = client.get(f"/contacts?vendor_id={new_contact['vendor_id']}", headers=auth_header)
    assert get_contacts_response.status_code == 200
    assert_contact_response_json(get_contacts_response.json()[0], new_contact, add_vendor_response.json()['name'])

def test_get_contacts_by_client_name(add_client, new_client, add_contact, new_contact, client, auth_header):
    add_client_response = add_client(new_client)
    assert add_client_response.status_code == 200
    
    new_contact['client_id'] = add_client_response.json()['id']
    add_contact_response = add_contact(new_contact)
    assert add_contact_response.status_code == 200

    get_contacts_response = client.get(f"/contacts?client_name={add_client_response.json()['name']}", headers=auth_header)
    assert get_contacts_response.status_code == 200
    assert_contact_response_json(get_contacts_response.json()[0], new_contact, add_client_response.json()['name'])

def test_get_contacts_by_vendor_name(add_vendor, new_vendor, add_contact, new_contact, client, auth_header):
    add_vendor_response = add_vendor(new_vendor)
    assert add_vendor_response.status_code == 200
    
    new_contact['vendor_id'] = add_vendor_response.json()['id']
    add_contact_response = add_contact(new_contact)
    assert add_contact_response.status_code == 200

    get_contacts_response = client.get(f"/contacts?vendor_name={add_vendor_response.json()['name']}", headers=auth_header)
    assert get_contacts_response.status_code == 200
    assert_contact_response_json(get_contacts_response.json()[0], new_contact, add_vendor_response.json()['name'])

def test_get_contacts_by_service_point(add_service, new_service, add_contact, new_contact, client, auth_header):
    add_service_response = add_service(new_service)
    assert add_service_response.status_code == 200
    
    new_contact['service_id'] = add_service_response.json()['id']
    add_contact_response = add_contact(new_contact)
    assert add_contact_response.status_code == 200

    get_clients_response = client.get(f"/clients?client_id={add_service_response.json()['client_id']}", headers=auth_header)
    assert get_clients_response.status_code == 200

    get_contacts_response = client.get(f"/contacts?service_point={add_service_response.json()['point']}&client_name={get_clients_response.json()[0]['name']}", headers=auth_header)
    assert get_contacts_response.status_code == 200
    assert_contact_response_json(get_contacts_response.json()[0], new_contact, add_service_response.json()['point'])

def test_get_contacts_missing_parameters(client, auth_header):
    get_contacts_response = client.get("/contacts", headers=auth_header)
    assert get_contacts_response.status_code == 400
    assert get_contacts_response.json()['detail'] == 'No query parameters'

def test_get_contacts_by_designation_or_type_missing_parameters(client, auth_header):
    get_contacts_response = client.get("/contacts?designation=some_designation", headers=auth_header)
    assert get_contacts_response.status_code == 400
    assert get_contacts_response.json()['detail'] == 'Must give at least one query parameter(client_id, service_id, vendor_id, client_name, service_point, vendor_name) when designation or contact_type is provided'

def test_get_contacts_by_client_service_vendor_ids(client, auth_header):
    get_contacts_response = client.get("/contacts?client_id=1&service_id=1&vendor_id=1", headers=auth_header)
    assert get_contacts_response.status_code == 400
    assert get_contacts_response.json()['detail'] == 'client_id, service_id, and vendor_id cannot be provided at the same time'

def test_get_contacts_by_client_name_and_vendor_name(client, auth_header):
    get_contacts_response = client.get("/contacts?client_name=client_name&vendor_name=vendor_name", headers=auth_header)
    assert get_contacts_response.status_code == 400
    assert get_contacts_response.json()['detail'] == 'client_name and vendor_name cannot be provided at the same time'

def test_get_contacts_by_service_id_and_service_point(client, auth_header):
    get_contacts_response = client.get("/contacts?service_id=1100&service_point=service_point", headers=auth_header)
    assert get_contacts_response.status_code == 400
    assert get_contacts_response.json()['detail'] == 'service_id and service_point both cannot be provided at the same time'

def test_get_contacts_by_client_id_and_client_name(client, auth_header):
    get_contacts_response = client.get("/contacts?client_id=1100&client_name=client_name", headers=auth_header)
    assert get_contacts_response.status_code == 400
    assert get_contacts_response.json()['detail'] == 'client_id and client_name both cannot be provided at the same time'

def test_get_contacts_by_vendor_id_and_vendor_name(client, auth_header):
    get_contacts_response = client.get("/contacts?vendor_id=1100&vendor_name=vendor_name", headers=auth_header)
    assert get_contacts_response.status_code == 400
    assert get_contacts_response.json()['detail'] == 'vendor_id and vendor_name both cannot be provided at the same time'

def test_get_contacts_by_designation_and_contact_type_missing_ids(client, auth_header):
    get_contacts_response = client.get("/contacts?designation=designation&contact_type=Technical", headers=auth_header)
    assert get_contacts_response.status_code == 400
    assert get_contacts_response.json()['detail'] == 'Must give at least one query parameter(client_id, service_id, vendor_id, client_name, service_point, vendor_name) when designation or contact_type is provided'

def test_get_contacts_by_service_point_missing_client_name(client, auth_header):
    get_contacts_response = client.get("/contacts?service_point=service_point", headers=auth_header)
    assert get_contacts_response.status_code == 400
    assert get_contacts_response.json()['detail'] == 'Must give query parameter client_name when service_name is provided'

#test "update_contact"
def test_update_contact(add_client, new_client, add_contact, new_contact, new_contact_updated, client, auth_header):
    add_client_response = add_client(new_client)
    assert add_client_response.status_code == 200
    
    new_contact['client_id'] = add_client_response.json()['id']
    add_contact_response = add_contact(new_contact)
    assert add_contact_response.status_code == 200

    new_contact_updated['id'] = add_contact_response.json()['id']
    new_contact_updated['client_id'] = add_contact_response.json()['client_id']
    update_contact_response = client.put("/contact", json=new_contact_updated, headers=auth_header)
    assert update_contact_response.status_code == 200
    assert_contact_response_json(update_contact_response.json(), new_contact_updated)

def test_update_contact_missing_id(new_contact_updated, client, auth_header):
    new_contact_updated['id'] = 10010
    new_contact_updated['client_id'] = 1290
    update_contact_response = client.put("/contact", json=new_contact_updated, headers=auth_header)
    assert update_contact_response.status_code == 400
    assert update_contact_response.json()['detail'] == 'Contact not found'

def test_update_contact_wrong_client_id(add_client, new_client, add_contact, new_contact, new_contact_updated, client, auth_header):
    add_client_response = add_client(new_client)
    assert add_client_response.status_code == 200

    new_contact['client_id'] = add_client_response.json()['id']
    add_contact_response = add_contact(new_contact)
    assert add_contact_response.status_code == 200

    new_contact_updated['id'] = add_contact_response.json()['id']
    new_contact_updated['client_id'] = 1290
    update_contact_response = client.put("/contact", json=new_contact_updated, headers=auth_header)
    assert update_contact_response.status_code == 400
    assert update_contact_response.json()['detail'] == 'Client id not found'

def test_update_contact_wrong_phone_number(add_client, new_client, add_contact, new_contact, new_contact_updated, client, auth_header):
    add_client_response = add_client(new_client)
    assert add_client_response.status_code == 200

    new_contact['client_id'] = add_client_response.json()['id']
    add_contact_response = add_contact(new_contact)
    assert add_contact_response.status_code == 200

    new_contact_updated['id'] = add_contact_response.json()['id']
    new_contact_updated['client_id'] = add_contact_response.json()['client_id']
    new_contact_updated['phone1'] = '0171342290123'
    update_contact_response = client.put("/contact", json=new_contact_updated, headers=auth_header)
    assert update_contact_response.status_code == 400
    assert update_contact_response.json()['detail'] == f"{new_contact_updated['phone1']} - Phone number must be 11 digits"
 
def test_update_contact_missing_body(client, auth_header):
    update_contact_response = client.put("/contact", headers=auth_header)
    assert update_contact_response.status_code == 422

def test_update_contact_blank_body(client, auth_header):
    update_contact_response = client.put("/contact", json={}, headers=auth_header)
    assert update_contact_response.status_code == 422

#test "delete_contact"
def test_delete_contact(add_client, new_client, add_contact, new_contact, client, auth_header):
    add_client_response = add_client(new_client)
    assert add_client_response.status_code == 200
    
    new_contact['client_id'] = add_client_response.json()['id']
    add_contact_response = add_contact(new_contact)
    assert add_contact_response.status_code == 200

    delete_contact_response = client.delete(f"/contact/{add_contact_response.json()['id']}", headers=auth_header)
    assert delete_contact_response.status_code == 200

def test_delete_contact_wrong_id(client, auth_header):
    delete_contact_response = client.delete("/contact/10010", headers=auth_header)
    assert delete_contact_response.status_code == 400
    assert delete_contact_response.json()['detail'] == 'Contact not found'

def test_delete_contact_missing_id(client, auth_header):
    delete_contact_response = client.delete("/contact/", headers=auth_header)
    assert delete_contact_response.status_code == 405