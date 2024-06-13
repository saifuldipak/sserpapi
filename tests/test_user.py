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

def test_get_users_by_all_parameters(new_user, add_user, client, auth_header):
    add_user_response = add_user(new_user)
    assert add_user_response.status_code == 200

    get_users_response = client.get(f"/users?user_name={new_user['user_name']}&disabled={new_user['disabled']}&scope={new_user['scope']}", headers=auth_header)
    assert get_users_response.status_code == 200
    assert_user_response(get_users_response.json()[0], new_user)