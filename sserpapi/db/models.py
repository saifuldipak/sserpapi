from db.connection import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

class Clients(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True, nullable=False)
    client_type_id = Column(Integer, ForeignKey('client_types.id'), nullable=False)
    client_type = relationship('ClientTypes', back_populates='clients')
    addresses = relationship('Addresses', back_populates='clients', cascade='all, delete-orphan')
    contacts = relationship('Contacts', back_populates='clients', cascade='all, delete-orphan')
    services = relationship('Services', back_populates='clients', cascade='all, delete-orphan')

class Contacts(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    designation = Column(String)
    type = Column(String)
    phone1 = Column(String)
    phone2 = Column(String)
    phone3 = Column(String)
    client_id = Column(Integer, ForeignKey('clients.id'))
    vendor_id = Column(Integer, ForeignKey('vendors.id'))
    service_id = Column(Integer, ForeignKey('services.id'))
    clients = relationship('Clients', back_populates='contacts')
    vendors = relationship('Vendors', back_populates='contacts')
    services = relationship('Services', back_populates='contacts')

class Vendors(Base):
    __tablename__ = 'vendors'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    contacts = relationship('Contacts', back_populates='vendors', cascade='all, delete-orphan')
    addresses = relationship('Addresses', back_populates='vendors', cascade='all, delete-orphan')
    leased_links = relationship('LeasedLinks', back_populates='vendors', cascade='all, delete-orphan')

class Services(Base):
    __tablename__ = 'services'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    point = Column(String, nullable=False)
    type = Column(String, nullable=False)
    bandwidth = Column(Integer)
    connected_to = Column(String)
    extra_info = Column(String)
    clients = relationship('Clients', back_populates='services')
    leased_links = relationship('LeasedLinks', back_populates='services')
    contacts = relationship('Contacts', back_populates='services')
    addresses = relationship('Addresses', back_populates='services')

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

class Addresses(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)
    flat = Column(String)
    floor = Column(String)
    holding = Column(String)
    street = Column(String)
    thana = Column(String)
    district = Column(String)
    client_id = Column(Integer, ForeignKey('clients.id'))
    service_id = Column(Integer, ForeignKey('services.id'))
    vendor_id = Column(Integer, ForeignKey('vendors.id'))
    clients = relationship('Clients', back_populates='addresses')
    services = relationship('Services', back_populates='addresses')
    vendors = relationship('Vendors', back_populates='addresses')

class LeasedLinks(Base):
    __tablename__ = 'leased_links'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    link_from = Column(String, nullable=False)
    link_to = Column(String, nullable=False)
    vendor_id = Column(Integer, ForeignKey('vendors.id'))
    service_id = Column(Integer, ForeignKey('services.id'))
    vendors = relationship('Vendors', back_populates='leased_links')
    services = relationship('Services', back_populates='leased_links')