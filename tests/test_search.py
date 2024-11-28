def assert_search_response(search_response, new_clients, new_client_type, total, page, items_per_page):
    assert search_response.status_code == 200
    assert len(search_response.json().get('results')) == items_per_page  
    assert search_response.json().get('total') == total
    assert search_response.json().get('page') == page
    assert search_response.json().get('items_per_page') == items_per_page  

    new_clients_sorted = sorted(new_clients, key=lambda client: client.get('name'))
    results_from = (page - 1) * items_per_page
    results_to = page * items_per_page
    new_clients_sorted_subset = new_clients_sorted[results_from:results_to]

    for i in range(items_per_page):
        assert search_response.json().get('results')[i].get('name') == new_clients_sorted_subset[i].get('name')
        assert search_response.json().get('results')[i]['client_types']['name'] == new_client_type.json().get('name')


def test_search_clients(auth_header, client, add_clients, new_client):
    clients = 100
    (new_clients, new_client_type, another_new_client_type)  = add_clients(clients)
    get_clients_response = client.get(f"/search?query={new_client['name']}&resource_type=clients", headers=auth_header)
    assert_search_response(get_clients_response, new_clients, new_client_type, clients, 1, 20)   

def test_search_clients_with_page_and_items_per_page(auth_header, client, add_clients, new_client):
    clients = 100
    page = 5
    items_per_page = 10
    (new_clients, new_client_type, another_new_client_type)  = add_clients(clients)
    get_clients_response = client.get(f"/search?query={new_client['name']}&resource_type=clients&page={page}&items_per_page={items_per_page}", headers=auth_header)
    assert_search_response(get_clients_response, new_clients, new_client_type, clients, page, items_per_page)
