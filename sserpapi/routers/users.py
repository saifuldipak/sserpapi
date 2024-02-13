from fastapi import APIRouter, Depends, HTTPException, Security
import db.queries as db_query
from db.dependency import get_db
from sqlalchemy.orm import Session
import pydantic_schemas as schemas
from auth import get_password_hash, get_current_active_user

router = APIRouter(dependencies=[Security(get_current_active_user, scopes=["Admin", "Editor"])])

@router.post("/users/add", response_model=schemas.UserBase, summary='Add an user', tags=['Users'])
def create_user(user: schemas.User, db: Session = Depends(get_db)):
    user_exists = db_query.get_user_by_name(db, user_name=user.user_name)
    if user_exists:
        raise HTTPException(status_code=400, detail="User exists")
    user.password = get_password_hash(user.password)
    return db_query.add_user(db=db, user=user)


@router.get("/users/show", response_model=list[schemas.UserBase], summary='Get all users', tags=['Users'])
def read_clients(page: int = 0, page_size: int = 10, db: Session = Depends(get_db)):
    offset = (page - 1) * page_size
    db_clients = db_query.get_users(db, offset=offset, limit=page_size)
    return db_clients
