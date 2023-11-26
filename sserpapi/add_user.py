from db_connection import SessionLocal
from auth import get_password_hash
from db_queries import get_user_by_name, add_user
from pydantic_schemas import User

user_name = 'saiful'
password = 'amisaiful'
disabled = False
scope = 'user'
email = 'saiful@somedoamin.com'

try:
    db = SessionLocal()
    user_exists = get_user_by_name(db=db, user_name=user_name)
    if user_exists:
        print(f'User exists: {user_name}')
    else:
        hashed_password = get_password_hash(password)
        new_user = User(user_name=user_name, password=hashed_password, email=email, disabled=disabled, scope=scope)
        new_user = add_user(db=db, user=new_user)
        print(f'User created: {new_user.user_name}')
except Exception as e:
    print(f'An error occured: {e}')
finally:
    db.close()
