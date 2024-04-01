from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import clients, users
import auth
import logging
from logger_config import create_console_handler, create_file_handler

# Configure logging
logger = logging.getLogger()
logger.addHandler(create_file_handler())
logger.addHandler(create_console_handler())
logging.getLogger('passlib').setLevel(logging.ERROR)

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

