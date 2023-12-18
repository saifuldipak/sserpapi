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
    pop_id: int
    extra_info: str | None = None

class Service(ServiceBase):
    id: int

class ClientBase(BaseModel):
    name: str
    client_type_id: int

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

class VendorBase(BaseModel):
    name: str
    type: typing_extensions.Literal['LSP', 'NTTN', 'ISP']

class Vendor(VendorBase):
    id: int

class ContactDetails(Contact):
    clients: Client | None = None
    vendors: Vendor | None = None
    services: Service | None = None

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

class EntryDelete(BaseModel):
    message: str
    id: int

class VendorDetails(Vendor):
    contacts: list[Contact] = []
    addresses: list[Address] = []

class PopBase(BaseModel):
    name: str
    owner: int
    extra_info: str | None = None

class Pop(PopBase):
    id: int

class PopDetails(Pop):
    vendors: Vendor = None
    services: list[Service] = []

class ServiceDetails(Service):
    service_types: ServiceType
    pops: Pop
    clients: Client