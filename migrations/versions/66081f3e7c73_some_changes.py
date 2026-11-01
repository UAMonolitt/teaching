"""some changes

Revision ID: 66081f3e7c73
Revises: 743e577598d4
Create Date: 2026-10-10 10:55:16.579987

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '66081f3e7c73'
down_revision: Union[str, Sequence[str], None] = '743e577598d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(table_name='test_table', column=sa.Column('password', sa.String(64)))
    op.create_table('another_test_table', sa.Column('id', sa.Integer), sa.Column('test_table_id', sa.Integer))
    op.create_foreign_key('test_table_address', 'another_test_table', 'test_table', ['test_table_id'], ['id'])
    op.create_primary_key('pk_another_test_table', 'another_test_table', ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('test_table', 'password')
    op.drop_constraint('test_table_address', 'another_test_table')
    op.drop_constraint('pk_another_test_table', 'another_test_table')
    op.drop_table('another_test_table')
