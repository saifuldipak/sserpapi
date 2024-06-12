import logging
from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.orm import Session
import sserpapi.db.queries as db_query
from sserpapi.db.dependency import get_db
from sserpapi.auth import get_password_hash, get_current_active_user
import sserpapi.pydantic_schemas as schemas

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Security(get_current_active_user, scopes=["admin"])])

@router.post("/user", response_model=schemas.UserBase, summary='Add an user', tags=['Users'])
def add_user(user: schemas.User, db: Session = Depends(get_db)):
    try:
        user_exists = db_query.get_user_by_name(db, user_name=user.user_name)
    except Exception as e:
        logger.error('get_user_by_name(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if user_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User exists")
    
    user.password = get_password_hash(user.password)
    return db_query.add_user(db=db, user=user)


@router.get("/users/show", response_model=list[schemas.UserBase], summary='Get all users', tags=['Users'])
def read_clients(page: int = 0, page_size: int = 10, db: Session = Depends(get_db)):
    offset = (page - 1) * page_size
    db_clients = db_query.get_users(db, offset=offset, limit=page_size)
    return db_clients
