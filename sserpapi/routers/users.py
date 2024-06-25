import logging
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import sserpapi.db.queries as db_query
from sserpapi.db.dependency import get_db
from sserpapi.auth import get_current_active_user, verify_password
import sserpapi.pydantic_schemas as schemas

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Security(get_current_active_user, scopes=["admin"])])

@router.post("/user", response_model=schemas.User, summary='Add an user', tags=['Users'])
def add_user(user: schemas.NewUser, db: Session = Depends(get_db)):
    try:
        user_exists = db_query.get_user_by_name(db, user_name=user.user_name)
    except Exception as e:
        logger.error('get_user_by_name(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if user_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User exists")
    
    return db_query.add_user(db=db, user=user)


@router.get("/users", response_model=list[schemas.User], summary='Get all users', tags=['Users'])
def get_users(user_name: str | None = None, disabled: bool | None = None, scope: str | None = None, page: int = 0, page_size: int = 10, db: Session = Depends(get_db)):
    offset = page * page_size

    try:
        users = db_query.get_users(db, user_name=user_name, disabled=disabled, scope=scope, offset=offset, limit=page_size)
    except Exception as e:
        logger.error('get_users(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return users

@router.put("/user", response_model=schemas.User, summary='Modify an user', tags=['Users'])
def update_user(user: schemas.User, db: Session = Depends(get_db)):
    try:
        user_exists = db_query.get_users(db, user_id=user.id)
    except Exception as e:
        logger.error('get_users(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if not user_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    
    return db_query.update_user(db=db, user=user)

@router.patch("/user/password", summary='Modify an user', tags=['Users'])
def update_password(user: schemas.UserNameAndPassword, db: Session = Depends(get_db)):
    try:
        user_exists = db_query.get_users(db, user_name=user.user_name)
    except Exception as e:
        logger.error('get_users(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if not user_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    
    try:
        same_password = verify_password(user.password, user_exists[0].password)
    except Exception as e:
        logger.error('verify_password(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if same_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password cannot be the same as the old password")
    
    return_value = db_query.update_password(db=db, user=user)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": return_value})

@router.delete("/user/{user_id}", summary='Delete an user', tags=['Users'])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    try:
        user_exists = db_query.get_users(db, user_id=user_id)
    except Exception as e:
        logger.error('get_users(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    if not user_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    
    try:
        db_query.delete_user(db=db, user_id=user_id)
    except Exception as e:
        logger.error('delete_user(): %s', e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    
    return JSONResponse(content={'detail': 'User deleted', 'id': user_id})