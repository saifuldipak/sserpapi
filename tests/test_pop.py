#helper functions
def assert_get_pops_response(get_pops_response, pop, vendor):
    assert get_pops_response.status_code == 200
    assert get_pops_response.json()[0]['name'] == pop['name']
    assert get_pops_response.json()[0]['owner'] == pop['owner']
    assert get_pops_response.json()[0]['extra_info'] == pop['extra_info']
    assert get_pops_response.json()[0]['vendors']['name'] == vendor['name']
    assert get_pops_response.json()[0]['vendors']['type'] == vendor['type']

#test add_pop
def test_add_pop(add_vendor_and_pop, new_pop):
    add_pop_response = add_vendor_and_pop
    assert add_pop_response.status_code == 200
    add_pop_response_json = add_pop_response.json()
    del (add_pop_response_json['id'])
    assert add_pop_response_json == new_pop

def test_add_duplicate_pop(add_vendor, new_vendor, add_pop, new_pop):
    add_vendor_response = add_vendor(new_vendor)
    assert add_vendor_response.status_code == 200
    
    new_pop['owner'] = add_vendor_response.json()['id']
    add_pop_response = add_pop(new_pop)
    assert add_pop_response.status_code == 200

    add_duplicate_pop_response = add_pop(new_pop)
    assert add_duplicate_pop_response.status_code == 400
    assert add_duplicate_pop_response.json()['detail'] == 'Pop exists'

def test_add_pop_blank_data(add_pop):
    add_pop_response = add_pop({})
    assert add_pop_response.status_code == 422

def test_add_pop_missing_body(add_pop):
    add_pop_response = add_pop(None)
    assert add_pop_response.status_code == 422

#test get_pops
def test_get_pops_by_name(add_vendor_and_pop, client, auth_header, new_pop, new_vendor):
    add_pop_response = add_vendor_and_pop
    assert add_pop_response.status_code == 200

    get_pops_response = client.get(f"/pops?pop_name={new_pop['name']}", headers=auth_header)
    assert_get_pops_response(get_pops_response, new_pop, new_vendor)

def test_get_pops_by_partial_name(add_vendor_and_pop, client, auth_header, new_pop, new_vendor):
    add_pop_response = add_vendor_and_pop
    assert add_pop_response.status_code == 200

    partial_pop_name = new_pop['name'][:3]
    get_pops_response = client.get(f"/pops?pop_name={partial_pop_name}", headers=auth_header)
    assert_get_pops_response(get_pops_response, new_pop, new_vendor)

def test_get_pops_by_owner(add_vendor_and_pop, client, auth_header, new_pop, new_vendor):
    add_pop_response  = add_vendor_and_pop
    assert add_pop_response.status_code == 200

    get_vendors_response = client.get(f"/vendors?vendor_id={new_pop['owner']}", headers=auth_header)
    assert get_vendors_response.status_code == 200

    get_pops_response = client.get(f"/pops?pop_owner={get_vendors_response.json()[0]['name']}", headers=auth_header)
    assert_get_pops_response(get_pops_response, new_pop, new_vendor)

def test_get_pops_by_wrong_name(client, auth_header):
    get_pops_response = client.get("/pops?pop_name='wrong_name'", headers=auth_header)
    assert get_pops_response.status_code == 404

def test_get_pops_by_wrong_owner(client, auth_header):
    get_pops_response = client.get("/pops?pop_owner='wrong_owner'", headers=auth_header)
    assert get_pops_response.status_code == 404

def test_get_pops_missing_parameters(client, auth_header):
    get_pops_response = client.get("/pops", headers=auth_header)
    assert get_pops_response.status_code == 400

#test update_pop
def test_update_pop(add_vendor_and_pop, client, auth_header, updated_pop):
    add_pop_response = add_vendor_and_pop
    assert add_pop_response.status_code == 200

    updated_pop['id'] = add_pop_response.json()['id']
    updated_pop['owner'] = add_pop_response.json()['owner']
    update_pop_response = client.put("/pop", json=updated_pop, headers=auth_header)
    assert update_pop_response.status_code == 200
    assert update_pop_response.json() == updated_pop

def test_update_pop_wrong_id(add_vendor_and_pop, client, auth_header, updated_pop):
    add_pop_response  = add_vendor_and_pop
    assert add_pop_response.status_code == 200

    updated_pop['id'] = 10001
    update_pop_response = client.put("/pop", json=updated_pop, headers=auth_header)
    assert update_pop_response.status_code == 400
    assert update_pop_response.json()['detail'] == 'Pop not found'

def test_update_pop_missing_body(add_vendor_and_pop, client, auth_header):
    add_pop_response  = add_vendor_and_pop
    assert add_pop_response.status_code == 200

    update_pop_response = client.put("/pop", json={}, headers=auth_header)
    assert update_pop_response.status_code == 422

#test delete_pop
def test_delete_pop(auth_header, client, add_vendor_and_pop):
    add_pop_response  = add_vendor_and_pop
    assert add_pop_response.status_code == 200

    delete_pop_response = client.delete(f"/pop/{add_pop_response.json()['id']}", headers=auth_header)
    assert delete_pop_response.status_code == 200
    assert delete_pop_response.json()['message'] == 'Pop deleted'
    assert delete_pop_response.json()['id'] == add_pop_response.json()['id']

def test_delete_pop_wrong_id(auth_header, client):
    delete_vendor_response = client.delete('/vendor/10001', headers=auth_header)
    assert delete_vendor_response.status_code == 400
    assert delete_vendor_response.json()['detail'] == 'Vendor not found'

def test_delete_pop_missing_id(auth_header, client):
    delete_pop_missing_id = client.delete('/vendor/', headers=auth_header)
    assert delete_pop_missing_id.status_code == 405
