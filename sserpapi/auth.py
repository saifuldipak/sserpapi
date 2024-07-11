import logging
from typing import Annotated
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from pydantic import ValidationError
import sserpapi.db.queries as db_query
from sserpapi.db.dependency import get_db
import sserpapi.pydantic_schemas as schemas

#logger name
logger = logging.getLogger(__name__)

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "852dfac7da799b2f17f9e3d0c4d571cf4946c6f4ff8fdc413d55e066f173a422"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 500

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token', scopes={"admin": "Can read & write to any table", "write": "Can read & write to any table except users", "read": "Can read any table except users"})

router = APIRouter()

def get_password_hash(password):
    hashed_password = pwd_context.hash(password)
    return hashed_password

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, username: str, password: str):
    user = db_query.get_user_by_name(db, username)
    if not user:
        logger.warning('User "%s" not found', username)
        return False
    
    if not verify_password(password, user.password):
        logger.warning('User "%s" password incorrect', username)
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

def get_current_user(security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)], db: Session=Depends(get_db),):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="No username")
        token_scopes = payload.get("scopes", [])
        token_data = schemas.TokenData(scopes=[token_scopes], username=username)
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'{e}') from e
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f'{e}') from e
    
    user = db_query.get_user_by_name(db=db, user_name=token_data.username)
    if user is None:
        raise credentials_exception

    has_permission = False
    for scope in security_scopes.scopes:
        if scope in token_data.scopes:
            has_permission = True

    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough permissions",
            headers={"WWW-Authenticate": authenticate_value},
    )

    return user


async def get_current_active_user(current_user: Annotated[schemas.User, Security(get_current_user, scopes=[])]):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user


@router.post("/token", response_model=schemas.Token)
async def get_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    if not db:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database connection error")
    
    user_authenticated = authenticate_user(db, form_data.username, form_data.password)
    if not user_authenticated:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user_authenticated.user_name, "scopes": user_authenticated.scope},expires_delta=access_token_expires,)
    
    return {"access_token": access_token, "token_type": "bearer"}