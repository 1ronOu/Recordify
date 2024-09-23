"""add new units field in Record model

Revision ID: cfa3b6f7d09d
Revises: 75862c081f81
Create Date: 2024-09-21 11:54:31.174388

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cfa3b6f7d09d'
down_revision: Union[str, None] = '75862c081f81'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('records', sa.Column('unit', sa.String()))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('records', 'unit')
    # ### end Alembic commands ###
