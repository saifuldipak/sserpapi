from sqlalchemy.orm import Session
from sserpapi.db.connection import SessionLocal, engine
from sserpapi.db.models import Base
from sserpapi.db.queries import get_user_by_name, add_user
from sserpapi.pydantic_schemas import User
from sserpapi.auth import get_password_hash

def user_add(db: Session, credential: dict) -> any:
    user_exists = get_user_by_name(db, user_name=credential['username'])
    if user_exists:
        print(f'User exists: {credential["username"]}')
    
    hashed_password = get_password_hash(credential['password'])
    new_user = User(
                user_name=credential['username'], 
                password=hashed_password, 
                email=credential['email'], 
                disabled=credential['disabled'], 
                scope=credential['scope']
                )
    new_user = add_user(db, user=new_user)
    print(f'User created: {new_user.user_name}')

if __name__ == '__main__':
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db_connection = SessionLocal()
    
    user_data = {
        'username': 'saiful',
        'password': 'amisaiful',
        'email': 'saiful@somedoamin.com',
        'disabled': False,
        'scope': 'user'
    }
    
    user_add(db_connection, user_data)