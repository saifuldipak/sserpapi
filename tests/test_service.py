#test "add_service"
def test_add_service(add_service, new_service):
    add_service_response = add_service(new_service)
    assert add_service_response.status_code == 200
    add_service_response_json = add_service_response.json()
    del(add_service_response_json['id'])
    assert add_service_response_json == new_service

#test "add_service_wrong_data"
def test_add_duplicate_service(add_service, new_service, add_service_only):
    add_service_response = add_service(new_service)
    assert add_service_response.status_code == 200

    add_service_only_response = add_service_only(new_service)
    assert add_service_only_response.status_code == 400
    assert add_service_only_response.json()['detail'] == 'Service exists'