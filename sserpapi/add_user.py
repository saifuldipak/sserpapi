from db_connection import SessionLocal
from auth import get_password_hash
from db_queries import get_user_by_name, add_user

USER = 'test'
PASSWORD = 'test123'

def user_add(db, user_name, password):
        user_exists = get_user_by_name(db=db, user_name=user_name)
        if user_exists:
            return f'User exists: {user_name}'
        else:
            hashed_password = get_password_hash(password)
            new_user= add_user(db=db, user_name=user_name, password=hashed_password)
            return f'User created: {new_user.user_name}'

try:
    db = SessionLocal()
    print(user_add(db=db, user_name=USER, password=PASSWORD))
except Exception as e:
    print(f'An error occured: {e}')
finally:
    db.close()
