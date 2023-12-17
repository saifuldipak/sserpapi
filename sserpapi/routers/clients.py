from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from db.dependency import get_db
import pydantic_schemas as schemas
import db.queries as db_query
from auth import get_current_active_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Security(get_current_active_user, scopes=["admin", "editor", "user"])])

class Result:
    value: bool = True
    message: str = ''

def check_contact_properties(db: Session, contact: schemas.ContactBase) -> Result:
    result = Result()
    id_values = [contact.client_id, contact.service_id, contact.vendor_id]
    id_values_exists = [item for item in id_values if item is not None]
    if len(id_values_exists) != 1:
        result.value = False
        result.message = 'You must provide any of client_id, service_id or vendor_id but not more than one'
        return result
    
    phone_numbers = [contact.phone1, contact.phone2, contact.phone3]
    phone_numbers_exists = [item for item in phone_numbers if item is not None]
    for phone_number in phone_numbers_exists:
        if len(phone_number) != 11:
            result.value = False
            result.message = 'Phone number must be 11 digits'
            return result

    if contact.client_id:
        client_exists = db_query.get_client_by_id(db, client_id=contact.client_id)
        if not client_exists:
            result.value = False
            result.message = 'Client id does not exist'
    elif contact.service_id:
        service_exists = db_query.get_service_by_id(db, client_id=contact.service_id)
        if not service_exists:
            result.value = False
            result.message = 'Service id does not exist'
    elif contact.vendor_id:
        vendor_exists = db_query.get_vendor_by_id(db, client_id=contact.vendor_id)
        if not vendor_exists:
            result.value = False
            result.message = 'Vendor id does not exist'
    
    return result

def check_id_presence(db: Session, schema_object) -> Result:
    result = Result()
    id_values = [schema_object.client_id, schema_object.service_id, schema_object.vendor_id]
    id_values_exists = [item for item in id_values if item is not None]
    
    if len(id_values_exists) != 1:
        result.value = False
        result.message = 'You must provide any of client_id, service_id or vendor_id but not more than one'
        return result
    
    if schema_object.client_id:
        client_exists = db_query.get_client_by_id(db, client_id=schema_object.client_id)
        if not client_exists:
            result.value = False
            result.message = 'Client id does not exist'
    elif schema_object.service_id:
        service_exists = db_query.get_service_by_id(db, service_id=schema_object.service_id)
        if not service_exists:
            result.value = False
            result.message = 'Service id does not exist'
    elif schema_object.vendor_id:
        vendor_exists = db_query.get_vendor_by_id(db, vendor_id=schema_object.vendor_id)
        if not vendor_exists:
            result.value = False
            result.message = 'Vendor id does not exist'
    
    return result

def check_phone_number_length(db: Session, schema_object) -> Result:
    result = Result()
    phone_numbers = [schema_object.phone1, schema_object.phone2, schema_object.phone3]
    phone_numbers_exists = [item for item in phone_numbers if item is not None]
    
    for phone_number in phone_numbers_exists:
        if len(phone_number) != 11:
            result.value = False
            result.message = 'Phone number must be 11 digits'
            return result    
    
    return result

@router.post("/clients/add", response_model=schemas.Client, summary='Add a client', tags=['Clients'])
def create_client(client: schemas.ClientBase, db: Session = Depends(get_db)):
    client_exists = db_query.get_client_by_name(db, client_name=client.name)
    if client_exists:
        raise HTTPException(status_code=400, detail="Client exists")
    
    client_type_exists = db_query.get_client_type_by_id(db, client_type_id=client.client_type_id)
    if not client_type_exists:
        raise HTTPException(status_code=400, detail='Client type does not exist')
    
    return db_query.add_client(db=db, client=client)

@router.get("/clients/search/{client_name}", response_model=list[schemas.ClientDetails], summary='Search client', tags=['Clients'])
def read_clients(client_name: str, page: int = 0, page_size: int = 10, db: Session = Depends(get_db)):
    """
    ## Search client by name

    **client_name**: Full or partial client name 

    **Note**: If you provide partial name, it will only show client names those start with that string
    """
    offset = page * page_size
    return db_query.get_client_list(db, client_name=client_name, offset=offset, limit=page_size)

@router.post("/clients/types/add", response_model=schemas.ClientType, summary='Add a client type', tags=['Clients'])
def add_client_type(client_type: schemas.ClientTypeBase, db: Session = Depends(get_db)):
    client_type_exists = db_query.get_client_type(db, client_type=client_type.name)
    if client_type_exists:
        raise HTTPException(status_code=400, detail="Client type exists")
    return db_query.add_client_type(db=db, client_type=client_type)

@router.get("/clients/types/get", response_model=list[schemas.ClientType], summary='Get client type list', tags=['Clients'])
def get_client_types(page: int = 0, page_size: int = 10, db: Session = Depends(get_db)):
    offset = page * page_size
    db_client_types = db_query.get_client_types(db, offset=offset, limit=page_size)
    return db_client_types

@router.post("/client/type/delete", response_model=schemas.ClientType, summary='Delete a client type', tags=['Clients'])
def delete_client_type(client_type_id: int, db: Session = Depends(get_db)):
    client_type_exists = db_query.get_client_type_by_id(db, client_type_id=client_type_id)
    if not client_type_exists:
        raise HTTPException(status_code=400, detail="Client type not found")
    
    return_value =  db_query.delete_client_type(db=db, client_type_id=client_type_id)
    if return_value == client_type_id:
        return JSONResponse(content={'Action': 'Client type deleted', 'Client type id': client_type_id})

@router.post("/clients/modify", response_model=schemas.Client, summary='Modify a client', tags=['Clients'])
def remove_client(client: schemas.Client, db: Session = Depends(get_db)):
    client_exists = db_query.get_client_by_id(db, client_id=client.id)
    if not client_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    
    client_type_exists = db_query.get_client_type_by_id(db, client_type_id=client.client_type_id)
    if not client_type_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Client type not found')
    
    return db_query.modify_client(db=db, client=client)

@router.post("/clients/delete/{client_id}", summary='Delete a client', tags=['Clients'])
def remove_client(client_id: int, db: Session = Depends(get_db)):
    client_exists = db_query.get_client_by_id(db, client_id=client_id)
    if not client_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    
    return_value = db_query.delete_client(db=db, client_id=client_id)
    if return_value == client_id:
        return JSONResponse(content={'Action': 'Client deleted', 'Client id': client_id})

@router.post("/contacts/add", response_model=schemas.Contact, summary='Add a contact', tags=['Contacts'])
def add_contact(contact: schemas.ContactBase, db: Session = Depends(get_db)):
    """
    ## Add a contact
    - **name**: Full name*
    - **designation**: Designation of the person*
    - **type**: 'Admin'/'Technical'/'Billing' *
    - **phone1**: Phone number*
    - **phone2**: Phone number
    - **phone3**: Phone number
    - **service_id**: Service id (integer)**
    - **client_id**: Client id (integer)**
    - **vendor_id**: Vendor id (integer)**

    **Note**: *Required fields. **You must provide any of client_id, vendor_id or service_id but not more than one.
    """
    check_result = check_contact_properties(db, contact)
    if not check_result.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=check_result.message)

    return db_query.add_contact(db=db, contact=contact)

@router.get("/contacts/search/{contact_name}", response_model=list[schemas.ContactWithClientName], summary='Search contact', tags=['Contacts'])
def read_contact(contact_name: str, page: int = 0, page_size: int = 10, db: Session = Depends(get_db)):
    """
    ## Search contact by name
    **contact_name**: Full or partial contact name*

    **Note**: *Required. If you provide partial name, it will show all contacts which has that name
    """
    offset = page * page_size
    return db_query.get_contact_list(db, contact_name=contact_name, offset=offset, limit=page_size)

@router.post("/contacts/modify", response_model=schemas.Contact, summary='Modify a contact', tags=['Contacts'])
def modify_contact(contact: schemas.Contact, db: Session = Depends(get_db)):
    """
    ## Modify a contact
    - **id**: Contact id*
    - **name**: Full name*
    - **designation**: Designation of the person*
    - **type**: 'Admin'/'Technical'/'Billing' *
    - **phone1**: Phone number*
    - **phone2**: Phone number
    - **phone3**: Phone number
    - **service_id**: Service id (integer)**
    - **client_id**: Client id (integer)**
    - **vendor_id**: Vendor id (integer)**

    **Note**: *Required fields. **You must provide any of client_id, vendor_id or service_id but not more than one.
    """
    check_result = check_contact_properties(db, contact)
    if not check_result.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=check_result.message)

    return db_query.modify_contact(db=db, contact=contact)

@router.post("/contact/delete/{contact_id}", summary='Delete a contact', tags=['Contacts'])
def remove_contact(contact_id: int, db: Session = Depends(get_db)):
    contact_exists = db_query.get_contact_by_id(db, contact_id=contact_id)
    if not contact_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    
    return_value = db_query.delete_contact(db=db, contact_id=contact_id)
    if return_value == contact_id:
        return JSONResponse(content={'Action': 'Contact deleted', 'Contact id': contact_id})

@router.post("/service/type/add", response_model=schemas.ServiceType, summary='Add a service type', tags=['Services'])
def add_service_type(service_type: schemas.ServiceTypeBase, db: Session = Depends(get_db)):
    '''
    ## Add service type
    - **name**: Service type name* 
    - **description**: Description

    *Required
    '''
    service_type_exists = db_query.get_service_type_by_name(db, service_type=service_type)
    if service_type_exists:
        raise HTTPException(status_code=400, detail="Service type exists")
    return db_query.add_service_type(db=db, service_type=service_type)

@router.get("/service/type/search", response_model=list[schemas.ServiceType], summary='Search service type', tags=['Services'])
def search_service_type(service_type: str | None = None, page: int = 0, page_size: int = 10, db: Session = Depends(get_db)):
    offset = page * page_size
    service_type_list =  db_query.get_service_type_list(db=db, service_type=service_type, offset=offset, limit=page_size)
    if not service_type_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return service_type_list

@router.post("/service/type/delete/{service_type_id}", summary='Delete a service type', tags=['Services'])
def remove_service_type(service_type_id: int, db: Session = Depends(get_db)):
    service_type_exists = db_query.get_service_type_by_id(db, service_type_id=service_type_id)
    if not service_type_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service type not found")
    
    return_value = db_query.delete_service_type(db=db, service_type_id=service_type_id)
    if return_value == service_type_id:
        return JSONResponse(content={'Action': 'Service type deleted', 'Service type id': service_type_id})

@router.post("/address/add", response_model=schemas.Address, summary='Add an address', tags=['Addresses'])
def add_address(address: schemas.AddressBase, db: Session = Depends(get_db)):
    '''
    ## Add address
    - **flat**: Flat name 
    - **floor**: Floor number
    - **holding**: Holding number*
    - **area**: Area name (Para/Moholla/Block/Sector/Housing society name etc.)*
    - **street**: Street name or number*
    - **thana**: Thana name*
    - **district**: District name*
    - **client_id**: Client id**
    - **service_id**: Service id**
    - **vendor_id**: Vendor id**
    - **extra_info**: Extra info (remark, description, landmark etc)

    **Note**: *Required items, **Need to give at least any one of these items but not more than one
    '''
    result = check_id_presence(db=db, schema_object=address)
    if not result.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.message)
    
    return db_query.add_address(db=db, address=address)    

@router.post("/address/modify", response_model=schemas.Address, summary='Modify an address', tags=['Addresses'])
def modify_address(address: schemas.Address, db: Session = Depends(get_db)):
    '''
    ## Modify address
    - **id**: Address id*
    - **flat**: Flat name 
    - **floor**: Floor number
    - **holding**: Holding number*
    - **area**: Area name (Para/Moholla/Block/Sector/Housing society name etc.)*
    - **street**: Street name or number*
    - **thana**: Thana name*
    - **district**: District name*
    - **client_id**: Client id**
    - **service_id**: Service id**
    - **vendor_id**: Vendor id**
    - **extra_info**: Extra info (remark, description, landmark etc)

    **Note**: *Required items, **Need to give at least any one of these items but not more than one
    '''
    result = check_id_presence(db=db, schema_object=address)
    if not result.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.message)
    
    address_exists = db_query.get_address_by_id(db, address_id=address.id)
    if not address_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    
    return db_query.modify_address(db=db, address=address)

@router.post("/address/delete/{address_id}", summary='Delete an address', tags=['Addresses'])
def remove_address(address_id: int, db: Session = Depends(get_db)):
    address_exists = db_query.get_address_by_id(db, address_id=address_id)
    if not address_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    
    return_value = db_query.delete_address(db=db, address_id=address_id)
    if return_value == address_id:
        return JSONResponse(content={'Action': 'Address deleted', 'Address id': address_id})

@router.post("/service/add", response_model=schemas.Service, summary='Add a service', tags=['Services'])
def add_service(service: schemas.ServiceBase, db: Session = Depends(get_db)):
    '''
    ## Add service
    - **client-id**: Client id*
    - **point**: Service location* 
    - **service_type_id**: Service type id*
    - **bandwidth**: Bandwidth amount in Mbps*
    - **connected_to**: Service logically connected to(DC, DR, Head Office etc)
    - **extra_info**: Information on the service (Primary, Secondary etc)

    **Note**: *Required items
    '''
   
    service_exists = db_query.get_service_by_properties(db=db, service=service)
    if service_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Service exists')
    
    return db_query.add_service(db=db, service=service)

@router.post("/service/modify", response_model=schemas.Service, summary='Modify a service', tags=['Services'])
def modify_service(service: schemas.Service, db: Session = Depends(get_db)):
    '''
    ## Modify service
    - **service_id**: Service id* 
    - **client_id**: Client id*
    - **point**: Service location* 
    - **service_type_id**: Service type id*
    - **bandwidth**: Bandwidth amount in Mbps*
    - **connected_to**: Service logically connected to(DC, DR, Head Office etc)
    - **extra_info**: Information on the service (Primary, Secondary etc)

    **Note**: *Required items
    '''
   
    service_exists = db_query.get_service_by_id(db=db, service_id=service.id)
    if not service_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Service not found')
    
    return db_query.modify_service(db=db, service=service)

@router.delete("/service/delete", response_model=schemas.EntryDelete, summary='Modify a service', tags=['Services'])
def modify_service(service_id: int, db: Session = Depends(get_db)):
    service_exists = db_query.get_service_by_id(db=db, service_id=service_id)
    if not service_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Service not found')
    
    return_value = db_query.delete_service(db=db, service_id=service_id)
    if return_value == service_id:
        entry_deleted = schemas.EntryDelete(message='Service deleted', id=service_id)
        return entry_deleted
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to delete service')
        

@router.get("/search/service", response_model=list[schemas.ServiceDetails], summary='Search service', tags=['Searches'])
def search(service_point: str | None = None, client_id: int | None = None, page: int = 0, page_size: int = 10, db: Session = Depends(get_db)):
    if not service_point and not client_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You must give at least one query parameter')
    
    offset = page * page_size
    service_list =  db_query.get_service_list(db=db, service_point=service_point, client_id=client_id, offset=offset, limit=page_size)
    if not service_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return service_list
