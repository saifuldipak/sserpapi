def test_get_access_token(new_user, add_user, client, user_password):
    add_user_response = add_user(new_user)
    assert add_user_response.status_code == 200

    user_password['user_name'] = new_user['user_name']
    user_password['password'] = new_user['password']

    get_access_token_response = client.post('/token', data=user_password)
    assert get_access_token_response.status_code == 200

def test_get_access_token_wrong_username_password(new_user, add_user, client, user_password):
    add_user_response = add_user(new_user)
    assert add_user_response.status_code == 200

    get_access_token_response = client.post('/token', data=user_password)
    assert get_access_token_response.status_code == 401
