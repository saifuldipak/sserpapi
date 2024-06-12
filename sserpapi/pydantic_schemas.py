# pylint: disable=E0401
from pydantic import BaseModel, EmailStr
import typing_extensions

#-- table 'clients' and 'client_types' --#
class ClientBase(BaseModel):
    name: str
    client_type_id: int

class Client(ClientBase):
    id: int

class ClientTypeBase(BaseModel):
    name: str

class ClientType(ClientTypeBase):
    id: int

#-- table 'services' and 'service_types' --#
class ServiceBase(BaseModel):
    client_id: int
    point: str
    service_type_id: int
    bandwidth: int
    pop_id: int
    extra_info: str | None = None

class Service(ServiceBase):
    id: int

class ServiceTypeBase(BaseModel):
    name: str
    description: str | None = None

class ServiceType(ServiceTypeBase):
    id: int

#-- table 'contacts' --#
class ContactBase(BaseModel):
    name: str
    designation: str
    type: typing_extensions.Literal['Admin', 'Technical', 'Billing']
    phone1: str
    phone2: str | None = None
    phone3: str | None = None
    email: EmailStr | None = None
    client_id: int | None = None
    vendor_id: int | None = None
    service_id: int | None = None

class Contact(ContactBase):
    id: int

class ContactSearch(BaseModel):
    id: int | None = None
    name: str | None = None
    designation: str | None = None
    type: typing_extensions.Literal['Admin', 'Technical', 'Billing'] | None = None
    phone1: str | None = None
    phone2: str | None = None
    phone3: str | None = None
    email: EmailStr | None = None
    client_id: int | None = None
    vendor_id: int | None = None
    service_id: int | None = None
    client_name: str | None = None
    service_point: str | None = None
    vendor_name: str | None = None

#-- table 'vendors' --#
class VendorBase(BaseModel):
    name: str
    type: typing_extensions.Literal['LSP', 'NTTN', 'ISP']

class Vendor(VendorBase):
    id: int

#-- table 'addresses' --#
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

class AddressSearch(BaseModel):
    id: int | None = None
    flat: str | None = None
    floor: str | None = None
    holding: str | None = None
    street: str | None = None
    area: str | None = None
    thana: str | None = None
    district: str | None = None
    client_id: int | None = None
    service_id: int | None = None
    vendor_id: int | None = None
    extra_info: str | None = None
    client_name: str | None = None
    service_point: str | None = None
    vendor_name: str | None = None

    def all_none_values(self):
        return all(value is None for value in self.__dict__.values())

#-- table 'pops' --#
class PopBase(BaseModel):
    name: str
    owner: int
    extra_info: str | None = None

class Pop(PopBase):
    id: int

#-- table 'users' --#    
class UserBase(BaseModel):
    user_name: str
    first_name: str
    middle_name: str | None = None
    last_name: str
    email: EmailStr
    disabled: bool | None = False
    scope: str

class User(UserBase):
    password: str

#-- JWT token generation --#
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []

#-- Return values for record deletion functions --#
class EntryDelete(BaseModel):
    message: str
    id: int

#-- records from different tables --#
class ClientDetails(Client):
    addresses: list[Address] = []
    contacts: list[Contact] = []
    services: list[Service] = []
    client_types: ClientType

class ServiceDetails(Service):
    service_types: ServiceType
    pops: Pop
    clients: Client
    contacts: list[Contact] = []
    addresses: list[Address] = []

class PopDetails(Pop):
    vendors: Vendor | None = None
    services: list[Service] = []

class ContactDetails(Contact):
    clients: Client | None = None
    vendors: Vendor | None = None
    services: Service | None = None

class VendorDetails(Vendor):
    contacts: list[Contact] = []
    addresses: list[Address] = []

class AddressDetails(Address):
    clients: Client | None = None
    vendors: Vendor | None = None
    services: Service | None = None
