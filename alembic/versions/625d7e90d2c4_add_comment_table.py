"""Add comment table

Revision ID: 625d7e90d2c4
Revises: 69e0e99ba28a
Create Date: 2023-08-28 11:02:38.281904

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '625d7e90d2c4'
down_revision: Union[str, None] = '69e0e99ba28a'
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