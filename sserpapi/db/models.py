# pylint: disable=missing-docstring
# pylint: disable=E0401
from db.connection import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

class ClientTypes(Base):
    __tablename__ = 'client_types'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    clients = relationship('Clients', back_populates='client_types')

class Clients(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True, nullable=False)
    client_type_id = Column(Integer, ForeignKey('client_types.id', ondelete='RESTRICT'), nullable=False)
    client_types = relationship('ClientTypes', back_populates='clients')
    addresses = relationship('Addresses', back_populates='clients', cascade='all, delete-orphan')
    contacts = relationship('Contacts', back_populates='clients', cascade='all, delete-orphan')
    services = relationship('Services', back_populates='clients', cascade='all, delete-orphan')

class Vendors(Base):
    __tablename__ = 'vendors'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    contacts = relationship('Contacts', back_populates='vendors', cascade='all, delete-orphan')
    addresses = relationship('Addresses', back_populates='vendors', cascade='all, delete-orphan')
    pops = relationship('Pops', back_populates='vendors', cascade='all, delete-orphan')

class ServiceTypes(Base):
    __tablename__ = 'service_types'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    services = relationship('Services', back_populates='service_types')

class Pops(Base):
    __tablename__ = 'pops'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    owner = Column(Integer, ForeignKey('vendors.id'), nullable=False)
    extra_info = Column(String)
    vendors = relationship('Vendors', back_populates='pops')
    services = relationship('Services', back_populates='pops')

class Services(Base):
    __tablename__ = 'services'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    point = Column(String, nullable=False)
    service_type_id = Column(Integer, ForeignKey('service_types.id', ondelete='RESTRICT'), nullable=False)
    bandwidth = Column(Integer, nullable=False)
    extra_info = Column(String)
    pop_id = Column(Integer, ForeignKey('pops.id', ondelete='RESTRICT'), nullable=False)
    clients = relationship('Clients', back_populates='services')
    contacts = relationship('Contacts', back_populates='services')
    addresses = relationship('Addresses', back_populates='services')
    service_types = relationship('ServiceTypes', back_populates='services')
    pops = relationship('Pops', back_populates='services')

class Addresses(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    flat = Column(String)
    floor = Column(String)
    holding = Column(String, nullable=False)
    street = Column(String, nullable=False)
    area = Column(String, nullable=False)
    thana = Column(String, nullable=False)
    district = Column(String, nullable=False)
    client_id = Column(Integer, ForeignKey('clients.id', ondelete='RESTRICT'))
    service_id = Column(Integer, ForeignKey('services.id', ondelete='RESTRICT'))
    vendor_id = Column(Integer, ForeignKey('vendors.id', ondelete='RESTRICT'))
    extra_info = Column(String)
    clients = relationship('Clients', back_populates='addresses')
    services = relationship('Services', back_populates='addresses')
    vendors = relationship('Vendors', back_populates='addresses')

class Contacts(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    designation = Column(String)
    type = Column(String)
    phone1 = Column(String)
    phone2 = Column(String)
    phone3 = Column(String)
    client_id = Column(Integer, ForeignKey('clients.id', ondelete='RESTRICT'))
    vendor_id = Column(Integer, ForeignKey('vendors.id', ondelete='RESTRICT'))
    service_id = Column(Integer, ForeignKey('services.id', ondelete='RESTRICT'))
    clients = relationship('Clients', back_populates='contacts')
    vendors = relationship('Vendors', back_populates='contacts')
    services = relationship('Services', back_populates='contacts')

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_name = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String)
    disabled = Column(Boolean, nullable=False)
    password = Column(String, nullable=False)
    scope = Column(String, nullable=False)