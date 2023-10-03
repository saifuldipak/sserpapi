from sqlalchemy.orm import Session
import sql_models as models
import pydantic_schemas as schemas

def get_client(db: Session, client_id: int):
    return db.query(models.Clients).filter(models.Clients.id==client_id).first()

def get_client_by_name(db: Session, client_name: str):
    return db.query(models.Clients).filter(models.Clients.name==client_name).first()

def get_clients(db: Session, offset: int = 0, limit: int = 100):
    return db.query(models.Clients).offset(offset).limit(limit).all()

def get_services(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Services).offset(skip).limit(limit).all()

def add_client(db: Session, client_schema: schemas.ClientBase):
    new_client = models.Clients(name=client_schema.name)
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

def add_user(db: Session, user_schema: schemas.User):
    new_user = models.Users(**user_schema.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user