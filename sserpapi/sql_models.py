from db_connection import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

class Clients(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True, nullable=False)
    address = Column(String)
    contacts = relationship('Contacts', back_populates='clients')
    services = relationship('Services', back_populates='clients')
    client_type_id = Column(Integer, ForeignKey('client_types.id'), nullable=False)
    client_type = relationship('ClientTypes', back_populates='clients')

class Contacts(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    designation = Column(String)
    phone = Column(String)
    type = Column(String)
    client_id = Column(Integer, ForeignKey('clients.id'))
    vendor_id = Column(Integer, ForeignKey('vendors.id'))
    clients = relationship('Clients', back_populates='contacts')
    vendors = relationship('Vendors', back_populates='contacts')

class Vendors(Base):
    __tablename__ = 'vendors'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    place = Column(String)
    union = Column(String)
    thana = Column(String)
    zilla = Column(String)
    contacts = relationship('Contacts', back_populates='vendors')
    services = relationship('Services', back_populates='vendors')

class Services(Base):
    __tablename__ = 'service'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    location = Column(String)
    type = Column(String)
    bandwidth = Column(Integer)
    vendor_id = Column(Integer, ForeignKey('vendors.id'))
    connected_to = Column(String)
    extra_info = Column(String)
    clients = relationship('Clients', back_populates='services')
    vendors = relationship('Vendors', back_populates='services')

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_name = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String)
    disabled = Column(Boolean, nullable=False)
    password = Column(String, nullable=False)
    scope = Column(String, nullable=False)

class ClientTypes(Base):
    __tablename__ = 'client_types'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    clients = relationship('Clients', back_populates='client_type')
