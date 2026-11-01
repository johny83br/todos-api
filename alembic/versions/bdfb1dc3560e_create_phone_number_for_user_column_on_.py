"""Create phone number for user column on users table

Revision ID: bdfb1dc3560e
Revises:
Create Date: 2026-10-31 19:57:45.434304

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bdfb1dc3560e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('phone_number', sa.String(),
                                     nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'phone_number')
