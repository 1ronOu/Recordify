"""first revision

Revision ID: 446b370ebf68
Revises: 
Create Date: 2024-08-28 18:08:17.769194

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '446b370ebf68'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('users',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('username', sa.String(), nullable=False),
                    sa.Column('email', sa.String(), nullable=False),
                    sa.Column('hashed_password', sa.String(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    pass
