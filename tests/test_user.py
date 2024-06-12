#helper functions
def assert_user_response(user_response_json, new_user):
    assert user_response_json['user_name'] == new_user['user_name']
    assert user_response_json['first_name'] == new_user['first_name']
    assert user_response_json['middle_name'] == new_user['middle_name']
    assert user_response_json['last_name'] == new_user['last_name']
    assert user_response_json['email'] == new_user['email']
    assert user_response_json['scope'] == new_user['scope']

def test_add_user(new_user, add_user):
    add_user_response = add_user(new_user)
    assert add_user_response.status_code == 200
    assert_user_response(add_user_response.json(), new_user)
