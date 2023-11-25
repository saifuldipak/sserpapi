from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependency import get_db
import pydantic_schemas as schemas
import db_queries as db_query

router = APIRouter()

@router.post("/clients/add", response_model=schemas.Client, summary='Add a client', tags=['Clients'])
def create_client(client: schemas.ClientBase, db: Session = Depends(get_db)):
    client_exists = db_query.get_client_by_name(db, client_name=client.name)
    if client_exists:
        raise HTTPException(status_code=400, detail="Client exists")
    
    client_type_exists = db_query.get_client_type_by_id(db, client_type_id=client.client_type_id)
    if not client_type_exists:
        raise HTTPException(status_code=400, detail='Client type does not exist')
    
    return db_query.add_client(db=db, client=client)


@router.get("/clients/query/{client_name}", response_model=list[schemas.Client], summary='Get client list', tags=['Clients'])
def read_clients(client_name: str, page: int = 0, page_size: int = 10, db: Session = Depends(get_db)):
    offset = (page - 1) * page_size
    db_clients = db_query.get_client_list(db, client_name=client_name, offset=offset, limit=page_size)
    return db_clients

@router.post("/clients/types/add", response_model=schemas.ClientTypesBase, summary='Add a client type', tags=['Clients'])
def add_client_type(client_type: schemas.ClientTypesBase, db: Session = Depends(get_db)):
    client_type_exists = db_query.get_client_type(db, client_type=client_type.name)
    if client_type_exists:
        raise HTTPException(status_code=400, detail="Client type exists")
    return db_query.add_client_type(db=db, client_type=client_type)

@router.get("/clients/types/get", response_model=list[schemas.ClientTypes], summary='Get client type list', tags=['Clients'])
def get_client_types(page: int = 0, page_size: int = 10, db: Session = Depends(get_db)):
    offset = page * page_size
    db_client_types = db_query.get_client_types(db, offset=offset, limit=page_size)
    return db_client_types

""" @router.get("/clients/{client_id}", response_model=schemas.Client, summary='Get one client info', tags=['Clients'])
def read_client(client_id: int, db: Session = Depends(get_db)):
    db_client = db_query.get_client(db, client_id=client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_client


@router.post("/clients/{client_id}/services/", response_model=schemas.ServiceBase)
def create_service_for_client(client_id: int, service: schemas.ServiceBase, db: Session = Depends(get_db)):
    db_client = db_query.get_client(db, client_id=client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return db_query.add_service(db=db, service=service)


@router.get("/services/", response_model=list[schemas.Service])
def read_services(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db_query.get_services(db, skip=skip, limit=limit)
    return items """
