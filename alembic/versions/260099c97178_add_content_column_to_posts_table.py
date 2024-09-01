"""add content column to posts table

Revision ID: 260099c97178
Revises: 05f99a4771de
Create Date: 2024-09-01 22:36:15.531111

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '260099c97178'
down_revision: Union[str, None] = '05f99a4771de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'content')
    pass
