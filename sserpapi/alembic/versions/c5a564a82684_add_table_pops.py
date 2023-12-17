"""add table 'pops'

Revision ID: c5a564a82684
Revises: c47f810550f6
Create Date: 2023-12-17 17:39:40.490673

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5a564a82684'
down_revision: Union[str, None] = 'c47f810550f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('pops',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('owner', sa.Integer(), nullable=False),
    sa.Column('extra_info', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['owner'], ['vendors.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('services', sa.Column('pop_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'services', 'pops', ['pop_id'], ['id'])
    op.drop_column('services', 'connected_to')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('services', sa.Column('connected_to', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'services', type_='foreignkey')
    op.drop_column('services', 'pop_id')
    op.drop_table('pops')
    # ### end Alembic commands ###
