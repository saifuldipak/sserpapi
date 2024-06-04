#helper functions
def assert_get_services_response_json(get_services_response_json, service):
    assert get_services_response_json['point'] == service['point']
    assert get_services_response_json['client_id'] == service['client_id']
    assert get_services_response_json['service_type_id'] == service['service_type_id']
    assert get_services_response_json['bandwidth'] == service['bandwidth']
    assert get_services_response_json['pop_id'] == service['pop_id']
    assert get_services_response_json['extra_info'] == service['extra_info']

#test "add_service"
def test_add_service(add_service, new_service):
    add_service_response = add_service(new_service)
    assert add_service_response.status_code == 200
    add_service_response_json = add_service_response.json()
    del(add_service_response_json['id'])
    assert add_service_response_json == new_service

def test_add_duplicate_service(add_service, new_service, add_service_only):
    add_service_response = add_service(new_service)
    assert add_service_response.status_code == 200

    add_service_only_response = add_service_only(new_service)
    assert add_service_only_response.status_code == 400
    assert add_service_only_response.json()['detail'] == 'Service exists'

def test_add_service_wrong_client_id(add_service_only, new_service):
    new_service['client_id'] = 10001
    add_service_only_response = add_service_only(new_service)
    assert add_service_only_response.status_code == 400
    assert add_service_only_response.json()['detail'] == 'Client not found'

def test_add_service_wrong_service_type_id(add_service_only, new_service, add_client, new_client):
    add_client_response = add_client(new_client)
    assert add_client_response.status_code == 200

    new_service['client_id'] = add_client_response.json()['id']
    new_service['service_type_id'] = 10001
    add_service_only_response = add_service_only(new_service)
    assert add_service_only_response.status_code == 400
    assert add_service_only_response.json()['detail'] == 'Service type not found'

def test_add_service_wrong_pop_id(add_service_only, new_service, add_client, new_client, add_service_type, new_service_type):
    add_client_response = add_client(new_client)
    assert add_client_response.status_code == 200

    add_service_type_response = add_service_type(new_service_type)
    assert add_service_type_response.status_code == 200

    new_service['client_id'] = add_client_response.json()['id']
    new_service['service_type_id'] = add_service_type_response.json()['id']
    new_service['pop_id'] = 10001
    add_service_only_response = add_service_only(new_service)
    assert add_service_only_response.status_code == 400
    assert add_service_only_response.json()['detail'] == 'Pop not found'

def test_add_service_blank_body(add_service_only):
    add_service_only_response = add_service_only({})
    assert add_service_only_response.status_code == 422

#test "get_services"
def test_get_services_by_point(add_service, new_service, client, auth_header):
    add_service_response = add_service(new_service)
    assert add_service_response.status_code == 200

    get_services_response = client.get(f"/services?service_point={add_service_response.json()['point']}", headers=auth_header)
    assert get_services_response.status_code == 200
    assert_get_services_response_json(get_services_response.json()[0], new_service)

def test_get_services_by_client_name(add_service, new_service, client, auth_header):
    add_service_response = add_service(new_service)
    assert add_service_response.status_code == 200

    get_clients_response = client.get(f"/clients?client_id={new_service['client_id']}", headers=auth_header)
    assert get_clients_response.status_code == 200

    get_services_response = client.get(f"/services?client_name={get_clients_response.json()[0]['name']}", headers=auth_header)
    assert get_services_response.status_code == 200
    assert_get_services_response_json(get_services_response.json()[0], new_service)

def test_get_services_by_pop_name(add_service, new_service, client, auth_header):
    add_service_response = add_service(new_service)
    assert add_service_response.status_code == 200

    get_pops_response = client.get(f"/pops?pop_id={new_service['pop_id']}", headers=auth_header)
    assert get_pops_response.status_code == 200

    get_services_response = client.get(f"/services?pop_name={get_pops_response.json()[0]['name']}", headers=auth_header)
    assert_get_services_response_json(get_services_response.json()[0], new_service)

def test_get_services_by_point_client_pop(add_service, new_service, client, auth_header):
    add_service_response = add_service(new_service)
    assert add_service_response.status_code == 200

    get_clients_response = client.get(f"/clients?client_id={new_service['client_id']}", headers=auth_header)
    assert get_clients_response.status_code == 200

    get_pops_response = client.get(f"/pops?pop_id={new_service['pop_id']}", headers=auth_header)
    assert get_pops_response.status_code == 200

    get_services_response = client.get(f"/services?service_point={new_service['point']}&client_name={get_clients_response.json()[0]['name']}&pop_name={get_pops_response.json()[0]['name']}", headers=auth_header)
    assert_get_services_response_json(get_services_response.json()[0], new_service)

def test_get_services_by_wrong_parameters(client, auth_header):
    get_services_response = client.get("/services?service_point=wrong_point", headers=auth_header)
    assert get_services_response.status_code == 404
    assert get_services_response.json()['detail'] == 'No service found'

    get_services_response = client.get("/services?client_name=wrong_client_name", headers=auth_header)
    assert get_services_response.status_code == 404
    assert get_services_response.json()['detail'] == 'No service found'

    get_services_response = client.get("/services?pop_name=wrong_pop_name", headers=auth_header)
    assert get_services_response.status_code == 404
    assert get_services_response.json()['detail'] == 'No service found'


#test "update_service"
def test_update_service(add_service, new_service, new_service_updated, client, auth_header):
    add_service_response = add_service(new_service)
    assert add_service_response.status_code == 200

    new_service_updated['id'] = add_service_response.json()['id']
    new_service_updated['client_id'] = add_service_response.json()['client_id']
    new_service_updated['service_type_id'] = add_service_response.json()['service_type_id']
    new_service_updated['pop_id'] = add_service_response.json()['pop_id']
    update_service_response = client.put('/service', json=new_service_updated, headers=auth_header)
    assert_get_services_response_json(update_service_response.json(), new_service_updated)

def test_update_service_by_wrong_id(new_service_updated, client, auth_header):
    update_service_response = client.put('/service', json=new_service_updated, headers=auth_header)
    assert update_service_response.status_code == 400
    assert update_service_response.json()['detail'] == 'Service not found'

def test_update_service_by_wrong_client_id(add_service, new_service, new_service_updated, client, auth_header):
    add_service_response = add_service(new_service)
    assert add_service_response.status_code == 200

    new_service_updated['id'] = add_service_response.json()['id']
    new_service_updated['client_id'] = 10001
    update_service_response = client.put('/service', json=new_service_updated, headers=auth_header)
    assert update_service_response.status_code == 400
    assert update_service_response.json()['detail'] == 'Client not found'

def test_update_service_by_wrong_service_type_id(add_service, new_service, new_service_updated, client, auth_header):
    add_service_response = add_service(new_service)
    assert add_service_response.status_code == 200

    new_service_updated['id'] = add_service_response.json()['id']
    new_service_updated['client_id'] = add_service_response.json()['client_id']
    new_service_updated['service_type_id'] = 10001
    update_service_response = client.put('/service', json=new_service_updated, headers=auth_header)
    assert update_service_response.status_code == 400
    assert update_service_response.json()['detail'] == 'Service type not found'

def test_update_service_by_wrong_pop_id(add_service, new_service, new_service_updated, client, auth_header):
    add_service_response = add_service(new_service)
    assert add_service_response.status_code == 200

    new_service_updated['id'] = add_service_response.json()['id']
    new_service_updated['client_id'] = add_service_response.json()['client_id']
    new_service_updated['service_type_id'] = add_service_response.json()['service_type_id']
    new_service_updated['pop_id'] = 10001
    update_service_response = client.put('/service', json=new_service_updated, headers=auth_header)
    assert update_service_response.status_code == 400
    assert update_service_response.json()['detail'] == 'Pop not found'

def test_update_service_blank_body(client, auth_header):
    update_service_response = client.put('/service', json={}, headers=auth_header)
    assert update_service_response.status_code == 422

def test_update_service_missing_body(client, auth_header):
    update_service_response = client.put('/service', headers=auth_header)
    assert update_service_response.status_code == 422

#test "delete_service"
def test_delete_service(add_service, new_service, client, auth_header):
    add_service_response = add_service(new_service)
    assert add_service_response.status_code == 200

    delete_service_response = client.delete(f"/service/{add_service_response.json()['id']}", headers=auth_header)
    assert delete_service_response.status_code == 200
    assert delete_service_response.json()['id'] == add_service_response.json()['id']
    assert delete_service_response.json()['message'] == 'Service deleted'

def test_delete_service_by_wrong_id(client, auth_header):
    delete_service_response = client.delete('/service/10001', headers=auth_header)
    assert delete_service_response.status_code == 400
    assert delete_service_response.json()['detail'] == 'Service not found'

def test_delete_service_missing_id(client, auth_header):
    delete_service_response = client.delete('/service', headers=auth_header)
    assert delete_service_response.status_code == 405