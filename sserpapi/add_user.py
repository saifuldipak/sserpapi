from sserpapi.db.connection import SessionLocal
from sserpapi.auth import get_password_hash
from sserpapi.db.queries import get_user_by_name, add_user
from sserpapi.pydantic_schemas import User

USER_NAME = 'saiful'
PASSWORD = 'amisaiful'
DISABLED = False
SCOPE = 'user'
EMAIL = 'saiful@somedoamin.com'

try:
    db = SessionLocal()
    user_exists = get_user_by_name(db=db, user_name=USER_NAME)
    if user_exists:
        print(f'User exists: {USER_NAME}')
    else:
        hashed_password = get_password_hash(PASSWORD)
        new_user = User(
                    user_name=USER_NAME, 
                    password=hashed_password, 
                    email=EMAIL, 
                    disabled=DISABLED, 
                    scope=SCOPE
                    )
        new_user = add_user(db=db, user=new_user)
        print(f'User created: {new_user.user_name}')
except Exception as e:
    print(f'An error occured: {e}')
finally:
    db.close()
