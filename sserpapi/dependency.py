from .database import SessionLocal

# Database connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()