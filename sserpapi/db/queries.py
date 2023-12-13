from sqlalchemy.orm import Session, joinedload
import db.models as models
import pydantic_schemas as schemas
import logging

logger = logging.getLogger(__name__)

def get_client(db: Session, client_id: int):
    return db.query(models.Clients).filter(models.Clients.id==client_id).first()

def get_client_by_name(db: Session, client_name: str):
    return db.query(models.Clients).filter(models.Clients.name==client_name).first()

def get_client_list(db: Session, client_name: str, offset: int = 0, limit: int = 100):
    client_name_string = f'{client_name}%'
    return (db.query(models.Clients)
            .join(models.ClientTypes)
            .options(joinedload(models.Clients.client_type))
            .filter(models.Clients.name.ilike(client_name_string))
            .offset(offset).limit(limit).all())

def get_services(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Services).offset(skip).limit(limit).all()

def add_client(db: Session, client: schemas.ClientBase):
    new_client = models.Clients(name=client.name, client_type_id=client.client_type_id)
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return new_client

def add_service(db: Session, service: schemas.ServiceBase):
    new_service = models.Services(**service.dict())
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return new_service

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

def get_client_type(db: Session, client_type: str):
    return db.query(models.Clients).filter(models.ClientTypes.name==client_type).first()

def add_client_type(db: Session, client_type: schemas.ClientType):
    new_client_type = models.ClientTypes(name=client_type.name)
    db.add(new_client_type)
    db.commit()
    db.refresh(new_client_type)
    return new_client_type

def get_client_types(db: Session, offset: int = 0, limit: int = 100):
    return db.query(models.ClientTypes).offset(offset).limit(limit).all()

def get_client_type_by_id(db: Session, client_type_id: int):
    return db.query(models.ClientTypes).filter(models.ClientTypes.id==client_type_id).first()

def get_client_by_id(db: Session, client_id: int):
    return db.query(models.Clients).filter(models.Clients.id==client_id).first()

def add_contact(db: Session, contact: schemas.ContactBase):
    new_contact = models.Contacts(**contact.model_dump())
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact

def get_contact_list(db: Session, contact_name: str, offset: int = 0, limit: int = 100):
    contact_name_string = f'%{contact_name}%'
    return db.query(models.Contacts).join(models.Clients).options(joinedload(models.Contacts.clients)).filter(models.Contacts.name.ilike(contact_name_string)).offset(offset).limit(limit).all()
    
def delete_client(db: Session, client_id: int):
    client = db.query(models.Clients).filter(models.Clients.id==client_id).first()
    db.delete(client)
    db.commit()
    return client_id

def modify_client(db: Session, client: schemas.Client):
    client_in_db = db.query(models.Clients).filter(models.Clients.id==client.id).first()
    client_in_db.name = client.name
    client_in_db.client_type_id = client.client_type_id 
    db.commit()
    db.refresh(client_in_db)
    return client_in_db

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

def delete_client_type(db: Session, client_type_id: int):
    client_type = db.query(models.ClientTypes).filter(models.ClientTypes.id==client_type_id).first()
    db.delete(client_type)
    db.commit()
    return client_type_id

def get_vendor_by_name(db: Session, vendor: schemas.VendorBase):
    return db.query(models.Vendors).filter(models.Vendors.name==vendor.name).first()

def add_vendor(db: Session, vendor: schemas.VendorBase):
    new_vendor = models.Vendors(name=vendor.name, type=vendor.type)
    db.add(new_vendor)
    db.commit()
    db.refresh(new_vendor)
    return new_vendor

def get_vendor_list(db: Session, vendor_name: str | None = None, offset: int = 0, limit: int = 100):
    if vendor_name:
        vendor_name_string = f'{vendor_name}%'
        return db.query(models.Vendors).filter(models.Vendors.name.ilike(vendor_name_string)).offset(offset).limit(limit).all()
    else:
        return db.query(models.Vendors).offset(offset).limit(limit).all()

def get_service_type_by_name(db: Session, service_type: schemas.ServiceTypeBase):
    return db.query(models.ServiceTypes).filter(models.ServiceTypes.name==service_type.name).first()

def add_service_type(db: Session, service_type: schemas.ServiceType):
    new_service_type = models.ServiceTypes(name=service_type.name, description=service_type.description)
    db.add(new_service_type)
    db.commit()
    db.refresh(new_service_type)
    return new_service_type

def get_service_type_list(db: Session, service_type: str, offset: int = 0, limit: int = 10):
    if service_type:
        sevice_type_string = f'{service_type}%'
        return db.query(models.ServiceTypes).filter(models.ServiceTypes.name.ilike(sevice_type_string)).offset(offset).limit(limit).all()
    else:
        return db.query(models.ServiceTypes).offset(offset).limit(limit).all()

def delete_service_type(db: Session, service_type_id: int):
    service_type = db.query(models.ServiceTypes).filter(models.ServiceTypes.id==service_type_id).first()
    db.delete(service_type)
    db.commit()
    return service_type_id

def get_service_type_by_id(db: Session, service_type_id: int):
    return db.query(models.ServiceTypes).filter(models.ServiceTypes.id==service_type_id).first()