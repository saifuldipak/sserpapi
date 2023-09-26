from fastapi import FastAPI
from . import sql_models
from .db_connection import engine
from fastapi.middleware.cors import CORSMiddleware
from .routers import clients

sql_models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    'http://localhost:5173'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ['*'],
    allow_headers = ['*']
    )

app.include_router(clients.router)

