import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

POSTGRES_SECRETS = "./db/postgres_secrets.txt"

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
SQLALCHEMY_DATABASE_URL = f"postgresql://{db_config['POSTGRES_USER']}:{db_config['POSTGRES_PASSWORD']}@{db_config['POSTGRES_HOST']}:{db_config['POSTGRES_PORT']}/{db_config['POSTGRES_DB']}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
Base = declarative_base()
