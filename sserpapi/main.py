from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from . import client, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/clients/", response_model=schemas.ClientBase)
def create_client(client_schema: schemas.ClientBase, db: Session = Depends(get_db)):
    client_exists = client.get_client_by_name(db, client_name=client_schema.name)
    if client_exists:
        raise HTTPException(status_code=400, detail="Client exists")
    return client.add_client(db=db, client_schema=client_schema)


@app.get("/clients/", response_model=list[schemas.Client])
def read_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_clients = client.get_clients(db, skip=skip, limit=limit)
    return db_clients


@app.get("/clients/{client_id}", response_model=schemas.Client)
def read_client(client_id: int, db: Session = Depends(get_db)):
    db_client = client.get_client(db, client_id=client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_client


@app.post("/clients/{client_id}/services/", response_model=schemas.ServiceBase)
def create_service_for_client(client_id: int, service: schemas.ServiceBase, db: Session = Depends(get_db)):
    return client.add_service(db=db, service=service, client_id=client_id)


@app.get("/services/", response_model=list[schemas.Service])
def read_services(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = client.get_services(db, skip=skip, limit=limit)
    return items
