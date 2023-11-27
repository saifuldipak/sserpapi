from pydantic import BaseModel, constr
import typing_extensions
from fastapi import Form

class ContactBase(BaseModel):
    name: str
    designation: str
    phone: str
    type: typing_extensions.Literal['Admin', 'Technical', 'Billing']
    client_id: int | None = None
    vendor_id: int | None = None

class Contact(ContactBase):
    id: int

class ServiceBase(BaseModel):
    client_id: int
    location: str
    type: typing_extensions.Literal['Internet', 'Data', 'Managed solution']
    bandwidth: int
    vendor_id: int | None = None
    connected_to: str | None = None
    extra_info: str | None = None

class Service(ServiceBase):
    id: int

class ClientBase(BaseModel):
    name: str
    client_type_id: int
    
class Client(ClientBase):
    id: int
    contacts: list[Contact] = []
    services: list[Service] = []

    class Config:
        from_attributes = True

class VendorBase(BaseModel):
    name: str
    place: str
    union: str | None = None
    thana: str
    zilla: str

class UserBase(BaseModel):
    user_name: str
    email: str
    full_name: str | None = None
    disabled: bool | None = False
    scope: str

class User(UserBase):
    password: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []

class ClientTypesBase(BaseModel):
    name: str

class ClientTypes(ClientTypesBase):
    id: int