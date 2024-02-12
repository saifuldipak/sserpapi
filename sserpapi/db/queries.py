# pylint: disable=E0401
import logging
from sqlalchemy.orm import Session, joinedload
import db.models as models
import pydantic_schemas as schemas
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)

#-- Table 'clients' queries --#
def get_client_types(db: Session, offset: int = 0, limit: int = 100):
    return db.query(models.ClientTypes).offset(offset).limit(limit).all()

def get_client_type(db: Session, client_type: str):
    return db.query(models.Clients).filter(models.ClientTypes.name==client_type).first()

def get_client_type_by_id(db: Session, client_type_id: int):
    return db.query(models.ClientTypes).filter(models.ClientTypes.id==client_type_id).first()

def get_client_by_id(db: Session, client_id: int):
    return db.query(models.Clients).filter(models.Clients.id==client_id).first()

def get_client(db: Session, client_id: int):
    return db.query(models.Clients).filter(models.Clients.id==client_id).first()

def get_client_by_name_and_type(db: Session, client_name: str, client_type_id: int):
    return db.query(models.Clients).filter(models.Clients.name==client_name, models.Clients.client_type_id==client_type_id).first()

def get_client_list(db: Session, client_name: str | None = None, client_type: str | None = None, offset: int = 0, limit: int = 10):
    base_query = db.query(models.Clients)

    if (client_name):
        client_name_string = f'{client_name}%'

    if (client_type):
        client_type_string = f'{client_type}%'

    if client_name and not client_type:
        base_query=  base_query.filter(models.Clients.name.ilike(client_name_string))
    elif not client_name and client_type:
        base_query = base_query.filter(models.ClientTypes.name.ilike(client_type_string))
    elif client_name and client_type:
        base_query = base_query.filter(models.Clients.name.ilike(client_name_string), models.ClientTypes.name.ilike(client_type_string))

    return base_query.offset(offset).limit(limit).all()

def add_client(db: Session, client: schemas.ClientBase):
    new_client = models.Clients(name=client.name, client_type_id=client.client_type_id)
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return new_client

def add_client_type(db: Session, client_type: schemas.ClientTypeBase):
    new_client_type = models.ClientTypes(name=client_type.name)
    db.add(new_client_type)
    db.commit()
    db.refresh(new_client_type)
    return new_client_type

def modify_client(db: Session, client: schemas.Client):
    client_in_db = db.query(models.Clients).filter(models.Clients.id==client.id).first()
    client_in_db.name = client.name
    client_in_db.client_type_id = client.client_type_id 
    db.commit()
    db.refresh(client_in_db)
    return client_in_db

def delete_client(db: Session, client_id: int):
    client = db.query(models.Clients).filter(models.Clients.id==client_id).first()
    db.delete(client)
    db.commit()
    return client_id

def delete_client_type(db: Session, client_type_id: int):
    client_type = db.query(models.ClientTypes).filter(models.ClientTypes.id==client_type_id).first()
    db.delete(client_type)
    db.commit()
    return client_type_id

#-- Table 'services' queries --#
def get_services(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Services).offset(skip).limit(limit).all()

def get_service_by_properties(db: Session, service: schemas.ServiceBase):
    return db.query(models.Services).filter(models.Services.client_id==service.client_id, models.Services.point==service.point, models.Services.service_type_id==service.service_type_id, models.Services.bandwidth==service.bandwidth, models.Services.extra_info==service.extra_info).first()

def get_service_list(db: Session, service_point: str | None = None, client_name: str | None = None, offset: int = 0, limit: int = 50):
    base_query = db.query(models.Services)
    if service_point:
        sevice_point_string = f'{service_point}%'
    
    if client_name:
        client_name_string = f'{client_name}%'
        base_query = base_query.join(models.Clients)

    if service_point and not client_name:
        base_query=  base_query.filter(models.Services.point.ilike(sevice_point_string))
    elif not service_point and client_name:
        base_query = base_query.filter(models.Clients.name.ilike(client_name_string))
    elif service_point and client_name:
        base_query = base_query.filter(models.Services.point.ilike(sevice_point_string), models.Clients.name.ilike(client_name_string))
    
    return base_query.offset(offset).limit(limit).all()

def get_service_type_by_name(db: Session, service_type: schemas.ServiceTypeBase):
    return db.query(models.ServiceTypes).filter(models.ServiceTypes.name==service_type.name).first()

def get_service_by_id(db: Session, service_id: int):
    return db.query(models.Services).filter(models.Services.id==service_id).first()

def get_service_type_by_id(db: Session, service_type_id: int):
    return db.query(models.ServiceTypes).filter(models.ServiceTypes.id==service_type_id).first()

def get_service_type_list(db: Session, service_type: str | None = None, offset: int = 0, limit: int = 10):
    if service_type:
        sevice_type_string = f'{service_type}%'
        return db.query(models.ServiceTypes).filter(models.ServiceTypes.name.ilike(sevice_type_string)).offset(offset).limit(limit).all()
    else:
        return db.query(models.ServiceTypes).offset(offset).limit(limit).all()

def add_service(db: Session, service: schemas.ServiceBase):
    new_service = models.Services(**service.model_dump())
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return new_service

def add_service_type(db: Session, service_type: schemas.ServiceTypeBase):
    new_service_type = models.ServiceTypes(name=service_type.name, description=service_type.description)
    db.add(new_service_type)
    db.commit()
    db.refresh(new_service_type)
    return new_service_type

def modify_service(db: Session, service: schemas.Service):
    service_in_db = db.query(models.Services).filter(models.Services.id==service.id).first()
    service_in_db.client_id = service.client_id
    service_in_db.point = service.point
    service_in_db.service_type_id = service.service_type_id
    service_in_db.bandwidth = service.bandwidth
    service_in_db.pop_id = service.pop_id
    service_in_db.extra_info = service.extra_info
    db.commit()
    db.refresh(service_in_db)
    return service_in_db

def delete_service(db: Session, service_id: int) -> any:
    service_in_db = db.query(models.Services).filter(models.Services.id==service_id).first()
    db.delete(service_in_db)
    db.commit()
    return service_id

def delete_service_type(db: Session, service_type_id: int):
    service_type = db.query(models.ServiceTypes).filter(models.ServiceTypes.id==service_type_id).first()
    db.delete(service_type)
    db.commit()
    return service_type_id

#-- Table 'contacts' queries --#
def add_contact(db: Session, contact: schemas.ContactBase):
    new_contact = models.Contacts(**contact.model_dump())
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact

def get_contact_list(
        db: Session, 
        client_name: str | None = None,
        service_point: str | None = None,
        vendor_name: str | None = None,
        offset: int = 0, 
        limit: int = 100
        ):    
    
    base_query = db.query(models.Contacts)
    
    if client_name and service_point:
        client_name_string = f'{client_name}%'
        service_point_string = f'{service_point}%'
        base_query = (
            base_query
            .join(models.Clients)
            .join(models.Services)
            .options(joinedload(models.Contacts.clients))
            .options(joinedload(models.Contacts.services))
            .filter(models.Clients.name.ilike(client_name_string))
            .filter(models.Services.point.ilike(service_point_string))
        )
    elif client_name:
        client_name_string = f'{client_name}%'
        base_query = (
            base_query
            .join(models.Clients)
            .options(joinedload(models.Contacts.clients))
            .filter(models.Clients.name.ilike(client_name_string))
        )
    elif vendor_name:
        vendor_name_string = f'{vendor_name}%'
        base_query = (
            base_query
            .join(models.Vendors)
            .options(joinedload(models.Contacts.vendors))
            .filter(models.Vendors.name.ilike(vendor_name_string))
        )
    
    return base_query.offset(offset).limit(limit).all()

def get_contact_by_id(db: Session, contact_id: int):
    contact = db.query(models.Contacts).filter(models.Contacts.id==contact_id).first()
    return contact

def modify_contact(db: Session, contact: schemas.Contact):
    contact_in_db = db.query(models.Contacts).filter(models.Contacts.id==contact.id).first()
    
    contact_in_db.name = contact.name
    contact_in_db.designation = contact.designation
    contact_in_db.type = contact.type
    contact_in_db.phone1 = contact.phone1
    contact_in_db.phone2 = contact.phone2
    contact_in_db.phone3 = contact.phone3
    contact_in_db.client_id = contact.client_id
    contact_in_db.vendor_id = contact.vendor_id
    contact_in_db.service_id = contact.service_id

    db.commit()
    db.refresh(contact_in_db)
    return contact_in_db

def delete_contact(db: Session, contact_id: int):
    contact = db.query(models.Contacts).filter(models.Contacts.id==contact_id).first()
    db.delete(contact)
    db.commit()
    return contact_id

#-- Table 'addresses' queries --#
def get_address_by_id(db: Session, address_id: int):
    return db.query(models.Addresses).filter(models.Addresses.id==address_id).first()

def get_address_list(db: Session, client_name: str | None = None, service_point: str | None = None, vendor_name: str | None = None, offset: int = 0, limit: int = 20):
    base_query = db.query(models.Addresses)

    if client_name:
        client_name_string = f'{client_name}%'        
        base_query = (
            base_query
            .join(models.Clients)
            .options(joinedload(models.Addresses.clients))
            .filter(models.Clients.name.ilike(client_name_string))
        )

    if service_point:
        service_point_string = f'{service_point}%'
        base_query = (
            base_query
            .join(models.Services)
            .options(joinedload(models.Addresses.services))
            .filter(models.Services.point.ilike(service_point_string))
        )

    if vendor_name:
        vendor_name_string = f'{vendor_name}%'
        base_query = (
            base_query
            .join(models.Vendors)
            .options(joinedload(models.Addresses.vendors))
            .filter(models.Vendors.name.ilike(vendor_name_string))
        )

    return base_query.offset(offset).limit(limit).all()

def add_address(db: Session, address: schemas.AddressBase):
    new_address = models.Addresses(**address.model_dump())
    db.add(new_address)
    db.commit()
    db.refresh(new_address)
    return new_address

def modify_address(db: Session, address: schemas.Address):
    address_in_db = db.query(models.Addresses).filter(models.Addresses.id==address.id).first()
    address_in_db.flat = address.flat
    address_in_db.floor = address.floor
    address_in_db.holding = address.holding
    address_in_db.street = address.street
    address_in_db.area = address.area
    address_in_db.thana = address.thana
    address_in_db.district = address.district
    address_in_db.client_id = address.client_id
    address_in_db.service_id = address.service_id
    address_in_db.vendor_id = address.vendor_id
    db.commit()
    db.refresh(address_in_db)
    return address_in_db

def delete_address(db: Session, address_id: int):
    address = db.query(models.Addresses).filter(models.Addresses.id==address_id).first()
    db.delete(address)
    db.commit()
    return address_id

#-- Table 'vendors' queries --#
def get_vendor_by_name(db: Session, vendor: schemas.VendorBase):
    return db.query(models.Vendors).filter(models.Vendors.name==vendor.name).first()

def get_vendor_list(db: Session, vendor_name: str | None = None, vendor_type: str | None = None, offset: int = 0, limit: int = 100):
    base_query = db.query(models.Vendors)

    if vendor_name:
        vendor_name_string = f'{vendor_name}%'
    
    if vendor_type:
        vendor_type_string = f'{vendor_type}%'
    
    if vendor_name and not vendor_type:
        base_query = base_query.filter(models.Vendors.name.ilike(vendor_name_string))
    elif not vendor_name and vendor_type:
        base_query = base_query.filter(models.Vendors.type.ilike(vendor_type_string))
    elif vendor_name and vendor_type:
        base_query = base_query.filter(models.Vendors.name.ilike(vendor_name_string), models.Vendors.type.ilike(vendor_type_string))

    return base_query.offset(offset).limit(limit).all()

def get_vendor_by_properties(db: Session, vendor: schemas.VendorBase):
    return db.query(models.Vendors).filter(models.Vendors.name==vendor.name, models.Vendors.type==vendor.type).first()

def get_vendor_by_id(db: Session, vendor_id: int):
    return db.query(models.Vendors).filter(models.Vendors.id==vendor_id).first()

def add_vendor(db: Session, vendor: schemas.VendorBase):
    new_vendor = models.Vendors(**vendor.model_dump())
    db.add(new_vendor)
    db.commit()
    db.refresh(new_vendor)
    return new_vendor

def modify_vendor(db: Session, vendor: schemas.Vendor):
    vendor_in_db = db.query(models.Vendors).filter(models.Vendors.id==vendor.id).first()
    vendor_in_db.name = vendor.name
    vendor_in_db.type = vendor.type
    db.commit()
    db.refresh(vendor_in_db)
    return vendor_in_db

def delete_vendor(db: Session, vendor_id: int) -> int:
    vendor_in_db = db.query(models.Vendors).filter(models.Vendors.id==vendor_id).first()
    db.delete(vendor_in_db)
    db.commit()
    return vendor_id

#-- Table 'pops' queries --#
def get_pop_by_properties(db: Session, pop: schemas.PopBase):
    return db.query(models.Pops).filter(models.Pops.name==pop.name, models.Pops.owner==pop.owner).first()

def get_pop_by_id(db: Session, pop_id: int):
    return db.query(models.Pops).filter(models.Pops.id==pop_id).first()

def get_pop_list(db: Session, pop_name: str | None = None, pop_owner: str | None = None, offset: int = 0, limit: int = 10):
    base_query = (
        db.query(models.Pops)
        .outerjoin(models.Vendors)
        .outerjoin(models.Services)
        .options(joinedload(models.Pops.vendors))    
        .options(joinedload(models.Pops.services))
    )

    pop_name_string = f'{pop_name}%'
    pop_owner_string = f'{pop_owner}%'

    if pop_name and not pop_owner:
        base_query=  base_query.filter(models.Pops.name.ilike(pop_name_string))
    elif not pop_name and pop_owner:
        base_query = base_query.filter(models.Vendors.name.ilike(pop_owner_string))
    elif pop_name and pop_owner:
        base_query = base_query.filter(models.Pops.name.ilike(pop_name_string), models.Vendors.name.ilike(pop_owner_string))

    return base_query.offset(offset).limit(limit).all()

def add_pop(db: Session, pop: schemas.PopBase):
    new_pop = models.Pops(**pop.model_dump())
    db.add(new_pop)
    db.commit()
    db.refresh(new_pop)
    return new_pop

def modify_pop(db: Session, pop: schemas.Pop):
    pop_in_db = db.query(models.Pops).filter(models.Pops.id==pop.id).first()
    pop_in_db.name = pop.name
    pop_in_db.owner = pop.owner
    pop_in_db.extra_info = pop.extra_info
    db.commit()
    db.refresh(pop_in_db)
    return pop_in_db

def delete_pop(db: Session, pop_id: int) -> any:
    pop_in_db = db.query(models.Pops).filter(models.Pops.id==pop_id).first()
    try:
        db.delete(pop_in_db)
        db.commit()
    except IntegrityError as e:
        return f'Integrity error: {e}'
    
    return pop_id

#-- Table 'users' queries --#
def get_user_by_name(db: Session, user_name: str):
    return db.query(models.Users).filter(models.Users.user_name==user_name).first()

def get_users(db: Session, offset: int = 0, limit: int = 100):
    return db.query(models.Users).offset(offset).limit(limit).all()

def add_user(db: Session, user: schemas.User):
    new_user = models.Users(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user