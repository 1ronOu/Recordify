"""add new field record_name

Revision ID: 4f5ec4b9c3ac
Revises: afd4b2bd0343
Create Date: 2024-09-16 17:32:53.814085

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4f5ec4b9c3ac'
down_revision: Union[str, None] = 'afd4b2bd0343'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('records', sa.Column('record_name', sa.String(), nullable=True))
    op.create_unique_constraint(None, 'records', ['record_name'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'records', type_='unique')
    op.drop_column('records', 'record_name')
    # ### end Alembic commands ###
