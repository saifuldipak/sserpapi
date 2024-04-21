import logging
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sserpapi.logger_config import create_file_handler

# Loading environment variables
load_dotenv()

logger = logging.getLogger(__name__)
file_handler = create_file_handler()
logger.addHandler(file_handler)

POSTGRES_USER=os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD=os.getenv('POSTGRES_PASSWORD')
POSTGRES_HOST=os.getenv('POSTGRES_HOST')
POSTGRES_PORT=os.getenv('POSTGRES_PORT')
POSTGRES_DB=os.getenv('POSTGRES_DB')

# Construct database URL
DB_URL = f"""postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}\
@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"""
print(DB_URL)
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
Base = declarative_base()
