import pytest

@pytest.fixture
def new_vendor():
    return {'name': 'test_vendor', 'type': 'LSP'}

@pytest.fixture
def add_vendor(auth_header, client):
    def _add_vendor(vendor: dict):
        add_vendor_response = client.post('/vendor', json=vendor, headers=auth_header)
        return add_vendor_response
    return _add_vendor

def test_add_vendor(add_vendor, new_vendor):
    add_vendor_response = add_vendor(new_vendor)
    assert add_vendor_response.status_code == 200
    assert add_vendor_response.json()['name'] == new_vendor['name']
    assert add_vendor_response.json()['type'] == new_vendor['type']

def test_add_duplicate_vendor(add_vendor, new_vendor):
    add_vendor_response = add_vendor(new_vendor)
    assert add_vendor_response.status_code == 200

    add_duplicate_vendor_response = add_vendor(new_vendor)
    assert add_duplicate_vendor_response.status_code == 400
    assert add_duplicate_vendor_response.json()['detail'] == 'Vendor exists'

def test_add_vendor_blank_data(add_vendor):
    add_vendor_response = add_vendor({})
    assert add_vendor_response.status_code == 422

def test_add_vendor_missing_body(add_vendor):
    add_vendor_response = add_vendor(None)
    assert add_vendor_response.status_code == 422

def test_get_vendors_by_name(add_vendor, new_vendor, client, auth_header):
    add_vendor_response = add_vendor(new_vendor)
    assert add_vendor_response.status_code == 200

    get_vendors_response = client.get(f"/vendors?vendor_name={new_vendor['name']}", headers=auth_header)
    assert get_vendors_response.status_code == 200
    assert get_vendors_response.json()[0]['name'] == new_vendor['name']

def test_get_vendors_by_id(add_vendor, new_vendor, client, auth_header):
    add_vendor_response = add_vendor(new_vendor)
    assert add_vendor_response.status_code == 200

    get_vendors_response = client.get(f"/vendors?vendor_id={add_vendor_response.json()['id']}", headers=auth_header)
    assert get_vendors_response.status_code == 200
    assert get_vendors_response.json()[0]['name'] == new_vendor['name']

def test_get_vendors_by_partial_name(add_vendor, new_vendor, client, auth_header):
    add_vendor_response = add_vendor(new_vendor)
    assert add_vendor_response.status_code == 200

    partial_vendor_name = new_vendor['name'][:3]
    get_vendors_response = client.get(f"/vendors?vendor_name={partial_vendor_name}", headers=auth_header)
    assert get_vendors_response.status_code == 200
    assert get_vendors_response.json()[0]['name'] == new_vendor['name']

def test_get_vendors_by_type(add_vendor, new_vendor, client, auth_header):
    add_vendor_response = add_vendor(new_vendor)
    assert add_vendor_response.status_code == 200

    get_vendors_response = client.get(f"/vendors?vendor_type={new_vendor['type']}", headers=auth_header)
    assert get_vendors_response.status_code == 200
    assert get_vendors_response.json()[0]['name'] == new_vendor['name']

def test_get_vendors_by_wrong_name(client, auth_header):
    get_vendors_response = client.get("/vendors?vendor_name='wrong_name'", headers=auth_header)
    assert get_vendors_response.status_code == 404

def test_get_vendors_by_wrong_id(client, auth_header):
    get_vendors_response = client.get("/vendors?vendor_id=10001", headers=auth_header)
    assert get_vendors_response.status_code == 404

def test_get_vendors_by_wrong_type(client, auth_header):
    get_vendors_response = client.get("/vendors?vendor_type='wrong_type'", headers=auth_header)
    assert get_vendors_response.status_code == 404

def test_get_vendors_missing_parameters(client, auth_header):
    get_vendors_response = client.get("/vendors", headers=auth_header)
    assert get_vendors_response.status_code == 400

def test_delete_vendor(auth_header, client, add_vendor, new_vendor):
    add_vendor_response = add_vendor(new_vendor)
    assert add_vendor_response.status_code == 200

    delete_vendor_response = client.delete(f"/vendor/{add_vendor_response.json()['id']}", headers=auth_header)
    assert delete_vendor_response.status_code == 200
    assert delete_vendor_response.json()['message'] == 'Vendor deleted'
    assert delete_vendor_response.json()['id'] == add_vendor_response.json()['id']

def test_delete_vendor_wrong_id(auth_header, client):
    delete_vendor_wrong_id = client.delete('/vendor/10001', headers=auth_header)
    assert delete_vendor_wrong_id.status_code == 400
    assert delete_vendor_wrong_id.json()['detail'] == 'Vendor not found'

def test_delete_vendor_missing_id(auth_header, client):
    delete_vendor_missing_id = client.delete('/vendor/', headers=auth_header)
    assert delete_vendor_missing_id.status_code == 405
