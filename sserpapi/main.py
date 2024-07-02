import yaml
from logging.config import dictConfig
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sserpapi.routers import clients, users
from sserpapi import auth
from dotenv import load_dotenv
import os

# Configure logging
load_dotenv()
FASTAPI_PATH=os.getenv('FASTAPI_PATH')
logging_config_file = os.path.join(FASTAPI_PATH, 'logging.yaml')
with open(logging_config_file, 'r', encoding='utf-8') as f:
    config_dict = yaml.safe_load(f)
    config_dict['handlers']['file']['filename'] = os.path.join(FASTAPI_PATH, config_dict['handlers']['file']['filename'])

dictConfig(config_dict)

# Create FastAPI app
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

