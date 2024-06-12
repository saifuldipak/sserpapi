from sserpapi.auth import get_password_hash
from sserpapi.db.queries import get_user_by_name, add_user
from sserpapi.pydantic_schemas import User
from sqlalchemy.orm import Session
from sserpapi.db.connection import SessionLocal

def user_add(db: Session, credential: dict) -> any:
    user_exists = get_user_by_name(db, user_name=credential['user_name'])
    if user_exists:
        print(f'User exists: {credential["username"]}')
    
    hashed_password = get_password_hash(credential['password'])
    new_user = User(user_name=credential['user_name'], password=hashed_password, first_name=credential['first_name'], last_name=credential['last_name'], email=credential['email'], disabled=credential['disabled'], scope=credential['scope']) 
    new_user = add_user(db, user=new_user)
    print(f'User created: {new_user.user_name}')

if __name__ == '__main__':
    db = SessionLocal()
    credential = {
        'user_name': 'saiful',
        'password': 'amisaiful',
        'first_name': 'Saiful',
        'last_name': 'Islam',
        'email': 'saiful@somedoamin.com',
        'disabled': False,
        'scope': 'admin'
    }
    user_add(db, credential)