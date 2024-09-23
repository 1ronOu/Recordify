"""added new table songs and enhanced table users with is_active column

Revision ID: 46b4c7c2a83e
Revises: 446b370ebf68
Create Date: 2024-08-29 14:37:08.752930

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '46b4c7c2a83e'
down_revision: Union[str, None] = '446b370ebf68'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
