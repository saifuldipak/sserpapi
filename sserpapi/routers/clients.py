# pylint: disable=E0401
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

class Check:
    failed: bool = False
    message: str = ''

#- helper functions -#
def check_id_presence(db: Session, ids: dict) -> Check:
    check = Check()
    no_of_ids = sum(value is not None for value in ids.values())

    if no_of_ids != 1:
        check.failed = True
        check.message = 'You must provide any of client_id, service_id, or vendor_id but not more than one'
        return check

    if ids['client_id']:
        client_exists = db_query.get_client_by_id(db, client_id=ids['client_id'])
        if not client_exists:
            check.failed = True
            check.message = 'Client id does not exist'
    elif ids['service_id']:
        service_exists = db_query.get_service_by_id(db, service_id=ids['service_id'])
        if not service_exists:
            check.failed = True
            check.message = 'Service id does not exist'
    elif ids['vendor_id']:
        vendor_exists = db_query.get_vendor_by_id(db, vendor_id=ids['vendor_id'])
        if not vendor_exists:
            check.failed = True
            check.message = 'Vendor id does not exist'
    else:
        check.failed = True
        check.message = 'Key names should be "client_id", "service_id" and "vendor_id"'

    return check

def check_phone_number_length(phone_numbers: tuple) -> Check:
    check = Check()
    phone_numbers_exists = [phone_number for phone_number in phone_numbers if phone_number is not None]
    
    for phone_number in phone_numbers_exists:
        if len(phone_number) != 11:
            check.failed = True
            check.message = f'{phone_number} - Phone number must be 11 digits'
            return check    
    
    return check

#-- Search different types of records --#
@router.get("/search/service", response_model=list[schemas.ServiceDetails], summary='Search service', tags=['Searches'])
def search_service(service_point: str | None = None, client_id: int | None = None, page: int = 0, page_size: int = 10, db: Session = Depends(get_db)):    
    offset = page * page_size
    service_list =  db_query.get_service_list(db=db, service_point=service_point, client_id=client_id, offset=offset, limit=page_size)
    if not service_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return service_list
    
@router.get("/search/vendor", response_model=list[schemas.VendorDetails], summary='Search vendor', tags=['Searches'])
def search_vendor(vendor_name: str | None = None, vendor_type: str | None = None, page: int = 0, page_size: int = 10, db: Session = Depends(get_db)):    
    offset = page * page_size
    vendor_list =  db_query.get_vendor_list(db=db, vendor_name=vendor_name, vendor_type=vendor_type, offset=offset, limit=page_size)
    if not vendor_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return vendor_list
    
@router.get("/search/pop", response_model=list[schemas.PopDetails], summary='Search pop', tags=['Searches'])
def search_pop(pop_name: str | None = None, pop_owner: int | None = None, page: int = 0, page_size: int = 10, db: Session = Depends(get_db)):
    if not pop_name and not pop_owner:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You must give at least one query parameter')
    
    offset = page * page_size
    pop_list =  db_query.get_pop_list(db=db, pop_name=pop_name, pop_owner=pop_owner, offset=offset, limit=page_size)
    if not pop_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return pop_list

@router.get("/search/client", response_model=list[schemas.ClientDetails], summary='Search client', tags=['Searches'])
def search_client(client_name: str | None = None, client_type_id: int | None = None, page: int = 0, page_size: int = 10, db: Session = Depends(get_db)):
    offset = page * page_size
    client_list =  db_query.get_client_list(db=db, client_name=client_name, offset=offset, limit=page_size)
    if not client_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return client_list

@router.get("/search/client/type", response_model=list[schemas.ClientType], summary='Get client type list', tags=['Searches'])
def get_client_types(page: int = 0, page_size: int = 10, db: Session = Depends(get_db)):
    offset = page * page_size
    db_client_types = db_query.get_client_types(db, offset=offset, limit=page_size)
    return db_client_types

@router.get("/search/contact", response_model=list[schemas.ContactDetails], summary='Get contact list', tags=['Searches'])
def read_contact(contact_name: str | None = None, page: int = 0, page_size: int = 10, db: Session = Depends(get_db)):
    offset = page * page_size
    contact_list = db_query.get_contact_list(db, contact_name=contact_name, offset=offset, limit=page_size)
    if not contact_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    else:
        return contact_list

@router.get("/search/service/type", response_model=list[schemas.ServiceType], summary='Search service type', tags=['Searches'])
def search_service_type(service_type: str | None = None, page: int = 0, page_size: int = 10, db: Session = Depends(get_db)):
    offset = page * page_size
    service_type_list =  db_query.get_service_type_list(db=db, service_type=service_type, offset=offset, limit=page_size)
    if not service_type_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return service_type_list

#- client and client types add, update & delete -#
@router.post("/clients/add", response_model=schemas.Client, summary='Add a client', tags=['Clients'])
def create_client(client: schemas.ClientBase, db: Session = Depends(get_db)):
    client_exists = db_query.get_client_by_name(db, client_name=client.name)
    if client_exists:
        raise HTTPException(status_code=400, detail="Client exists")
    
    client_type_exists = db_query.get_client_type_by_id(db, client_type_id=client.client_type_id)
    if not client_type_exists:
        raise HTTPException(status_code=400, detail='Client type does not exist')
    
    return db_query.add_client(db=db, client=client)

@router.post("/clients/types/add", response_model=schemas.ClientType, summary='Add a client type', tags=['Clients'])
def add_client_type(client_type: schemas.ClientTypeBase, db: Session = Depends(get_db)):
    client_type_exists = db_query.get_client_type(db, client_type=client_type.name)
    if client_type_exists:
        raise HTTPException(status_code=400, detail="Client type exists")
    return db_query.add_client_type(db=db, client_type=client_type)

@router.put("/clients/modify", response_model=schemas.Client, summary='Modify a client', tags=['Clients'])
def update_client(client: schemas.Client, db: Session = Depends(get_db)):
    client_exists = db_query.get_client_by_id(db, client_id=client.id)
    if not client_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    
    client_type_exists = db_query.get_client_type_by_id(db, client_type_id=client.client_type_id)
    if not client_type_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Client type not found')
    
    return db_query.modify_client(db=db, client=client)

@router.delete("/client/type/delete/{client_type_id}", response_model=schemas.ClientType, summary='Delete a client type', tags=['Clients'])
def delete_client_type(client_type_id: int, db: Session = Depends(get_db)):
    client_type_exists = db_query.get_client_type_by_id(db, client_type_id=client_type_id)
    if not client_type_exists:
        raise HTTPException(status_code=400, detail="Client type not found")
    
    return_value =  db_query.delete_client_type(db=db, client_type_id=client_type_id)
    if return_value == client_type_id:
        return JSONResponse(content={'Action': 'Client type deleted', 'Client type id': client_type_id})
    
@router.delete("/clients/delete/{client_id}", summary='Delete a client', tags=['Clients'])
def remove_client(client_id: int, db: Session = Depends(get_db)):
    client_exists = db_query.get_client_by_id(db, client_id=client_id)
    if not client_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    
    return_value = db_query.delete_client(db=db, client_id=client_id)
    if return_value == client_id:
        return JSONResponse(content={'Action': 'Client deleted', 'Client id': client_id})

#-- Service and service types add, update and delete --#
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

@router.post("/service/add", response_model=schemas.Service, summary='Add a service', tags=['Services'])
def add_service(service: schemas.ServiceBase, db: Session = Depends(get_db)):
    '''
    ## Add service
    - **client-id**: Client id*
    - **point**: Service location* 
    - **service_type_id**: Service type id*
    - **bandwidth**: Bandwidth amount in Mbps*
    - **pop_id**: Pop id*
    - **extra_info**: Information on the service (Primary, Secondary, Head office/Branch office, connected to DC/DR etc)

    **Note**: *Required items
    '''
   
    service_exists = db_query.get_service_by_properties(db=db, service=service)
    if service_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Service exists')
    
    return db_query.add_service(db=db, service=service)

@router.put("/service/modify", response_model=schemas.Service, summary='Modify a service', tags=['Services'])
def modify_service(service: schemas.Service, db: Session = Depends(get_db)):
    '''
    ## Modify service
    - **id**: Service id* 
    - **client_id**: Client id*
    - **point**: Service location* 
    - **service_type_id**: Service type id*
    - **bandwidth**: Bandwidth amount in Mbps*
    - **pop_id**: Pop id*
    - **extra_info**: Information on the service (Primary, Secondary, Head office/Branch office, connected to DC/DR etc)

    **Note**: *Required items
    '''
   
    service_exists = db_query.get_service_by_id(db=db, service_id=service.id)
    if not service_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Service not found')
    
    return db_query.modify_service(db=db, service=service)

@router.delete("/service/type/delete/{service_type_id}", summary='Delete a service type', tags=['Services'])
def remove_service_type(service_type_id: int, db: Session = Depends(get_db)):
    service_type_exists = db_query.get_service_type_by_id(db, service_type_id=service_type_id)
    if not service_type_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service type not found")
    
    return_value = db_query.delete_service_type(db=db, service_type_id=service_type_id)
    if return_value == service_type_id:
        return JSONResponse(content={'Action': 'Service type deleted', 'Service type id': service_type_id})

@router.delete("/service/delete", response_model=schemas.EntryDelete, summary='Modify a service', tags=['Services'])
def remove_service(service_id: int, db: Session = Depends(get_db)):
    service_exists = db_query.get_service_by_id(db=db, service_id=service_id)
    if not service_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Service not found')
    
    return_value = db_query.delete_service(db=db, service_id=service_id)
    if return_value == service_id:
        entry_deleted = schemas.EntryDelete(message='Service deleted', id=service_id)
        return entry_deleted
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to delete service')

#-- Contacts add, update & delete --#
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
    ids = {'client_id': contact.client_id, 'service_id': contact.service_id, 'vendor_id': contact.vendor_id}
    check = check_id_presence(db=db, ids=ids)
    if check.failed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=check.message)

    phone_numbers = (contact.phone1, contact.phone2, contact.phone3)
    check = check_phone_number_length(phone_numbers=phone_numbers)
    if check.failed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=check.message)

    return db_query.add_contact(db=db, contact=contact)

@router.put("/contacts/modify", response_model=schemas.Contact, summary='Modify a contact', tags=['Contacts'])
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
    ids = {'client_id': contact.client_id, 'service_id': contact.service_id, 'vendor_id': contact.vendor_id}
    check = check_id_presence(db=db, ids=ids)
    if check.failed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=check.message)

    phone_numbers = (contact.phone1, contact.phone2, contact.phone3)
    check = check_phone_number_length(phone_numbers=phone_numbers)
    if check.failed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=check.message)

    return db_query.modify_contact(db=db, contact=contact)

@router.delete("/contact/delete/{contact_id}", summary='Delete a contact', tags=['Contacts'])
def remove_contact(contact_id: int, db: Session = Depends(get_db)):
    contact_exists = db_query.get_contact_by_id(db, contact_id=contact_id)
    if not contact_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    
    return_value = db_query.delete_contact(db=db, contact_id=contact_id)
    if return_value == contact_id:
        return JSONResponse(content={'Action': 'Contact deleted', 'Contact id': contact_id})

#-- Address add, update & modify --#
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
    ids = {'client_id': address.client_id, 'service_id': address.service_id, 'vendor_id': address.vendor_id}
    check = check_id_presence(db=db, ids=ids)
    if check.failed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=check.message)
    
    return db_query.add_address(db=db, address=address)    

@router.put("/address/modify", response_model=schemas.Address, summary='Modify an address', tags=['Addresses'])
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
    ids = {'client_id': address.client_id, 'service_id': address.service_id, 'vendor_id': address.vendor_id}
    check = check_id_presence(db=db, ids=ids)
    if not check.failed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=check.message)
    
    address_exists = db_query.get_address_by_id(db, address_id=address.id)
    if not address_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    
    return db_query.modify_address(db=db, address=address)

@router.delete("/address/delete/{address_id}", summary='Delete an address', tags=['Addresses'])
def remove_address(address_id: int, db: Session = Depends(get_db)):
    address_exists = db_query.get_address_by_id(db, address_id=address_id)
    if not address_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    
    return_value = db_query.delete_address(db=db, address_id=address_id)
    if return_value == address_id:
        return JSONResponse(content={'Action': 'Address deleted', 'Address id': address_id})

#-- Vendors add, update & modify --#
@router.post("/vendor/add", response_model=schemas.Vendor, summary='Add a vendor', tags=['Vendors'])
def add_vendor(vendor: schemas.VendorBase, db: Session = Depends(get_db)):
    '''
    ## Add vendor
    - **name**: Vendor name*
    - **type**: 'LSP'/'NTTN'/'ISP'* 

    **Note**: *Required items
    '''
   
    vendor_exists = db_query.get_vendor_by_properties(db=db, vendor=vendor)
    if vendor_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Vendor exists')
    
    return db_query.add_vendor(db=db, vendor=vendor)

@router.put("/vendor/modify", response_model=schemas.Vendor, summary='Modify a vendor', tags=['Vendors'])
def update_vendor(vendor: schemas.Vendor, db: Session = Depends(get_db)):
    '''
    ## Add vendor
    - **id**: Vendor id*
    - **name**: Vendor name*
    - **type**: 'LSP'/'NTTN'/'ISP'* 

    **Note**: *Required items
    '''
   
    vendor_exists = db_query.get_vendor_by_id(db=db, vendor_id=vendor.id)
    if not vendor_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Vendor not found')
    
    return db_query.modify_vendor(db=db, vendor=vendor)

@router.delete("/vendor/delete", response_model=schemas.EntryDelete, summary='Delete a vendor', tags=['Vendors'])
def remove_vendor(vendor_id: int, db: Session = Depends(get_db)):
    vendor_exists = db_query.get_vendor_by_id(db=db, vendor_id=vendor_id)
    if not vendor_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Vendor not found')
    
    vendor_deleted = db_query.delete_vendor(db=db, vendor_id=vendor_id)
    if vendor_deleted == vendor_id:
        return schemas.EntryDelete(message='Vendor deleted', id=vendor_id)

#-- Pops add, update & delete --#
@router.post("/pop/add", response_model=schemas.Pop, summary='Add a pop', tags=['Pops'])
def add_pop(pop: schemas.PopBase, db: Session = Depends(get_db)):
    '''
    ## Add Pop
    - **name**: Pop name*
    - **owner**: Vendor id*
    - **extra_info**: Any extra information 

    **Note**: *Required items
    '''
    pop_owner = db_query.get_vendor_by_id(db=db, vendor_id=pop.owner)
    if not pop_owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Vendor not found')
    
    pop_exists = db_query.get_pop_by_properties(db=db, pop=pop)
    if pop_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Pop exists')
    
    return db_query.add_pop(db=db, pop=pop)

@router.put("/pop/modify", response_model=schemas.Pop, summary='Modify a pop', tags=['Pops'])
def update_pop(pop: schemas.Pop, db: Session = Depends(get_db)):
    '''
    ## Modify Pop
    - **id**: Pop id*
    - **name**: Pop name*
    - **owner**: Vendor id*
    - **extra_info**: Any extra information 

    **Note**: *Required items
    '''
    pop_owner = db_query.get_vendor_by_id(db=db, vendor_id=pop.owner)
    if not pop_owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Vendor not found')
    
    pop_exists = db_query.get_pop_by_id(db=db, pop_id=pop.id)
    if not pop_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Pop not found')
    
    return db_query.modify_pop(db=db, pop=pop)

@router.delete("/pop/delete", response_model=schemas.EntryDelete, summary='Delete a pop', tags=['Pops'])
def remove_pop(pop_id: int, db: Session = Depends(get_db)):
    pop_exists = db_query.get_pop_by_id(db=db, pop_id=pop_id)
    if not pop_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Pop not found')
    
    vendor_deleted = db_query.delete_pop(db=db, pop_id=pop_id)
    if vendor_deleted == pop_id:
        return schemas.EntryDelete(message='Pop deleted', id=pop_id)