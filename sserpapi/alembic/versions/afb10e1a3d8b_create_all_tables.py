"""create all tables

Revision ID: afb10e1a3d8b
Revises: 
Create Date: 2024-02-12 16:38:13.598487

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'afb10e1a3d8b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('client_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('service_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('full_name', sa.String(), nullable=True),
    sa.Column('disabled', sa.Boolean(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('scope', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_user_name'), 'users', ['user_name'], unique=True)
    op.create_table('vendors',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('type', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('clients',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('client_type_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['client_type_id'], ['client_types.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_clients_name'), 'clients', ['name'], unique=True)
    op.create_table('pops',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('owner', sa.Integer(), nullable=False),
    sa.Column('extra_info', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['owner'], ['vendors.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('services',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('client_id', sa.Integer(), nullable=False),
    sa.Column('point', sa.String(), nullable=False),
    sa.Column('service_type_id', sa.Integer(), nullable=False),
    sa.Column('bandwidth', sa.Integer(), nullable=False),
    sa.Column('extra_info', sa.String(), nullable=True),
    sa.Column('pop_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
    sa.ForeignKeyConstraint(['pop_id'], ['pops.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['service_type_id'], ['service_types.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('addresses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('flat', sa.String(), nullable=True),
    sa.Column('floor', sa.String(), nullable=True),
    sa.Column('holding', sa.String(), nullable=False),
    sa.Column('street', sa.String(), nullable=False),
    sa.Column('area', sa.String(), nullable=False),
    sa.Column('thana', sa.String(), nullable=False),
    sa.Column('district', sa.String(), nullable=False),
    sa.Column('client_id', sa.Integer(), nullable=True),
    sa.Column('service_id', sa.Integer(), nullable=True),
    sa.Column('vendor_id', sa.Integer(), nullable=True),
    sa.Column('extra_info', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['service_id'], ['services.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('contacts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('designation', sa.String(), nullable=True),
    sa.Column('type', sa.String(), nullable=True),
    sa.Column('phone1', sa.String(), nullable=True),
    sa.Column('phone2', sa.String(), nullable=True),
    sa.Column('phone3', sa.String(), nullable=True),
    sa.Column('client_id', sa.Integer(), nullable=True),
    sa.Column('vendor_id', sa.Integer(), nullable=True),
    sa.Column('service_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['service_id'], ['services.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contacts_name'), 'contacts', ['name'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_contacts_name'), table_name='contacts')
    op.drop_table('contacts')
    op.drop_table('addresses')
    op.drop_table('services')
    op.drop_table('pops')
    op.drop_index(op.f('ix_clients_name'), table_name='clients')
    op.drop_table('clients')
    op.drop_table('vendors')
    op.drop_index(op.f('ix_users_user_name'), table_name='users')
    op.drop_table('users')
    op.drop_table('service_types')
    op.drop_table('client_types')
    # ### end Alembic commands ###
