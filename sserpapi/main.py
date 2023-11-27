from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import clients, users
import auth
import logging

#sql_models.Base.metadata.create_all(bind=engine)

#logging config
logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s: %(message)s', filename='sserpapi.log', level=logging.WARNING)

app = FastAPI()

origins = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ['*'],
    allow_headers = ['*']
    )

app.include_router(clients.router)
app.include_router(users.router)
app.include_router(auth.router)

