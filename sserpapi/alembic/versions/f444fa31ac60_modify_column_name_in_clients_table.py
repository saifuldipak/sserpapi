"""Modify column name in 'clients' table

Revision ID: f444fa31ac60
Revises: 0bd714da1dd9
Create Date: 2023-11-29 15:03:20.275448

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f444fa31ac60'
down_revision: Union[str, None] = '0bd714da1dd9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
