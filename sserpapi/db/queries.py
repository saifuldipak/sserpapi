# pylint: disable=E0401
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DBAPIError
from sqlalchemy import delete
from sserpapi.db import models
import sserpapi.pydantic_schemas as schemas
from sserpapi.auth import get_password_hash

logger = logging.getLogger(__name__)

#-- Table 'clients' queries --#
def get_client_types(db: Session, type_name: str | None = None, type_id: int | None = None, offset: int = 0, limit: int = 100) -> list[models.ClientTypes]:
    base_query = db.query(models.ClientTypes)

    if type_name:
        client_type_name_string = f'{type_name}%'
        base_query = base_query.filter(models.ClientTypes.name.ilike(client_type_name_string))
    
    if type_id:
        base_query = base_query.filter(models.ClientTypes.id==type_id)

    try:
        return base_query.offset(offset).limit(limit).all()
    except Exception as e:
        raise e
    
def get_client_type(db: Session, client_type: str) -> models.ClientTypes:
    try:
        return db.query(models.Clients).filter(models.ClientTypes.name==client_type).first()
    except Exception as e:
        raise e
    
def get_client_type_by_id(db: Session, client_type_id: int) -> models.ClientTypes:
    try:
        return db.query(models.ClientTypes).filter(models.ClientTypes.id==client_type_id).first()
    except Exception as e:
        raise e
    
def get_client_by_id(db: Session, client_id: int) -> models.Clients:
    try:
        return db.query(models.Clients).filter(models.Clients.id==client_id).first()
    except Exception as e:
        raise e
    
def get_client(db: Session, client_id: int) -> models.Clients:
    try:
        return db.query(models.Clients).filter(models.Clients.id==client_id).first()
    except Exception as e:
        raise e

def get_client_by_name_and_type(db: Session, client_name: str, client_type_id: int) -> models.Clients:
    try:
        return db.query(models.Clients).filter(models.Clients.name==client_name, models.Clients.client_type_id==client_type_id).first()
    except Exception as e:
        raise e
def get_clients(db: Session, client_name: str | None = None, client_type: str | None = None, client_id: int | None = None, offset: int = 0, limit: int = 10) -> list[models.Clients]:
    if not client_name and not client_type and not client_id:
        raise TypeError('Must provide at least client_name, client_type or client_id')
    
    base_query = db.query(models.Clients)

    if (client_name):
        client_name_string = f'{client_name}%'

    if (client_type):
        client_type_string = f'{client_type}%'

    if client_name:
        base_query =  base_query.filter(models.Clients.name.ilike(client_name_string))

    if client_type:
        base_query = base_query.join(models.ClientTypes).filter(models.ClientTypes.name.ilike(client_type_string))

    if client_id:
        base_query = base_query.filter(models.Clients.id==client_id)

    try:
        return base_query.offset(offset).limit(limit).all()
    except Exception as e:
        raise e

def add_client(db: Session, client: schemas.ClientBase) -> models.Clients:
    try:
        new_client = models.Clients(**client.model_dump())
        db.add(new_client)
        db.commit()
        db.refresh(new_client)
    except Exception as e:
        raise e
    
    return new_client

def add_client_type(db: Session, client_type: schemas.ClientTypeBase) -> models.ClientTypes:
    try:
        new_client_type = models.ClientTypes(name=client_type.name)
        db.add(new_client_type)
        db.commit()
        db.refresh(new_client_type)
    except Exception as e:
        raise DBAPIError(str(new_client_type), [], e) from e

    return new_client_type

def modify_client(db: Session, client: schemas.Client) -> models.Clients:
    try:
        client_in_db = db.query(models.Clients).filter(models.Clients.id==client.id).first()
        client_in_db.name = client.name # type: ignore 
        client_in_db.client_type_id = client.client_type_id # type: ignore
        
        db.commit()
        db.refresh(client_in_db)
    except Exception as e:
        raise e
    
    return client_in_db

def delete_client(db: Session, client_id: int) -> int:
    stmt = delete(models.Clients).where(models.Clients.id==client_id)
    try:
        db.execute(stmt)
        db.commit()
    except IntegrityError as e:
        logger.error(e)
        raise IntegrityError from e
    except Exception as e:
        raise e
    
    return client_id

def delete_client_type(db: Session, client_type_id: int) -> int:
    stmt = delete(models.ClientTypes).where(models.ClientTypes.id==client_type_id)
    try:
        db.execute(stmt)
        db.commit()
    except IntegrityError as e:
        raise IntegrityError(str(stmt), [], e) from e
    except Exception as e:
        raise DBAPIError(str(stmt), [], e) from e
    
    return client_type_id

#-- Table 'services' queries --#
def get_service_by_properties(db: Session, service: schemas.ServiceBase) -> models.Services:
    try:
        return db.query(models.Services).filter(models.Services.client_id==service.client_id, models.Services.point==service.point, models.Services.service_type_id==service.service_type_id, models.Services.bandwidth==service.bandwidth, models.Services.extra_info==service.extra_info).first()
    except Exception as e:
        raise e
    
def get_services(db: Session, service_point: str | None = None, client_name: str | None = None, pop_name: str | None = None, service_id: int | None = None, offset: int = 0, limit: int = 50) -> list[models.Services]:
    base_query = db.query(models.Services)

    if client_name:
        client_name_string = f'{client_name}%'
        base_query = base_query.join(models.Clients).filter(models.Clients.name.ilike(client_name_string))

    if service_point:
        service_point_string = f'{service_point}%'
        base_query = base_query.filter(models.Services.point.ilike(service_point_string))

    if pop_name:
        pop_name_string = f'{pop_name}%'
        base_query = base_query.join(models.Pops).filter(models.Pops.name.ilike(pop_name_string))

    if service_id:
        base_query = base_query.filter(models.Services.id==service_id)
    
    try:
        return base_query.offset(offset).limit(limit).all()
    except Exception as e:
        raise DBAPIError(str(base_query), [], e) from e

def get_service_type_by_id(db: Session, service_type_id: int) -> models.ServiceTypes:
    try:
        return db.query(models.ServiceTypes).filter(models.ServiceTypes.id==service_type_id).first()
    except Exception as e:
        raise e

def get_service_types(db: Session, type_name: str | None = None, type_id: int | None = None, offset: int = 0, limit: int = 10) -> list[models.ServiceTypes]:
    base_query = db.query(models.ServiceTypes)

    if type_name:
        sevice_type_string = f'{type_name}%'
        base_query = base_query.filter(models.ServiceTypes.name.ilike(sevice_type_string))

    if type_id:
        base_query = base_query.filter(models.ServiceTypes.id==type_id)
    
    try:
        return base_query.offset(offset).limit(limit).all()
    except Exception as e:
        raise DBAPIError(str(base_query), [], e) from e

def add_service(db: Session, service: schemas.ServiceBase) -> schemas.Service:
    try:
        new_service = models.Services(**service.model_dump())
        db.add(new_service)
        db.commit()
        db.refresh(new_service)
    except Exception as e:
        raise e
    
    return new_service

def add_service_type(db: Session, service_type: schemas.ServiceTypeBase) -> schemas.ServiceType:
    try:
        new_service_type = models.ServiceTypes(**service_type.model_dump())
        db.add(new_service_type)
        db.commit()
        db.refresh(new_service_type)
    except Exception as e:
        raise e
    
    return new_service_type

def modify_service(db: Session, service: schemas.Service) -> schemas.Service:
    try:
        service_in_db = db.query(models.Services).filter(models.Services.id==service.id).first()
        service_in_db.client_id = service.client_id # type: ignore
        service_in_db.point = service.point # type: ignore
        service_in_db.service_type_id = service.service_type_id # type: ignore
        service_in_db.bandwidth = service.bandwidth # type: ignore
        service_in_db.pop_id = service.pop_id # type: ignore
        service_in_db.extra_info = service.extra_info # type: ignore
        db.commit()
        db.refresh(service_in_db)
    except Exception as e:
        raise e
    
    return service_in_db

def delete_service(db: Session, service_id: int) -> int:
    stmt = delete(models.Services).where(models.Services.id==service_id)
    try:
        db.execute(stmt)
        db.commit()
    except IntegrityError as e:
        raise IntegrityError from e
    except Exception as e:
        raise e
    
    return service_id

def delete_service_type(db: Session, service_type_id: int) -> int:
    stmt = delete(models.ServiceTypes).where(models.ServiceTypes.id==service_type_id)
    try:
        db.execute(stmt)
        db.commit()
    except Exception as e:
        raise e
    
    return service_type_id

#-- Table 'contacts' queries --#
def add_contact(db: Session, contact: schemas.ContactBase) -> schemas.Contact:
    try:
        new_contact = models.Contacts(**contact.model_dump())
        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)
    except Exception as e:
        raise e
    
    return new_contact

def get_contacts_by_properties(db: Session, contact: schemas.ContactBase):
    base_query = db.query(models.Contacts).filter(models.Contacts.name==contact.name, models.Contacts.designation==contact.designation, models.Contacts.type==contact.type)

    if contact.client_id:
        base_query = base_query.filter(models.Contacts.client_id==contact.client_id)

    if contact.service_id:
        base_query = base_query.filter(models.Contacts.service_id==contact.service_id)

    if contact.vendor_id:
        base_query = base_query.filter(models.Contacts.vendor_id==contact.vendor_id)

    try:
        return base_query.first()
    except Exception as e:
        raise e

def get_contacts(db: Session, contact: schemas.ContactSearch, offset: int = 0, limit: int = 100) -> list[models.Contacts]:    
    
    base_query = db.query(models.Contacts)

    if contact.id:
        base_query = base_query.filter(models.Contacts.id==contact.id)

    if contact.name:
        base_query = base_query.filter(models.Contacts.name.ilike(f"{contact.name}%"))

    if contact.designation:
        base_query = base_query.filter(models.Contacts.designation.ilike(f"{contact.designation}%"))
    
    if contact.type:
        base_query = base_query.filter(models.Contacts.type.ilike(f"{contact.type}%"))

    if contact.phone1:
        base_query = base_query.filter(models.Contacts.phone1.ilike(f"{contact.phone1}%"))

    if contact.email:
        base_query = base_query.filter(models.Contacts.email.ilike(f"{contact.email}%"))
    
    if contact.client_id:
        base_query = base_query.filter(models.Contacts.client_id==contact.client_id)

    if contact.service_id:    
        base_query = base_query.filter(models.Contacts.service_id==contact.service_id)
    
    if contact.vendor_id:
        base_query = base_query.filter(models.Contacts.vendor_id==contact.vendor_id)
    
    try:
        return base_query.offset(offset).limit(limit).all()
    except Exception as e:
        raise e

def get_contact_by_id(db: Session, contact_id: int) -> models.Contacts:
    try:
        return db.query(models.Contacts).filter(models.Contacts.id==contact_id).first()
    except Exception as e:
        raise e

def update_contact(db: Session, contact: schemas.Contact) -> models.Contacts:
    try:
        contact_in_db = db.query(models.Contacts).filter(models.Contacts.id==contact.id).first()
        
        contact_in_db.name = contact.name # type: ignore
        contact_in_db.designation = contact.designation # type: ignore
        contact_in_db.type = contact.type # type: ignore
        contact_in_db.phone1 = contact.phone1 # type: ignore
        contact_in_db.phone2 = contact.phone2 # type: ignore
        contact_in_db.phone3 = contact.phone3 # type: ignore
        contact_in_db.email = contact.email # type: ignore
        contact_in_db.client_id = contact.client_id # type: ignore
        contact_in_db.vendor_id = contact.vendor_id # type: ignore
        contact_in_db.service_id = contact.service_id # type: ignore

        db.commit()
        db.refresh(contact_in_db)
    except Exception as e:
        raise e
    
    return contact_in_db

def delete_contact(db: Session, contact_id: int) -> int:
    stmt = delete(models.Contacts).where(models.Contacts.id==contact_id)
    try:
        db.execute(stmt)
        db.commit()
    except IntegrityError as e:
        raise IntegrityError from e
    except Exception as e:
        raise e
    
    return contact_id

#-- Table 'addresses' queries --#
def get_address_by_id(db: Session, address_id: int) -> models.Addresses:
    try:
        return db.query(models.Addresses).filter(models.Addresses.id==address_id).first()
    except Exception as e:
        raise e

def get_addresses(db: Session, address_properties: schemas.AddressSearch, offset: int = 0, limit: int = 20) -> list[models.Addresses]:
    base_query = db.query(models.Addresses)
    
    if address_properties.flat:
        base_query = base_query.filter(models.Addresses.flat==address_properties.flat)
    
    if address_properties.floor:
        base_query = base_query.filter(models.Addresses.floor==address_properties.floor)

    if address_properties.holding:
        base_query = base_query.filter(models.Addresses.holding==address_properties.holding)

    if address_properties.street:
        base_query = base_query.filter(models.Addresses.street==address_properties.street)

    if address_properties.area:
        base_query = base_query.filter(models.Addresses.area==address_properties.area)

    if address_properties.thana:
        base_query = base_query.filter(models.Addresses.thana==address_properties.thana)

    if address_properties.district:
        base_query = base_query.filter(models.Addresses.district==address_properties.district)

    if address_properties.client_id:
        base_query = base_query.filter(models.Addresses.client_id==address_properties.client_id)

    if address_properties.service_id:
        base_query = base_query.filter(models.Addresses.service_id==address_properties.service_id)

    if address_properties.vendor_id:
        base_query = base_query.filter(models.Addresses.vendor_id==address_properties.vendor_id)

    try:
        return base_query.offset(offset).limit(limit).all()
    except Exception as e:
        raise e

def add_address(db: Session, address: schemas.AddressBase) -> models.Addresses:
    try:
        new_address = models.Addresses(**address.model_dump())
        db.add(new_address)
        db.commit()
        db.refresh(new_address)
    except Exception as e:
        raise e
    
    return new_address

def update_address(db: Session, address: schemas.Address) -> models.Addresses:
    try:
        address_in_db = db.query(models.Addresses).filter(models.Addresses.id==address.id).first()
        address_in_db.flat = address.flat # type: ignore
        address_in_db.floor = address.floor # type: ignore
        address_in_db.holding = address.holding # type: ignore
        address_in_db.street = address.street # type: ignore
        address_in_db.area = address.area # type: ignore
        address_in_db.thana = address.thana # type: ignore
        address_in_db.district = address.district # type: ignore
        address_in_db.client_id = address.client_id # type: ignore
        address_in_db.service_id = address.service_id # type: ignore
        address_in_db.vendor_id = address.vendor_id # type: ignore
        address_in_db.extra_info = address.extra_info # type: ignore
        db.commit()
        db.refresh(address_in_db)
    except Exception as e:
        raise e
    
    return address_in_db

def delete_address(db: Session, address_id: int) -> int:
    stmt = delete(models.Addresses).where(models.Addresses.id==address_id)
    try:
        db.execute(stmt)
        db.commit()
    except IntegrityError as e:
        raise IntegrityError from e
    except Exception as e:
        raise e
    
    return address_id

#-- Table 'vendors' queries --#
def get_vendor_by_name(db: Session, vendor: schemas.VendorBase) -> models.Vendors:
    try:
        return db.query(models.Vendors).filter(models.Vendors.name==vendor.name).first()
    except Exception as e:
        raise e

def get_vendors(db: Session, 
                    vendor_name: str | None = None, 
                    vendor_type: str | None = None,
                    vendor_id: int | None = None, 
                    offset: int = 0, limit: int = 100) -> list[models.Vendors]:
    base_query = db.query(models.Vendors)

    if vendor_name:
        vendor_name_string = f'{vendor_name}%'
    
    if vendor_type:
        vendor_type_string = f'{vendor_type}%'
    
    if vendor_name:
        base_query = base_query.filter(models.Vendors.name.ilike(vendor_name_string))
    
    if vendor_type:
        base_query = base_query.filter(models.Vendors.type.ilike(vendor_type_string))
    
    if vendor_id:
        base_query = base_query.filter(models.Vendors.id==vendor_id)

    try:
        return base_query.offset(offset).limit(limit).all()
    except Exception as e:
        raise e

def get_vendor_by_properties(db: Session, vendor: schemas.VendorBase) -> models.Vendors:
    try:
        return db.query(models.Vendors).filter(models.Vendors.name==vendor.name, models.Vendors.type==vendor.type).first()
    except Exception as e:
        raise e

def get_vendor_by_id(db: Session, vendor_id: int) -> models.Vendors:
    try:
        return db.query(models.Vendors).filter(models.Vendors.id==vendor_id).first()
    except Exception as e:
        raise e

def add_vendor(db: Session, vendor: schemas.VendorBase) -> models.Vendors:
    try:
        new_vendor = models.Vendors(**vendor.model_dump())
        db.add(new_vendor)
        db.commit()
        db.refresh(new_vendor)
    except Exception as e:
        raise e
    
    return new_vendor

def modify_vendor(db: Session, vendor: schemas.Vendor) -> models.Vendors:
    try:
        vendor_in_db = db.query(models.Vendors).filter(models.Vendors.id==vendor.id).first()
        vendor_in_db.name = vendor.name # type: ignore
        vendor_in_db.type = vendor.type # type: ignore
        db.commit()
        db.refresh(vendor_in_db)
    except Exception as e:
        raise e
    
    return vendor_in_db

def delete_vendor(db: Session, vendor_id: int) -> int:
    stmt = delete(models.Vendors).where(models.Vendors.id==vendor_id)
    try:
        db.execute(stmt)
        db.commit()
    except Exception as e:
        raise e
    
    return vendor_id

#-- Table 'pops' queries --#
def get_pop_by_properties(db: Session, pop: schemas.PopBase) -> models.Pops:
    try:
        return db.query(models.Pops).filter(models.Pops.name==pop.name, models.Pops.owner==pop.owner).first()
    except Exception as e:
        raise e

def get_pops(db: Session, pop_id: int | None = None, pop_name: str | None = None, pop_owner: str | None = None, offset: int = 0, limit: int = 10) -> list[models.Pops]:
    base_query = db.query(models.Pops)

    if pop_id:
        base_query = base_query.filter(models.Pops.id==pop_id)
        
    if pop_name:
        pop_name_string = f'{pop_name}%'
        base_query = base_query.filter(models.Pops.name.ilike(pop_name_string))
    
    if pop_owner:
        pop_owner_string = f'{pop_owner}%'
        base_query = base_query.join(models.Vendors).filter(models.Vendors.name.ilike(pop_owner_string))

    try:
        return base_query.offset(offset).limit(limit).all()
    except Exception as e:
        raise DBAPIError(str(base_query), [], e) from e

def add_pop(db: Session, pop: schemas.PopBase) -> models.Pops:
    try:
        new_pop = models.Pops(**pop.model_dump())
        db.add(new_pop)
        db.commit()
        db.refresh(new_pop)
    except Exception as e:
        raise e
    
    return new_pop

def modify_pop(db: Session, pop: schemas.Pop) -> models.Pops:
    try:
        pop_in_db = db.query(models.Pops).filter(models.Pops.id==pop.id).first()
        pop_in_db.name = pop.name # type: ignore
        pop_in_db.owner = pop.owner # type: ignore
        pop_in_db.extra_info = pop.extra_info # type: ignore
        db.commit()
        db.refresh(pop_in_db)
    except Exception as e:
        raise e
    
    return pop_in_db

def delete_pop(db: Session, pop_id: int) -> int:
    stmt = delete(models.Pops).where(models.Pops.id==pop_id)
    try:
        db.execute(stmt)
        db.commit()
    except Exception as e:
        raise e
    
    return pop_id

#-- Table 'users' queries --#
def get_user_by_name(db: Session, user_name: str) -> models.Users:
    try:
        return db.query(models.Users).filter(models.Users.user_name==user_name).first()
    except Exception as e:
        raise e
    
def get_users(db: Session, user_id: int | None = None, user_name: str | None = None, disabled: bool | None = None, scope: str | None = None, offset: int = 0, limit: int = 100) -> list[models.Users]:
    base_query = db.query(models.Users)

    if user_id:
        base_query = base_query.filter(models.Users.id==user_id)

    if user_name:
        base_query = base_query.filter(models.Users.user_name.ilike(f"{user_name}%"))
    
    if disabled is not None:
        base_query = base_query.filter(models.Users.disabled==disabled)
    
    if scope:
        base_query = base_query.filter(models.Users.scope.ilike(f"{scope}%"))

    try:
        return base_query.offset(offset).limit(limit).all()
    except Exception as e:
        raise e
    
def add_user(db: Session, user: schemas.NewUser) -> models.Users:
    try:
        new_user = models.Users(**user.model_dump())
        new_user.password = get_password_hash(user.password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        raise e
    
    return new_user

def update_user(db: Session, user: schemas.User) -> models.Users:
    try:
        user_in_db = db.query(models.Users).filter(models.Users.id==user.id).first()
        user_in_db.user_name = user.user_name # type: ignore
        user_in_db.email = user.email # type: ignore
        user_in_db.first_name = user.first_name # type: ignore
        user_in_db.middle_name = user.middle_name # type: ignore
        user_in_db.last_name = user.last_name # type: ignore
        user_in_db.disabled = user.disabled # type: ignore
        user_in_db.scope = user.scope # type: ignore
        db.commit()
        db.refresh(user_in_db)
    except Exception as e:
        raise e
    
    return user_in_db

def update_password(db: Session, user: schemas.UserNameAndPassword) -> str:
    try:
        user_in_db = db.query(models.Users).filter(models.Users.user_name==user.user_name).first()
        user_in_db.password = get_password_hash(user.password)
        db.commit()
        db.refresh(user_in_db)
    except Exception as e:
        raise e
    
    return 'Password updated'

def delete_user(db: Session, user_id: int) -> int:
    stmt = delete(models.Users).where(models.Users.id==user_id)
    try:
        db.execute(stmt)
        db.commit()
    except Exception as e:
        raise e
    
    return user_id