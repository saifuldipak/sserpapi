from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import clients, users
import auth

#sql_models.Base.metadata.create_all(bind=engine)

app = FastAPI()

""" origins = [
    'http://localhost:5173'
] """

app.add_middleware(
    CORSMiddleware,
    allow_origins = ['*'],
    allow_credentials = True,
    allow_methods = ['*'],
    allow_headers = ['*']
    )

app.include_router(clients.router)
app.include_router(users.router)
app.include_router(auth.router)

