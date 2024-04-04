import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sserpapi.logger_config import create_file_handler

logger = logging.getLogger(__name__)
file_handler = create_file_handler()
logger.addHandler(file_handler)

POSTGRES_SECRETS = ".env"

# Function to read config file and extract database connection info
def read_db_config(file_path):
    config = {}
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            try:
                key, value = line.strip().split("=")
                config[key] = value
            except ValueError:
                logger.warning('Issue with line: %s', line.strip())
    return config

# Read database connection info from config file
db_config = read_db_config(POSTGRES_SECRETS)

# Construct database URL
DB_URL = f"""postgresql://{db_config['POSTGRES_USER']}:{db_config['POSTGRES_PASSWORD']}\
@{db_config['POSTGRES_HOST']}:{db_config['POSTGRES_PORT']}/{db_config['POSTGRES_DB']}"""

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
Base = declarative_base()
