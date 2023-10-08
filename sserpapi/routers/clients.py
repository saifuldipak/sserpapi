from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependency import get_db
import pydantic_schemas as schemas
import db_queries as db_query

router = APIRouter()

@router.post("/clients/add", response_model=schemas.ClientBase, summary='Add a client', tags=['Clients'])
def create_client(client_schema: schemas.ClientBase, db: Session = Depends(get_db)):
    client_exists = db_query.get_client_by_name(db, client_name=client_schema.name)
    if client_exists:
        raise HTTPException(status_code=400, detail="Client exists")
    return db_query.add_client(db=db, client_schema=client_schema)


@router.get("/clients/show", response_model=list[schemas.Client], summary='Get all clients', tags=['Clients'])
def read_clients(page: int = 0, page_size: int = 10, db: Session = Depends(get_db)):
    offset = (page - 1) * page_size
    db_clients = db_query.get_clients(db, offset=offset, limit=page_size)
    return db_clients


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
