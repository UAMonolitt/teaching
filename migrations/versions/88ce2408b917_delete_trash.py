"""delete trash

Revision ID: 88ce2408b917
Revises: 66081f3e7c73
Create Date: 2026-10-10 12:07:03.012303

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '88ce2408b917'
down_revision: Union[str, Sequence[str], None] = '66081f3e7c73'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_table('another_test_table')
    op.drop_table('test_table')


def downgrade() -> None:
    """Downgrade schema."""
    op.create_table('test_table', sa.Column('id', sa.Integer, primary_key=True), sa.Column('username', sa.String(50)))