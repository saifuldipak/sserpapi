#helper functions
def assert_pop_response(pop_response_json: dict, pop: dict, vendor: dict | None = None) -> None:
    assert pop_response_json['name'] == pop['name']
    assert pop_response_json['owner'] == pop['owner']
    assert pop_response_json['extra_info'] == pop['extra_info']
    if vendor:
        assert pop_response_json['vendors']['name'] == vendor['name']
        assert pop_response_json['vendors']['type'] == vendor['type']

#test add_pop
def test_add_pop(add_pop, new_pop, new_vendor):
    add_pop_response = add_pop(new_pop, new_vendor)
    assert add_pop_response.status_code == 200

    add_pop_response_json = add_pop_response.json()
    del (add_pop_response_json['id'])
    assert_pop_response(add_pop_response_json, new_pop)

def test_add_duplicate_pop(add_vendor, new_vendor, add_pop_only, new_pop):
    add_vendor_response = add_vendor(new_vendor)
    assert add_vendor_response.status_code == 200
    
    new_pop['owner'] = add_vendor_response.json()['id']
    add_pop_response = add_pop_only(new_pop)
    assert add_pop_response.status_code == 200

    add_duplicate_pop_response = add_pop_only(new_pop)
    assert add_duplicate_pop_response.status_code == 400
    assert add_duplicate_pop_response.json()['detail'] == 'Pop exists'

def test_add_pop_wrong_vendor_id(add_pop_only, new_pop):
    new_pop['owner'] = 1000019
    add_pop_only_response = add_pop_only(new_pop)
    assert add_pop_only_response.status_code == 400
    assert add_pop_only_response.json()['detail'] == 'Vendor id not found'

def test_add_pop_missing_parameters(add_pop_only, new_pop):
    add_pop_response = add_pop_only(new_pop)
    assert add_pop_response.status_code == 422    

def test_add_pop_wrong_data_type(add_pop_only, new_pop):
    new_pop['owner'] = 'test'
    add_pop_only_response = add_pop_only(new_pop)
    assert add_pop_only_response.status_code == 422
    assert add_pop_only_response.json()['detail'][0]['msg'] == 'Input should be a valid integer, unable to parse string as an integer'

def test_add_pop_missing_body(auth_header, client):
    add_pop_response = client.post('/pop', headers=auth_header)
    assert add_pop_response.status_code == 422

#test get_pops
def test_get_pops_by_name(add_pop, new_pop, new_vendor, client, auth_header):
    add_pop_response = add_pop(new_pop, new_vendor)
    assert add_pop_response.status_code == 200

    get_pops_response = client.get(f"/pops?pop_name={new_pop['name']}", headers=auth_header)
    assert_pop_response(get_pops_response.json()[0], new_pop, new_vendor)

def test_get_pops_by_partial_name(add_pop, new_pop, new_vendor, client, auth_header):
    add_pop_response = add_pop(new_pop, new_vendor)
    assert add_pop_response.status_code == 200

    partial_pop_name = new_pop['name'][:3]
    get_pops_response = client.get(f"/pops?pop_name={partial_pop_name}", headers=auth_header)
    assert_pop_response(get_pops_response.json()[0], new_pop, new_vendor)

def test_get_pops_by_vendor_name(add_pop, new_pop, new_vendor, client, auth_header):
    add_pop_response  = add_pop(new_pop, new_vendor)
    assert add_pop_response.status_code == 200

    get_vendors_response = client.get(f"/vendors?vendor_id={new_pop['owner']}", headers=auth_header)
    assert get_vendors_response.status_code == 200

    get_pops_response = client.get(f"/pops?pop_owner={get_vendors_response.json()[0]['name']}", headers=auth_header)
    assert_pop_response(get_pops_response.json()[0], new_pop, new_vendor)

def test_get_pops_by_wrong_name_and_owner(client, auth_header):
    get_pops_response = client.get("/pops?pop_name='wrong_name'&pop_owner='wrong_owner'", headers=auth_header)
    assert get_pops_response.status_code == 404

def test_get_pops_missing_parameters(client, auth_header):
    get_pops_response = client.get("/pops", headers=auth_header)
    assert get_pops_response.status_code == 400

#test update_pop
def test_update_pop(add_pop, new_pop, new_vendor, new_pop_updated, update_pop):
    add_pop_response = add_pop(new_pop, new_vendor)
    assert add_pop_response.status_code == 200

    new_pop_updated['id'] = add_pop_response.json()['id']
    new_pop_updated['owner'] = add_pop_response.json()['owner']
    update_pop_response = update_pop(new_pop_updated)
    assert update_pop_response.status_code == 200
    assert_pop_response(update_pop_response.json(), new_pop_updated)

def test_update_pop_wrong_id(new_pop_updated, update_pop):
    new_pop_updated['id'] = 10001
    new_pop_updated['owner'] = 191901
    update_pop_response = update_pop(new_pop_updated)
    assert update_pop_response.status_code == 400
    assert update_pop_response.json()['detail'] == 'Pop not found'

def test_update_pop_wrong_vendor_id(new_pop, new_vendor, add_pop, new_pop_updated, update_pop):
    add_pop_response = add_pop(new_pop, new_vendor)
    assert add_pop_response.status_code == 200

    new_pop_updated['id'] = add_pop_response.json()['id']
    new_pop_updated['owner'] = 1009101
    update_pop_response = update_pop(new_pop_updated)
    assert update_pop_response.status_code == 400
    assert update_pop_response.json()['detail'] == 'Vendor not found'

def test_update_pop_missing_body(client, auth_header):
    update_pop_response = client.put("/pop", headers=auth_header)
    assert update_pop_response.status_code == 422

#test delete_pop
def test_delete_pop(auth_header, client, new_vendor, new_pop, add_pop):
    add_pop_response  = add_pop(new_pop, new_vendor)
    assert add_pop_response.status_code == 200

    delete_pop_response = client.delete(f"/pop/{add_pop_response.json()['id']}", headers=auth_header)
    assert delete_pop_response.status_code == 200
    assert delete_pop_response.json()['message'] == 'Pop deleted'
    assert delete_pop_response.json()['id'] == add_pop_response.json()['id']

    get_pops_response = client.get(f"/pops?pop_name={new_pop['name']}", headers=auth_header)
    assert get_pops_response.status_code == 404

def test_delete_pop_with_active_services(new_service, add_service, client, auth_header):
    add_service_response = add_service(new_service)
    assert add_service_response.status_code == 200

    delete_pop_response = client.delete(f"/pop/{add_service_response.json()['pop_id']}", headers=auth_header)
    assert delete_pop_response.status_code == 400
    assert delete_pop_response.json()['detail'] == 'Cannot delete pop with active services'

def test_delete_pop_wrong_id(auth_header, client):
    delete_vendor_response = client.delete('/pop/10001', headers=auth_header)
    assert delete_vendor_response.status_code == 400
    assert delete_vendor_response.json()['detail'] == 'Pop not found'

def test_delete_pop_missing_id(auth_header, client):
    delete_pop_missing_id = client.delete('/vendor/', headers=auth_header)
    assert delete_pop_missing_id.status_code == 405
