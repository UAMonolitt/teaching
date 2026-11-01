"""new column and column name changes

Revision ID: 40c2cf66e511
Revises: 88ce2408b917
Create Date: 2026-10-10 16:38:37.936557

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '40c2cf66e511'
down_revision: Union[str, Sequence[str], None] = '88ce2408b917'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('screenshots', 'screenshot_id', new_column_name='id')
    op.alter_column('screenshots', 'screenshot_name', new_column_name='name')
    op.alter_column('screenshots', 'screenshot_date', new_column_name='date')
    op.add_column('screenshots', sa.Column('public', sa.Boolean, server_default=sa.false()))

def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('screenshots', 'id', new_column_name='screenshot_id')
    op.alter_column('screenshots', 'name', new_column_name='screenshot_name')
    op.alter_column('screenshots', 'date', new_column_name='screenshot_date')
    op.drop_column('screenshots', 'public')