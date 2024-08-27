# pylint: disable=E0401
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Optional, Self
from typing_extensions import Literal

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
    type: Literal['Admin', 'Technical', 'Sales', 'Billing']
    phone1: str
    phone2: str | None = None
    phone3: str | None = None
    email: EmailStr | None = None
    client_id: int | None = None
    vendor_id: int | None = None
    service_id: int | None = None
    
    @model_validator(mode='after')
    def check_ids(self) -> Self:
        ids = [self.client_id, self.vendor_id, self.service_id]
        if sum(id is not None for id in ids) > 1:
            raise ValueError('Only one of client_id, vendor_id, or service_id can be provided.')
        return self
    
    @field_validator('phone1', 'phone2', 'phone3')
    @classmethod
    def check_phone_length_and_prefix(cls, data: str) -> str:
        if data is not None:
            if len(data) != 11:
                raise ValueError('Phone number must be exactly 11 characters long.')
            if not data.startswith("01"):
                raise ValueError('Phone number must start with "01".')
        return data 
   
class Contact(ContactBase):
    id: int
    
class ContactSearch(BaseModel):
    id: int | None = None
    name: str | None = None
    designation: str | None = None
    type: Literal['Admin', 'Technical', 'Sales','Billing'] | None = None
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
    type: Literal['LSP', 'NTTN', 'ISP']

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
class UserName(BaseModel):
    user_name: str = Field(min_length=4, max_length=16)

class UserNameAndPassword(UserName):
    password: str = Field(min_length=8)

class UserBase(BaseModel):
    first_name: str = Field(min_length=4, max_length=16)
    middle_name: Optional[str] = Field(min_length=4, max_length=16, default=None)
    last_name: str = Field(min_length=4, max_length=16)
    email: EmailStr
    disabled: bool | None = False
    scope: Literal['admin', 'write', 'read']

class User(UserName, UserBase):
    id: int

class NewUser(UserNameAndPassword, UserBase):
    pass
    
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

class AccountManagerBase(BaseModel):
    client_id: int
    contact_id: int

class AccountManager(AccountManagerBase):
    id: int

class AccountManagerSearch(BaseModel):
    id: int | None = None
    client_id: int | None = None
    contact_id: int | None = None
    client_name: str | None = None
    contact_name: str | None = None

    @model_validator(mode='before')
    def check_parameters_presence(cls, values):
        if all(value is None for value in values.values()):
            raise ValueError("At least one parameter must be provided")
        return values

class AccountManagerDetails(AccountManager):
    clients: Client | None = None
    contacts: Contact | None = None