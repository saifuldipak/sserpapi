def get_partial_list(list, resource_type, page, items_per_page):
    if resource_type == 'clients':
        sorted_list = sorted(list, key=lambda item: item.get('name'))
    elif resource_type == 'services':
        sorted_list = sorted(list, key=lambda item: item.get('point'))
    
    results_from = (page - 1) * items_per_page
    results_to = page * items_per_page
    partial_list = sorted_list[results_from:results_to]
    return partial_list

def assert_client_search_response(search_response, new_clients, new_client_type, total, page, items_per_page):
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
        assert search_response.json().get('results')[i]['client_types']['name'] == new_client_type.get('name')

def assert_service_search_response(search_response, new_services, total, page, items_per_page):
    assert search_response.status_code == 200
    assert len(search_response.json().get('results')) == items_per_page
    assert search_response.json().get('total') == total
    assert search_response.json().get('page') == page
    assert search_response.json().get('items_per_page') == items_per_page

    new_services_partial = get_partial_list(new_services, 'services', page, items_per_page)
    for i in range(items_per_page):
        assert search_response.json().get('results')[i].get('point') == new_services_partial[i].get('point')
        assert search_response.json().get('results')[i]['client_id'] == new_services_partial[i]['client_id']
        assert search_response.json().get('results')[i]['pop_id'] == new_services_partial[i]['pop_id']
        assert search_response.json().get('results')[i]['service_type_id'] == new_services_partial[i]['service_type_id']
        assert search_response.json().get('results')[i]['bandwidth'] == new_services_partial[i]['bandwidth']
  
def test_search_clients(auth_header, client, add_clients, new_client, new_client_type, add_client_type):
    clients = 50
    add_client_type_response = add_client_type(new_client_type)
    assert add_client_type_response.status_code == 200
    test_client = new_client.copy()
    test_client['client_type_id'] = add_client_type_response.json()['id']
    new_clients  = add_clients(clients, test_client)
    get_clients_response = client.get(f"/search?query={test_client['name']}&resource_type=clients", headers=auth_header)
    assert_client_search_response(get_clients_response, new_clients, new_client_type, clients, 1, 20)

def test_search_clients_with_pagination(auth_header, client, add_clients, new_client, new_client_type, add_client_type):
    clients = 50
    page = 5
    items_per_page = 10

    add_client_type_response = add_client_type(new_client_type)
    assert add_client_type_response.status_code == 200
    test_client = new_client.copy()
    test_client['client_type_id'] = add_client_type_response.json()['id']
    new_clients  = add_clients(clients, test_client)

    get_clients_response = client.get(f"/search?query={test_client['name']}&resource_type=clients&page={page}&items_per_page={items_per_page}", headers=auth_header)
    assert_client_search_response(get_clients_response, new_clients, new_client_type, clients, page, items_per_page)

def test_search_clients_with_wrong_pagination(auth_header, client, add_clients, new_client, new_client_type, add_client_type):
    clients = 20
    page = 3
    items_per_page = 10

    add_client_type_response = add_client_type(new_client_type)
    assert add_client_type_response.status_code == 200
    test_client = new_client.copy()
    test_client['client_type_id'] = add_client_type_response.json()['id']
    new_clients  = add_clients(clients, test_client)

    get_clients_response = client.get(f"/search?query={test_client['name']}&resource_type=clients&page={page}&items_per_page={items_per_page}", headers=auth_header)
    assert get_clients_response.status_code == 404

def test_search_clients_by_client_type(auth_header, client, add_clients, new_client, new_client_type, add_client_type):
    clients = 50
    page = 2
    items_per_page = 10

    client_type_a = new_client_type.copy()
    client_type_a['name'] = 'client_type_a'
    add_client_type_a_response = add_client_type(client_type_a)
    assert add_client_type_a_response.status_code == 200
    new_client_a = new_client.copy()
    new_client_a['name'] = 'Client_a'
    new_client_a['client_type_id'] = add_client_type_a_response.json()['id']
    new_clients_a = add_clients(clients, new_client_a)

    client_type_b = new_client_type.copy()
    client_type_b['name'] = 'client_type_b'
    add_client_type_b_response = add_client_type(client_type_b)
    assert add_client_type_b_response.status_code == 200
    new_client_b = new_client.copy()
    new_client_b['name'] = 'Client_b'
    new_client_b['client_type_id'] = add_client_type_b_response.json()['id']
    new_clients_b = add_clients(clients, new_client_b)

    get_clients_response = client.get(f"/search?query={new_client_a['name']}&resource_type=clients&client_type={add_client_type_a_response.json()['name']}&page={page}&items_per_page={items_per_page}", headers=auth_header)
    assert_client_search_response(get_clients_response, new_clients_a, client_type_a, clients, page, items_per_page)

    get_clients_response = client.get(f"/search?query={new_client_b['name']}&resource_type=clients&client_type={add_client_type_b_response.json()['name']}&page={page}&items_per_page={items_per_page}", headers=auth_header)
    assert_client_search_response(get_clients_response, new_clients_b, client_type_b, clients, page, items_per_page)

def test_search_clients_by_wrong_client_type(auth_header, client, add_clients, new_client, new_client_type, add_client_type):
    clients = 50
    page = 2
    items_per_page = 10

    add_client_type_response = add_client_type(new_client_type)
    assert add_client_type_response.status_code == 200
    test_client = new_client.copy()
    test_client['client_type_id'] = add_client_type_response.json()['id']
    new_clients = add_clients(clients, test_client)

    get_clients_response = client.get(f"/search?query={new_client['name']}&resource_type=clients&client_type=wrong_client_type&page={page}&items_per_page={items_per_page}", headers=auth_header)
    assert get_clients_response.status_code == 404

def test_search_clients_by_wrong_client_name(auth_header, client, add_clients, new_client_type, add_client_type, new_client):
    clients = 50

    add_client_type_response = add_client_type(new_client_type)
    assert add_client_type_response.status_code == 200
    test_client = new_client.copy()
    test_client['client_type_id'] = add_client_type_response.json()['id']
    new_clients = add_clients(clients, test_client)
    get_clients_response = client.get(f"/search?query=wrong_client_name&resource_type=clients", headers=auth_header)
    assert get_clients_response.status_code == 404

def test_search_services(auth_header, client, add_services, new_service, add_pop, new_pop, new_vendor, add_client, new_client, add_service_type, new_service_type):
    services = 50
    add_client_response = add_client(new_client)
    assert add_client_response.status_code == 200
    add_pop_response = add_pop(new_pop, new_vendor)
    assert add_pop_response.status_code == 200
    add_service_type_response = add_service_type(new_service_type)
    assert add_service_type_response.status_code == 200

    test_service = new_service.copy()
    test_service['client_id'] = add_client_response.json()['id']
    test_service['service_type_id'] = add_service_type_response.json()['id']
    test_service['pop_id'] = add_pop_response.json()['id']
    new_services = add_services(services, test_service)

    get_services_response = client.get(f"/search?query={new_service['point']}&resource_type=services", headers=auth_header)
    assert_service_search_response(get_services_response, new_services, services, 1, 20)

def test_search_services_with_pagination(auth_header, client, add_services, new_service, add_pop, new_pop, new_vendor, add_client, new_client, add_service_type, new_service_type):
    services = 50
    page = 2
    items_per_page = 10
    add_client_response = add_client(new_client)
    assert add_client_response.status_code == 200
    add_pop_response = add_pop(new_pop, new_vendor)
    assert add_pop_response.status_code == 200
    add_service_type_response = add_service_type(new_service_type)
    assert add_service_type_response.status_code == 200

    test_service = new_service.copy()
    test_service['client_id'] = add_client_response.json()['id']
    test_service['service_type_id'] = add_service_type_response.json()['id']
    test_service['pop_id'] = add_pop_response.json()['id']
    new_services = add_services(services, test_service)

    get_services_response = client.get(f"/search?query={new_service['point']}&resource_type=services&page={page}&items_per_page={items_per_page}", headers=auth_header)
    assert_service_search_response(get_services_response, new_services, services, page, items_per_page)

def test_search_services_with_wrong_pagination(auth_header, client, add_services, new_service, add_pop, new_pop, new_vendor, add_client, new_client, add_service_type, new_service_type):
    services = 10
    page = 2
    items_per_page = 10
    add_client_response = add_client(new_client)
    assert add_client_response.status_code == 200
    add_pop_response = add_pop(new_pop, new_vendor)
    assert add_pop_response.status_code == 200
    add_service_type_response = add_service_type(new_service_type)
    assert add_service_type_response.status_code == 200

    test_service = new_service.copy()
    test_service['client_id'] = add_client_response.json()['id']
    test_service['service_type_id'] = add_service_type_response.json()['id']
    test_service['pop_id'] = add_pop_response.json()['id']
    new_services = add_services(services, test_service)

    get_services_response = client.get(f"/search?query={new_service['point']}&resource_type=services&page={page}&items_per_page={items_per_page}", headers=auth_header)
    assert get_services_response.status_code == 404

def test_search_services_by_client_name(auth_header, client, add_services, new_service, add_pop, new_pop, new_vendor, add_client_only, new_client, add_service_type, new_service_type, add_client_type, new_client_type):
    services = 50
    page = 2
    items_per_page = 10

    add_client_type_response = add_client_type(new_client_type)
    assert add_client_type_response.status_code == 200
    add_pop_response = add_pop(new_pop, new_vendor)
    assert add_pop_response.status_code == 200
    add_service_type_response = add_service_type(new_service_type)
    assert add_service_type_response.status_code == 200

    test_client_1 = new_client.copy()
    test_client_1['name'] = 'test_client_1'
    test_client_1['client_type_id'] = add_client_type_response.json()['id']
    add_test_client_1_response = add_client_only(test_client_1)
    assert add_test_client_1_response.status_code == 200
    test_service_1 = new_service.copy()
    test_service_1['client_id'] = add_test_client_1_response.json()['id']
    test_service_1['service_type_id'] = add_service_type_response.json()['id']
    test_service_1['pop_id'] = add_pop_response.json()['id']
    new_services_1 = add_services(services, test_service_1)

    test_client_2 = new_client.copy()
    test_client_2['name'] = 'test_client_2'
    test_client_2['client_type_id'] = add_client_type_response.json()['id']
    add_test_client_2_response = add_client_only(test_client_2)
    assert add_test_client_2_response.status_code == 200
    test_service_2 = new_service.copy()
    test_service_2['client_id'] = add_test_client_2_response.json()['id']
    test_service_2['service_type_id'] = add_service_type_response.json()['id']
    test_service_2['pop_id'] = add_pop_response.json()['id']
    new_services_2 = add_services(services, test_service_2)
    
    get_services_response = client.get(f"/search?query={new_service['point']}&resource_type=services&client_name={add_test_client_1_response.json()['name']}&page={page}&items_per_page={items_per_page}", headers=auth_header)
    assert_service_search_response(get_services_response, new_services_1, services, page, items_per_page)

    get_services_response = client.get(f"/search?query={new_service['point']}&resource_type=services&client_name={add_test_client_2_response.json()['name']}&page={page}&items_per_page={items_per_page}", headers=auth_header)
    assert_service_search_response(get_services_response, new_services_2, services, page, items_per_page)

def test_search_services_by_service_type(auth_header, client, add_services, new_service, add_pop, new_pop, new_vendor, add_client, new_client, add_service_type, new_service_type):
    services = 50
    page = 2
    items_per_page = 10

    add_client_response = add_client(new_client)
    assert add_client_response.status_code == 200
    add_pop_response = add_pop(new_pop, new_vendor)
    assert add_pop_response.status_code == 200

    service_type_internet = new_service_type.copy()
    service_type_internet['name'] = 'Internet'
    add_service_type_internet_response = add_service_type(service_type_internet)
    assert add_service_type_internet_response.status_code == 200
    test_service_1 = new_service.copy()
    test_service_1['client_id'] = add_client_response.json()['id']
    test_service_1['service_type_id'] = add_service_type_internet_response.json()['id']
    test_service_1['pop_id'] = add_pop_response.json()['id']
    new_services_1 = add_services(services, test_service_1)

    service_type_data = new_service_type.copy()
    service_type_data['name'] = 'Data'
    add_service_type_data_response = add_service_type(service_type_data)
    assert add_service_type_data_response.status_code == 200
    test_service_2 = new_service.copy()
    test_service_2['client_id'] = add_client_response.json()['id']
    test_service_2['service_type_id'] = add_service_type_data_response.json()['id']
    test_service_2['pop_id'] = add_pop_response.json()['id']
    new_services_2 = add_services(services, test_service_2)
    
    get_services_response = client.get(f"/search?query={new_service['point']}&resource_type=services&service_type={add_service_type_internet_response.json()['name']}&page={page}&items_per_page={items_per_page}", headers=auth_header)
    assert_service_search_response(get_services_response, new_services_1, services, page, items_per_page)

    get_services_response = client.get(f"/search?query={new_service['point']}&resource_type=services&service_type={add_service_type_data_response.json()['name']}&page={page}&items_per_page={items_per_page}", headers=auth_header)
    assert_service_search_response(get_services_response, new_services_2, services, page, items_per_page)

def test_search_services_by_pop_name(auth_header, client, add_services, new_service, add_pop_only, new_pop, add_vendor, new_vendor, add_client, new_client, add_service_type, new_service_type):
    services = 50
    page = 2
    items_per_page = 10

    add_client_response = add_client(new_client)
    assert add_client_response.status_code == 200
    add_service_type_response = add_service_type(new_service_type)
    assert add_service_type_response.status_code == 200
    add_vendor_response = add_vendor(new_vendor)
    assert add_vendor_response.status_code == 200

    test_pop_1 = new_pop.copy()
    test_pop_1['name'] = 'Pop_1'
    test_pop_1['owner'] = add_vendor_response.json()['id']
    add_test_pop_1_response = add_pop_only(test_pop_1)
    assert add_test_pop_1_response.status_code == 200
    test_service_1 = new_service.copy()
    test_service_1['point'] = 'test_service_a'
    test_service_1['client_id'] = add_client_response.json()['id']
    test_service_1['service_type_id'] = add_service_type_response.json()['id']
    test_service_1['pop_id'] = add_test_pop_1_response.json()['id']
    new_services_1 = add_services(services, test_service_1)

    test_pop_2 = new_pop.copy()
    test_pop_2['name'] = 'Pop_2'
    test_pop_2['owner'] = add_vendor_response.json()['id']
    add_test_pop_2_response = add_pop_only(test_pop_2)
    assert add_test_pop_2_response.status_code == 200
    test_service_2 = new_service.copy()
    test_service_1['point'] = 'test_service_b'
    test_service_2['client_id'] = add_client_response.json()['id']
    test_service_2['service_type_id'] = add_service_type_response.json()['id']
    test_service_2['pop_id'] = add_test_pop_2_response.json()['id']
    new_services_2 = add_services(services, test_service_2)
    
    get_services_response = client.get(f"/search?query={new_service['point']}&resource_type=services&pop_name={add_test_pop_1_response.json()['name']}&page={page}&items_per_page={items_per_page}", headers=auth_header)
    assert_service_search_response(get_services_response, new_services_1, services, page, items_per_page)

    get_services_response = client.get(f"/search?query={new_service['point']}&resource_type=services&pop_name={add_test_pop_2_response.json()['name']}&page={page}&items_per_page={items_per_page}", headers=auth_header)
    assert_service_search_response(get_services_response, new_services_2, services, page, items_per_page)