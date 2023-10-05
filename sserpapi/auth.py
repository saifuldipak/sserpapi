from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status
import db_queries as db_query
from dependency import get_db
from sqlalchemy.orm import Session
import pydantic_schemas as schemas
from typing import Annotated
from datetime import datetime, timedelta
from jose import jwt

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

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, username: str, password: str):
    user = db_query.get_user_by_name(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.user_name}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}