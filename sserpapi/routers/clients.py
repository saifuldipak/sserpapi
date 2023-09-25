from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..dependency import get_db
import sserpapi.sql_models as models
import sserpapi.pydantic_schemas as schemas

router = APIRouter()

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

@router.post("/clients/add", response_model=schemas.ClientBase)
def create_client(client_schema: schemas.ClientBase, db: Session = Depends(get_db)):
    client_exists = get_client_by_name(db, client_name=client_schema.name)
    if client_exists:
        raise HTTPException(status_code=400, detail="Client exists")
    return add_client(db=db, client_schema=client_schema)


@router.get("/clients/", response_model=list[schemas.Client])
def read_clients(page: int = 0, page_size: int = 10, db: Session = Depends(get_db)):
    offset = (page -1) * page_size
    db_clients = get_clients(db, offset=offset, limit=page_size)
    return db_clients


@router.get("/clients/{client_id}", response_model=schemas.Client)
def read_client(client_id: int, db: Session = Depends(get_db)):
    db_client = get_client(db, client_id=client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_client


@router.post("/clients/{client_id}/services/", response_model=schemas.ServiceBase)
def create_service_for_client(client_id: int, service: schemas.ServiceBase, db: Session = Depends(get_db)):
    db_client = get_client(db, client_id=client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return add_service(db=db, service=service)


@router.get("/services/", response_model=list[schemas.Service])
def read_services(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = get_services(db, skip=skip, limit=limit)
    return items
