# pylint: disable=E0401
import logging
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import sserpapi.pydantic_schemas as schemas
from sserpapi.db.dependency import get_db
from sserpapi.db import queries as db_query
from sserpapi.auth import get_current_active_user
import typing_extensions

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Security(get_current_active_user, scopes=["admin", "editor", "user"])])

class Check:
    """
    Represents the result of a check operation.

    Attributes:
    - failed (bool): Indicates whether the check failed (True) or succeeded (False).
    - message (str): A message providing additional information about the check result.

    Example:
    >>> result = Check()
    >>> result.failed = True
    >>> result.message = 'Validation failed due to missing data'
    >>> print(result.failed)  # True
    >>> print(result.message)  # 'Validation failed due to missing data'

    Note:
    - Instances of this class are typically used to convey the outcome of validation or verification checks.
    - The 'failed' attribute is a boolean indicating the success or failure of the check.
    - The 'message' attribute provides additional details or reasons for the check result.
    """
    failed: bool = False
    message: str = ''

#-- Helper functions --#
def check_id_presence(db: Session, ids: dict) -> Check:
    """
    Checks the presence and validity of identifiers (client_id, service_id, vendor_id) in the provided dictionary.

    Parameters:
    - db (Session): The database session to perform queries.
    - ids (dict): A dictionary containing identifiers with keys 'client_id', 'service_id', and 'vendor_id'.

    Returns:
    - Check: An object indicating the result of the checks, including success or failure status and messages.

    Example:
    >>> from sqlalchemy.orm import Session
    >>> import db.queries as db_query

    >>> session = Session()  # Replace with your actual database session
    >>> id_dict = {'client_id': 1, 'service_id': None, 'vendor_id': None}
    >>> result = check_id_presence(session, id_dict)
    >>> print(result.failed)  # True or False
    >>> print(result.message)  # Failure or success message

    Note:
    - The function checks that exactly one of client_id, service_id, or vendor_id is provided in the dictionary.
    - It then validates the presence of the provided identifier in the respective database table.
    - The dictionary keys should be 'client_id', 'service_id', and 'vendor_id'.
    - If the dictionary structure is incorrect, the check fails with an appropriate message.
    """
    check = Check()
    no_of_ids = sum(value is not None for value in ids.values())

    if no_of_ids != 1:
        check.failed = True
        check.message = 'Must provide any of client_id, service_id, or vendor_id but not more than one'
        return check

    if ids['client_id']:
        try:
            client_exists = db_query.get_clients(db, client_id=ids['client_id'])
        except Exception as e:
            logger.error("get_clients(): %s", e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
        
        if not client_exists:
            check.failed = True
            check.message = 'Client not found'
    elif ids['service_id']:
        try:
            service_exists = db_query.get_services(db, service_id=ids['service_id'])
        except Exception as e:
            logger.error("get_services(): %s", e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
        
        if not service_exists:
            check.failed = True
            check.message = 'Service not found'
    elif ids['vendor_id']:
        try:
            vendor_exists = db_query.get_vendor_by_id(db, vendor_id=ids['vendor_id'])
        except Exception as e:
            logger.error("get_vendor_by_id(): %s", e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
        
        if not vendor_exists:
            check.failed = True
            check.message = 'Vendor id does not exist'
    else:
        check.failed = True
        check.message = 'You must provide any of client_id, service_id, or vendor_id but not more than one'

    return check

def check_phone_number_length(phone_numbers: tuple) -> Check:
    """
    Checks the length of phone numbers in the provided tuple.

    Parameters:
    - phone_numbers (tuple): A tuple containing phone numbers to be checked.

    Returns:
    - Check: An object indicating the result of the phone number length checks, including success or failure status
      and messages.

    Example:
    >>> phone_numbers = ('12345678901', '98765432109', None)
    >>> result = check_phone_number_length(phone_numbers=phone_numbers)
    >>> print(result.failed)  # True or False
    >>> print(result.message)  # Failure or success message

    Note:
    - The function checks the length of each provided phone number (11 digits expected).
    - If any phone number has a length other than 11 digits, the check fails, and an appropriate message is set.
    - The 'failed' attribute in the returned Check object indicates the overall success or failure of the checks.
    """
    check = Check()
    phone_numbers_exists = [phone_number for phone_number in phone_numbers if phone_number is not None]

    for phone_number in phone_numbers_exists:
        if len(phone_number) != 11:
            check.failed = True
            check.message = f'{phone_number} - Phone number must be 11 digits'
            return check

    return check

def check_service_data(db: Session, service: dict) -> None:
    try:
        client_exists = db_query.get_clients(db, client_id=service['client_id'])
    except Exception as e:
        logger.error('get_clients(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if not client_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Client not found')
    
    try:
        service_type_exists = db_query.get_service_types(db, type_id=service['service_type_id'])
    except Exception as e:
        logger.error('get_service_types(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if not service_type_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Service type not found')
    
    try:
        pop_exists = db_query.get_pops(db, pop_id=service['pop_id'])
    except Exception as e:
        logger.error('get_pop(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if not pop_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Pop not found')

def check_query_parameters(contact: schemas.ContactSearch) -> None:
    if contact.client_id and contact.service_id and contact.vendor_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='client_id, service_id, and vendor_id cannot be provided at the same time')
    
    if contact.client_name and contact.vendor_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='client_name and vendor_name cannot be provided at the same time')
    
    if contact.service_id and contact.service_point:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='service_id and service_point both cannot be provided at the same time')
    
    if contact.client_id and contact.client_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='client_id and client_name both cannot be provided at the same time')
    
    if contact.vendor_id and contact.vendor_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='vendor_id and vendor_name both cannot be provided at the same time')
   
    if contact.designation or contact.type:
        if not any(param for param in [contact.client_id, contact.service_id, contact.vendor_id, contact.client_name, contact.service_point, contact.vendor_name]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Must give at least one query parameter(client_id, service_id, vendor_id, client_name, service_point, vendor_name) when designation or contact_type is provided')
    
    if contact.service_point and not contact.client_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Must give query parameter client_name when service_name is provided')

def convert_names_to_ids(db: Session, client_name: str | None, service_point: str | None, vendor_name: str | None) -> int:
    if client_name and service_point:
        try:
            services = db_query.get_services(db, service_point=service_point)
        except Exception as e:
            logger.error('get_services(): %s', e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
        
        if not services:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Service point not found')
        
        return services[0].id
        
    
    if client_name:
        try:
            clients = db_query.get_clients(db, client_name=client_name)
        except Exception as e:
            logger.error('get_clients(): %s', e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
        
        if not clients:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Client not found')

        return clients[0].id
    
    if vendor_name:
        try:
            vendors = db_query.get_vendors(db, vendor_name=vendor_name)
        except Exception as e:
            logger.error('get_vendors(): %s', e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
        
        if not vendors:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Vendor not found')

        return vendors[0].id
        

#-- API routes --#

# client and client types query, add, update & delete #
@router.get("/clients", response_model=list[schemas.ClientDetails], summary='Get client list', tags=['Clients'])
def get_clients(client_name: str | None = None, client_type: str | None = None, client_id: int | None = None, page: int = 0, page_size: int = 10, db: Session = Depends(get_db)):
    if not client_name and not client_type and not client_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You must give at least one query parameter(client_name, client_type, client_id)')
    
    offset = page * page_size
    try:
        client_list =  db_query.get_clients(db, client_name=client_name, client_type=client_type, client_id=client_id, offset=offset, limit=page_size)
    except Exception as e:
        logger.error('get_client_list(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if not client_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    return client_list
    
@router.get("/client/types", response_model=list[schemas.ClientType], summary='Get client type list', tags=['Clients'])
def get_client_types(type_name: str | None = None, type_id: int | None = None, page: int = 0, page_size: int = 10, db: Session = Depends(get_db)):
    offset = page * page_size
    try:
        client_types = db_query.get_client_types(db, type_name=type_name, type_id=type_id, offset=offset, limit=page_size)
    except Exception as e:
        logger.error('get_client_types(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e

    if not client_types:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    return client_types
@router.post("/client", response_model=schemas.Client, summary='Add a client', tags=['Clients'])
def create_client(client: schemas.ClientBase, db: Session = Depends(get_db)):
    try:
        client_exists = db_query.get_client_by_name_and_type(db, client_name=client.name, client_type_id=client.client_type_id)
    except Exception as e:
        logger.error('get_client_by_name_and_type(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if client_exists:
        raise HTTPException(status_code=400, detail="Client exists")
    
    try:
        client_type_exists = db_query.get_client_type_by_id(db, client_type_id=client.client_type_id)
    except Exception as e:
        logger.error('get_client_type_by_id(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if not client_type_exists:
        raise HTTPException(status_code=400, detail='Client type does not exist')
    
    return db_query.add_client(db=db, client=client)

@router.post("/client/type", response_model=schemas.ClientType, summary='Add a client type', tags=['Clients'])
def add_client_type(client_type: schemas.ClientTypeBase, db: Session = Depends(get_db)):
    try:
        client_type_exists = db_query.get_client_types(db, type_name=client_type.name)
    except Exception as e:
        logger.error('get_client_type(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if client_type_exists:
        raise HTTPException(status_code=400, detail="Client type exists")
    
    return db_query.add_client_type(db=db, client_type=client_type)

@router.put("/client", response_model=schemas.Client, summary='Modify a client', tags=['Clients'])
def update_client(client: schemas.Client, db: Session = Depends(get_db)):
    try:
        client_id = db_query.get_client_by_id(db, client_id=client.id)
    except Exception as e:
        logger.error('get_client_by_id(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if not client_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Client id not found")
    
    try:
        client_type = db_query.get_client_type_by_id(db, client_type_id=client.client_type_id)
    except Exception as e:
        logger.error('get_client_type_by_id(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if not client_type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Client type not found')
    
    try:
        client_name_and_type = db_query.get_client_by_name_and_type(db, client_name=client.name, client_type_id=client.client_type_id)
    except Exception as e:
        logger.error('get_client_by_name_and_type(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if client_name_and_type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Existing client data and submitted client data same')
    
    return db_query.modify_client(db=db, client=client)

@router.delete("/client/type/{client_type_id}", response_model=schemas.EntryDelete, summary='Delete a client type', tags=['Clients'])
def delete_client_type(client_type_id: int, db: Session = Depends(get_db)) -> schemas.EntryDelete:
    try:
        client_type_exists = db_query.get_client_type_by_id(db, client_type_id=client_type_id)
    except Exception as e:
        logger.error('get_client_type_by_id(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if not client_type_exists:
        raise HTTPException(status_code=400, detail="Client type not found")
    
    try:
        db_query.delete_client_type(db=db, client_type_id=client_type_id)
    except IntegrityError as e:
        logger.error('delete_client_type(): %s', e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot delete client type with active clients') from e
    except Exception as e:
        logger.error('delete_client_type(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Cannot delete client type due to internal server error') from e
    
    return schemas.EntryDelete(message='Client type deleted', id=client_type_id)
    
@router.delete("/client/{client_id}", summary='Delete a client', tags=['Clients'])
def delete_client(client_id: int, db: Session = Depends(get_db)) -> schemas.EntryDelete:
    try:
        client_exists = db_query.get_client_by_id(db, client_id=client_id)
    except Exception as e:
        logger.error('get_client_by_id(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if not client_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Client not found")
    
    try:
        db_query.delete_client(db=db, client_id=client_id)
    except Exception as e:
        logger.error('delete_client(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    return schemas.EntryDelete(message='Client deleted', id=client_id)
    
# Service and service types add, update and delete #
@router.get("/services", response_model=list[schemas.ServiceDetails], summary='Search service', tags=['Services'])
def get_services(service_point: str | None = None, client_name: str | None = None, pop_name: str | None = None, page: int = 0, page_size: int = 10, db: Session = Depends(get_db)):    
    if not service_point and not client_name and not pop_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Must provide at least one (service_name,client_name,pop_name')

    offset = page * page_size
    service_list =  db_query.get_services(db=db, service_point=service_point, client_name=client_name, pop_name=pop_name, offset=offset, limit=page_size)
    if not service_list:
        logger.warning('No service named "%s"', service_point)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No service found')
    
    return service_list
@router.get("/service/types", response_model=list[schemas.ServiceType], summary='Search service type', tags=['Services'])
def get_service_types(type_name: str | None = None, type_id: int | None = None, page: int = 0, page_size: int = 10, db: Session = Depends(get_db)):
    offset = page * page_size
    try:
        service_type_list =  db_query.get_service_types(db=db, type_name=type_name, type_id=type_id, offset=offset, limit=page_size)
    except Exception as e:
        logger.error('get_service_type_list(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if not service_type_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No service types found')
    
    return service_type_list

@router.post("/service/type", response_model=schemas.ServiceType, summary='Add a service type', tags=['Services'])
def add_service_type(service_type: schemas.ServiceTypeBase, db: Session = Depends(get_db)):
    '''
    ## Add service type
    - **name**: Service type name* 
    - **description**: Description

    *Required
    '''
    try:
        service_type_exists = db_query.get_service_types(db, type_name=service_type.name)
    except Exception as e:
        logger.error('add_service_type() - failed to get service types using get_service_types(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if service_type_exists:
        raise HTTPException(status_code=400, detail="Service type exists")
    
    try:
        return db_query.add_service_type(db=db, service_type=service_type)
    except Exception as e:
        logger.error('add_service_type(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
@router.post("/service", response_model=schemas.Service, summary='Add a service', tags=['Services'])
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
    check_service_data(db, service.model_dump())

    try:
        client_exists = db_query.get_clients(db, client_id=service.client_id)
    except Exception as e:
        logger.error('get_clients(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if not client_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Client not found')
    
    try:
        service_type_exists = db_query.get_service_types(db, type_id=service.service_type_id)
    except Exception as e:
        logger.error('get_service_types(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if not service_type_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Service type not found')
    
    try:
        pop_exists = db_query.get_pops(db, pop_id=service.pop_id)
    except Exception as e:
        logger.error('get_pop(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if not pop_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Pop not found')

    try:
        service_exists = db_query.get_service_by_properties(db=db, service=service)
    except Exception as e:
        logger.error('get_service_by_properties(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if service_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Service exists')
    
    return db_query.add_service(db=db, service=service)

@router.put("/service", response_model=schemas.Service, summary='Modify a service', tags=['Services'])
def update_service(service: schemas.Service, db: Session = Depends(get_db)):
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

    try:
        service_exists = db_query.get_services(db=db, service_id=service.id)
    except Exception as e:
        logger.error('get_services(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if not service_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Service not found')
    
    check_service_data(db, service.model_dump())
    
    try:
        return db_query.modify_service(db=db, service=service)
    except Exception as e:
        logger.error('modify_service(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e

@router.delete("/service/type/{service_type_id}", summary='Delete a service type', tags=['Services'])
def delete_service_type(service_type_id: int, db: Session = Depends(get_db)):
    service_type_exists = db_query.get_service_type_by_id(db, service_type_id=service_type_id)
    if not service_type_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Service type not found")
    
    try:
        db_query.delete_service_type(db=db, service_type_id=service_type_id)
    except Exception as e:
        logger.error('delete_service_type(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e

    return JSONResponse(content={'message': 'Service type deleted', 'id': service_type_id})

@router.delete("/service/{service_id}", response_model=schemas.EntryDelete, summary='Modify a service', tags=['Services'])
def delete_service(service_id: int, db: Session = Depends(get_db)):
    service_exists = db_query.get_services(db=db, service_id=service_id)
    if not service_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Service not found')
    
    try:
        db_query.delete_service(db=db, service_id=service_id)
    except Exception as e:
        logger.error('delete_service(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    return JSONResponse(content={'message': 'Service deleted', 'id': service_id})

# Contacts add, update & delete #
@router.get("/contacts", response_model=list[schemas.ContactDetails], summary='Get contact list', tags=['Contacts'])
def get_contacts(contact_id: int | None = None, contact_name: str | None = None, designation: str | None = None, contact_type: typing_extensions.Literal['Admin', 'Technical', 'Billing'] | None = None, phone1: str | None = None, email: str | None = None, client_id: int | None = None, service_id: int | None = None, vendor_id: int | None = None, client_name: str | None = None, service_point: str | None = None, vendor_name: str | None = None, page: int = 0, page_size: int = 10, db: Session = Depends(get_db)):
     
    offset = page * page_size

    contact = schemas.ContactSearch(id=contact_id, name=contact_name, designation=designation, type=contact_type, phone1=phone1, email=email, client_id=client_id, service_id=service_id, vendor_id=vendor_id, client_name=client_name, service_point=service_point, vendor_name=vendor_name)
    
    if all (value is None for porperty, value in vars(contact).items()): 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No query parameters')

    check_query_parameters(contact)
    
    convert_names_to_ids(db, client_name=client_name, service_point=service_point, vendor_name=vendor_name)
    
    contact = schemas.ContactSearch(id=contact_id, name=contact_name, type=contact_type, designation=designation, phone1=phone1, email=email, client_id=client_id, service_id=service_id, vendor_id=vendor_id)
    try:
        contact_list = db_query.get_contacts(db, contact=contact, offset=offset, limit=page_size)
    except Exception as e:
        logger.error('get_contact_list(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if not contact_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact not found')
    
    return contact_list

@router.post("/contact", response_model=schemas.Contact, summary='Add a contact', tags=['Contacts'])
def add_contact(contact: schemas.ContactBase, db: Session = Depends(get_db)):
    """
    ## Add a contact
    - **name**: Full name*
    - **designation**: Designation of the person*
    - **type**: 'Admin'/'Technical'/'Billing' *
    - **phone1**: Phone number*
    - **phone2**: Phone number
    - **phone3**: Phone number
    - **email**: Email address
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
    
    try:
        contact_exists = db_query.get_contacts_by_properties(db=db, contact=contact)
    except Exception as e:
        logger.error('get_contacts_by_properties(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if contact_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Contact exists')

    try:
        return db_query.add_contact(db=db, contact=contact)
    except Exception as e:
        logger.error('add_contact(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e

@router.put("/contact", response_model=schemas.Contact, summary='Modify a contact', tags=['Contacts'])
def update_contact(contact: schemas.Contact, db: Session = Depends(get_db)):
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
    contact_exists = db_query.get_contact_by_id(db, contact_id=contact.id)
    if not contact_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Contact not found')
    
    ids = {'client_id': contact.client_id, 'service_id': contact.service_id, 'vendor_id': contact.vendor_id}
    check = check_id_presence(db=db, ids=ids)
    if check.failed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=check.message)

    phone_numbers = (contact.phone1, contact.phone2, contact.phone3)
    check = check_phone_number_length(phone_numbers=phone_numbers)
    if check.failed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=check.message)

    try:
        return db_query.update_contact(db=db, contact=contact)
    except Exception as e:
        logger.error('modify_contact(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e

@router.delete("/contact/{contact_id}", summary='Delete a contact', tags=['Contacts'])
def delete_contact(contact_id: int, db: Session = Depends(get_db)) -> schemas.EntryDelete:
    try:
        contact_exists = db_query.get_contact_by_id(db, contact_id=contact_id)
    except Exception as e:
        logger.error('get_contact_by_id(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if not contact_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Contact not found")
    
    try:
        db_query.delete_contact(db=db, contact_id=contact_id)
    except Exception as e:
        logger.error('delete_contact(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    return schemas.EntryDelete(message='Contact deleted', id=contact_id)

# Address add, update & modify #
@router.get("/addresses", response_model=list[schemas.AddressDetails], summary='Search address', tags=['Addresses'])
def get_addresses(flat: str | None = None, floor: str | None = None, holding: str | None = None, street: str | None = None, area: str | None = None, thana: str | None = None, district: str | None = None, client_id: int | None = None, service_id: int | None = None, vendor_id: int | None = None, client_name: str | None = None, service_point: str | None = None, vendor_name: str | None = None, extra_info: str | None = None, page: int = 0, page_size: int = 20, db: Session = Depends(get_db)):
    '''
    ## Search addresses
    - **flat**: Flat name 
    - **floor**: Floor number
    - **holding**: Holding number
    - **area**: Area name (Para/Moholla/Block/Sector/Housing society name etc.)
    - **street**: Street name or number
    - **thana**: Thana name
    - **district**: District name
    - **client_id**: Client id
    - **service_id**: Service id
    - **vendor_id**: Vendor id
    - **client_name**: Client name
    - **service_point**: Service point
    - **vendor_name**: Vendor name
    - **extra_info**: Extra info (remark, description, landmark etc)
    '''
    
    address_properties = schemas.AddressSearch(flat=flat, floor=floor, holding=holding, street=street, area=area, thana=thana, district=district, client_id=client_id, service_id=service_id, vendor_id=vendor_id, client_name=client_name, service_point=service_point, vendor_name=vendor_name, extra_info=extra_info)

    if address_properties.all_none_values():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Must provide at least one search parameter')
    
    offset = page * page_size
    
    try:
        address_list =  db_query.get_addresses(db=db, address_properties=address_properties, offset=offset, limit=page_size)
    except Exception as e:
        logger.error('get_addresses(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if not address_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    return address_list
@router.post("/address", summary='Add an address', tags=['Addresses'])
def add_address(address: schemas.AddressBase, db: Session = Depends(get_db)) -> schemas.Address:
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
    address_properties = schemas.AddressSearch(flat=address.flat, floor=address.floor, holding=address.holding, area=address.area, street=address.street, thana=address.thana, district=address.district, client_id=address.client_id, service_id=address.service_id, vendor_id=address.vendor_id, extra_info=address.extra_info)

    address_exists = db_query.get_addresses(db=db, address_properties=address_properties)
    if address_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Address exists")

    ids = {'client_id': address.client_id, 'service_id': address.service_id, 'vendor_id': address.vendor_id}
    check = check_id_presence(db=db, ids=ids)
    if check.failed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=check.message)
    
    try:
        return db_query.add_address(db=db, address=address)
    except Exception as e:
        logger.error('add_address(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e

@router.put("/address", summary='Modify an address', tags=['Addresses'])
def modify_address(address: schemas.Address, db: Session = Depends(get_db)) -> schemas.Address:
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
    
    try:
        return db_query.modify_address(db=db, address=address)
    except Exception as e:
        logger.error('modify_address(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e

@router.delete("/address/{address_id}", summary='Delete an address', tags=['Addresses'])
def remove_address(address_id: int, db: Session = Depends(get_db)) -> schemas.EntryDelete:
    address_exists = db_query.get_address_by_id(db, address_id=address_id)
    if not address_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    
    try:
        db_query.delete_address(db=db, address_id=address_id)
    except Exception as e:
        logger.error('remove_address(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    return schemas.EntryDelete(message='Address deleted', id=address_id)

# Vendors add, update & modify #
@router.get("/vendors", response_model=list[schemas.VendorDetails], summary='Search vendor', tags=['Vendors'])
def get_vendors(vendor_name: str | None = None, 
                vendor_type: str | None = None, 
                vendor_id: int | None = None, 
                page: int = 0, page_size: int = 10, 
                db: Session = Depends(get_db)):    
    if not vendor_name and not vendor_type and not vendor_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You must give at least one query parameter')
    
    offset = page * page_size
    try:
        vendor_list =  db_query.get_vendors(db=db, 
                                                vendor_name=vendor_name, 
                                                vendor_type=vendor_type, 
                                                vendor_id=vendor_id, 
                                                offset=offset, limit=page_size)
    except Exception as e:
        logger.error('get_vendors(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if not vendor_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    return vendor_list
@router.post("/vendor", summary='Add a vendor', tags=['Vendors'])
def add_vendor(vendor: schemas.VendorBase, db: Session = Depends(get_db)) -> schemas.Vendor:
    '''
    ## Add vendor
    - **name**: Vendor name*
    - **type**: 'LSP'/'NTTN'/'ISP'* 

    **Note**: *Required items
    '''
   
    vendor_exists = db_query.get_vendor_by_properties(db=db, vendor=vendor)
    if vendor_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Vendor exists')
    
    try:
        return db_query.add_vendor(db=db, vendor=vendor)
    except Exception as e:
        logger.error('add_vendor(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e

@router.put("/vendor", summary='Modify a vendor', tags=['Vendors'])
def update_vendor(vendor: schemas.Vendor, db: Session = Depends(get_db)) -> schemas.Vendor: 
    '''
    ## Add vendor
    - **id**: Vendor id*
    - **name**: Vendor name*
    - **type**: 'LSP'/'NTTN'/'ISP'* 

    **Note**: *Required items
    '''
   
    vendor_exists = db_query.get_vendor_by_id(db=db, vendor_id=vendor.id)
    if not vendor_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Vendor not found')
    
    try:
        return db_query.modify_vendor(db=db, vendor=vendor)
    except Exception as e:
        logger.error('modify_vendor(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e

@router.delete("/vendor/{vendor_id}", summary='Delete a vendor', tags=['Vendors'])
def delete_vendor(vendor_id: int, db: Session = Depends(get_db)) -> schemas.EntryDelete:
    vendor_exists = db_query.get_vendor_by_id(db=db, vendor_id=vendor_id)
    if not vendor_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Vendor not found')
    
    try:
        db_query.delete_vendor(db=db, vendor_id=vendor_id)
    except IntegrityError as e:
        logger.error('remove_vendor(): %s', e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot delete vendor with active pop') from e
    except Exception as e:
        logger.error('remove_vendor(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e

    return schemas.EntryDelete(message='Vendor deleted', id=vendor_id)

# Pops add, update & delete #
@router.get("/pops", response_model=list[schemas.PopDetails], summary='Search pop', tags=['Pops'])
def get_pops(pop_name: str | None = None, pop_owner: str | None = None, pop_id: int | None = None, page: int = 0, page_size: int = 10, db: Session = Depends(get_db)):
    if not pop_name and not pop_owner and not pop_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You must give at least one query parameter(pop_name,pop_owner,pop_id)')
    
    offset = page * page_size
    try:
        pop_list =  db_query.get_pops(db=db, pop_name=pop_name, pop_owner=pop_owner, pop_id=pop_id, offset=offset, limit=page_size)
    except Exception as e:
        logger.error('get_pops(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if not pop_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    return pop_list

@router.post("/pop", summary='Add a pop', tags=['Pops'])
def add_pop(pop: schemas.PopBase, db: Session = Depends(get_db)) -> schemas.Pop:
    '''
    ## Add Pop
    - **name**: Pop name*
    - **owner**: Vendor id*
    - **extra_info**: Any extra information 

    **Note**: *Required items
    '''
    pop_owner = db_query.get_vendors(db=db, vendor_id=pop.owner)
    if not pop_owner:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Vendor not found')
    
    pop_exists = db_query.get_pop_by_properties(db=db, pop=pop)
    if pop_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Pop exists')
    
    try:
        return db_query.add_pop(db=db, pop=pop)
    except Exception as e:
        logger.error('add_pop(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e

@router.put("/pop", summary='Modify a pop', tags=['Pops'])
def update_pop(pop: schemas.Pop, db: Session = Depends(get_db)) -> schemas.Pop:
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Vendor not found')
    
    pop_exists = db_query.get_pop_by_id(db=db, pop_id=pop.id)
    if not pop_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Pop not found')
    
    try:
        return db_query.modify_pop(db=db, pop=pop)
    except Exception as e:
        logger.error('modify_pop(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e

@router.delete("/pop/{pop_id}", summary='Delete a pop', tags=['Pops'])
def remove_pop(pop_id: int, db: Session = Depends(get_db)) -> schemas.EntryDelete:
    pop_exists = db_query.get_pop_by_id(db=db, pop_id=pop_id)
    if not pop_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Pop not found')
    
    vendor_deleted = db_query.delete_pop(db=db, pop_id=pop_id)
    if vendor_deleted != pop_id:
        logger.warning('%s', vendor_deleted)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot delete pop, may be this pop is assigned to any service')
    
    return schemas.EntryDelete(message='Pop deleted', id=pop_id)