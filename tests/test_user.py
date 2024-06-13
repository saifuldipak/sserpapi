#helper functions
def assert_user_response(user_response_json, new_user):
    assert user_response_json['user_name'] == new_user['user_name']
    assert user_response_json['first_name'] == new_user['first_name']
    assert user_response_json['middle_name'] == new_user['middle_name']
    assert user_response_json['last_name'] == new_user['last_name']
    assert user_response_json['email'] == new_user['email']
    assert user_response_json['scope'] == new_user['scope']

#test "add_user"
def test_add_user(new_user, add_user):
    add_user_response = add_user(new_user)
    assert add_user_response.status_code == 200
    assert_user_response(add_user_response.json(), new_user)

def test_add_duplicate_user(new_user, add_user):
    add_user_response = add_user(new_user)
    assert add_user_response.status_code == 200
    add_user_response = add_user(new_user)
    assert add_user_response.status_code == 400
    assert add_user_response.json()['detail'] == 'User exists'

def test_add_user_wrong_scope(new_user, add_user):
    new_user['scope'] = 'wrong_scope'
    add_user_response = add_user(new_user)
    assert add_user_response.status_code == 422
    assert add_user_response.json()['detail'][0]['type'] == "literal_error"
    assert add_user_response.json()['detail'][0]['loc'] == ['body', 'scope']
    assert add_user_response.json()['detail'][0]['msg'] == "Input should be 'admin', 'write' or 'read'"

def test_add_user_missing_parameters(new_user, add_user):
    new_user.pop('user_name')
    add_user_response = add_user(new_user)
    assert add_user_response.status_code == 422
    assert add_user_response.json()['detail'][0]['type'] == "missing"
    assert add_user_response.json()['detail'][0]['loc'] == ['body', 'user_name']
    assert add_user_response.json()['detail'][0]['msg'] == "Field required"

def test_add_user_wrong_data_type(new_user, add_user):
    new_user['user_name'] = 123
    add_user_response = add_user(new_user)
    assert add_user_response.status_code == 422
    assert add_user_response.json()['detail'][0]['type'] == 'string_type'
    assert add_user_response.json()['detail'][0]['loc'] == ['body', 'user_name']
    assert add_user_response.json()['detail'][0]['msg'] == 'Input should be a valid string'

def test_add_user_missing_body(add_user):
    add_user_response = add_user({})
    assert add_user_response.status_code == 422

#test "get_users"
def test_get_users(new_user, add_user, client, auth_header):
    add_user_response = add_user(new_user)
    assert add_user_response.status_code == 200

    get_users_response = client.get('/users', headers=auth_header)
    assert get_users_response.status_code == 200
    assert len(get_users_response.json()) > 0

def test_get_users_by_name(new_user, add_user, client, auth_header):
    add_user_response = add_user(new_user)
    assert add_user_response.status_code == 200

    get_users_response = client.get(f"/users?user_name={new_user['user_name']}", headers=auth_header)
    assert get_users_response.status_code == 200
    assert_user_response(get_users_response.json()[0], new_user)

def test_get_users_by_name_and_status(new_user, add_user, client, auth_header):
    add_user_response = add_user(new_user)
    assert add_user_response.status_code == 200

    get_users_response = client.get(f"/users?user_name={new_user['user_name']}&disabled={new_user['disabled']}", headers=auth_header)
    assert get_users_response.status_code == 200
    assert_user_response(get_users_response.json()[0], new_user)

def test_get_users_by_name_and_scope(new_user, add_user, client, auth_header):
    add_user_response = add_user(new_user)
    assert add_user_response.status_code == 200

    get_users_response = client.get(f"/users?user_name={new_user['user_name']}&scope={new_user['scope']}", headers=auth_header)
    assert get_users_response.status_code == 200
    assert_user_response(get_users_response.json()[0], new_user)

def test_get_users_by_all_parameters(new_user, add_user, client, auth_header):
    add_user_response = add_user(new_user)
    assert add_user_response.status_code == 200

    get_users_response = client.get(f"/users?user_name={new_user['user_name']}&disabled={new_user['disabled']}&scope={new_user['scope']}", headers=auth_header)
    assert get_users_response.status_code == 200
    assert_user_response(get_users_response.json()[0], new_user)

def test_get_users_by_wrong_name(client, auth_header):
    get_users_response = client.get("/users?user_name=wrong_user_name", headers=auth_header)
    assert get_users_response.status_code == 404
    assert get_users_response.json()['detail'] == 'User not found'

def test_get_users_by_wrong_status(client, auth_header):
    get_users_response = client.get("/users?disabled=True", headers=auth_header)
    assert get_users_response.status_code == 404
    assert get_users_response.json()['detail'] == 'User not found'

def test_get_users_by_wrong_scope(client, auth_header):
    get_users_response = client.get("/users?scope=wrong_scope", headers=auth_header)
    assert get_users_response.status_code == 404
    assert get_users_response.json()['detail'] == 'User not found'

#test "update_user"
def test_update_user(new_user, add_user, new_user_updated, update_user):
    add_user_response = add_user(new_user)
    assert add_user_response.status_code == 200

    new_user_updated['id'] = add_user_response.json()['id']
    update_user_response = update_user(new_user_updated)
    assert update_user_response.status_code == 200
    assert_user_response(update_user_response.json(), new_user_updated)

def test_update_user_wrong_id(new_user_updated, update_user):
    new_user_updated['id'] = 1910091
    update_user_response = update_user(new_user_updated)
    assert update_user_response.status_code == 400
    assert update_user_response.json()['detail'] == 'User not found'

def test_update_user_wrong_scope(new_user_updated, update_user):
    new_user_updated['scope'] = 'wrong_scope'
    update_user_response = update_user(new_user_updated)
    assert update_user_response.status_code == 422
    assert update_user_response.json()['detail'][0]['type'] == "literal_error"
    assert update_user_response.json()['detail'][0]['loc'] == ['body', 'scope']
    assert update_user_response.json()['detail'][0]['msg'] == "Input should be 'admin', 'write' or 'read'"

def test_update_user_missing_parameters(new_user_updated, update_user):
    new_user_updated.pop('user_name')
    update_user_response = update_user(new_user_updated)
    assert update_user_response.status_code == 422
    assert update_user_response.json()['detail'][0]['type'] == "missing"
    assert update_user_response.json()['detail'][0]['loc'] == ['body', 'user_name']
    assert update_user_response.json()['detail'][0]['msg'] == "Field required"

def test_update_user_wrong_data_type(new_user_updated, update_user):
    new_user_updated['user_name'] = 123
    update_user_response = update_user(new_user_updated)
    assert update_user_response.status_code == 422
    assert update_user_response.json()['detail'][0]['type'] == 'string_type'
    assert update_user_response.json()['detail'][0]['loc'] == ['body', 'user_name']
    assert update_user_response.json()['detail'][0]['msg'] == 'Input should be a valid string'

def test_update_user_missing_body(update_user):
    update_user_response = update_user({})
    assert update_user_response.status_code == 422
    