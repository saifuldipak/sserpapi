from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, Depends, HTTPException, Form
import db_queries as db_query
from dependency import get_db
from sqlalchemy.orm import Session
import pydantic_schemas as schemas
from typing import Annotated

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "852dfac7da799b2f17f9e3d0c4d571cf4946c6f4ff8fdc413d55e066f173a422"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oath2_scheme = OAuth2PasswordBearer(tokenUrl='token')

router = APIRouter()

def get_password_hash(password):
    hashed_password = pwd_context.hash(password)
    return hashed_password

@router.post("/users/add", response_model=schemas.User, summary='Add an user', tags=['Users'])
def create_user(user_name: Annotated[str, Form()], password: Annotated[str, Form()], db: Session = Depends(get_db)):
    user_exists = db_query.get_user_by_name(db, user_name=user_name)
    if user_exists:
        raise HTTPException(status_code=400, detail="User exists")
    hashed_password = get_password_hash(password)
    return db_query.add_user(db=db, user_name=user_name, password=hashed_password)

@router.get("/users/show", response_model=list[schemas.UserBase], summary='Get all users', tags=['Users'])
def read_clients(page: int = 0, page_size: int = 10, db: Session = Depends(get_db)):
    offset = (page - 1) * page_size
    db_clients = db_query.get_users(db, offset=offset, limit=page_size)
    return db_clients
