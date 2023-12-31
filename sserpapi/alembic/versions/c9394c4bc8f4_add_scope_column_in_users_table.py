"""Add "scope" column in "users" table

Revision ID: c9394c4bc8f4
Revises: a5b3be35c1ca
Create Date: 2023-10-05 16:44:12.786981

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9394c4bc8f4'
down_revision: Union[str, None] = 'a5b3be35c1ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('scope', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'scope')
    # ### end Alembic commands ###
