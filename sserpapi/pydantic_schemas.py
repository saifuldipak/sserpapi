from pydantic import BaseModel, constr
import typing_extensions
from fastapi import Form

class ContactBase(BaseModel):
    name: str
    designation: str
    type: typing_extensions.Literal['Admin', 'Technical', 'Billing']
    phone1: str
    phone2: str | None = None
    phone3: str | None = None
    client_id: int | None = None
    vendor_id: int | None = None
    service_id: int | None = None

class Contact(ContactBase):
    id: int

class ServiceBase(BaseModel):
    client_id: int
    point: str
    service_type_id: int
    bandwidth: int
    connected_to: str | None = None
    extra_info: str | None = None

class Service(ServiceBase):
    id: int

class ClientBase(BaseModel):
    name: str
    client_type_id: int

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

class ClientTypeBase(BaseModel):
    name: str

class ClientType(ClientTypeBase):
    id: int

class Client(ClientBase):
    id: int

class ContactWithClientName(Contact):
    clients: Client

    class Config:
        from_attributes = True

class VendorBase(BaseModel):
    name: str
    type: typing_extensions.Literal['LSP', 'NTTN', 'ISP']

class Vendor(VendorBase):
    id: int

class ServiceTypeBase(BaseModel):
    name: str
    description: str | None = None

class ServiceType(ServiceTypeBase):
    id: int
    
class AddressBase(BaseModel):
    flat: str | None = None
    floor: str | None = None
    holding: str
    street: str
    area: str
    thana: str
    district: str
    client_id: int | None = None
    service_id: int | None = None
    vendor_id: int | None = None
    extra_info: str | None = None

class Address(AddressBase):
    id: int

class ClientDetails(Client):
    addresses: list[Address] = []
    contacts: list[Contact] = []
    services: list[Service] = []
    client_type: ClientType

class ServiceDetails(Service):
    service_types: ServiceType
    clients: Client