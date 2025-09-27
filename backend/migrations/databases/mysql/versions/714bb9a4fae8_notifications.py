"""notifications

Revision ID: 714bb9a4fae8
Revises: 506d67cdfa17
Create Date: 2025-06-19 09:51:00.634744

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '714bb9a4fae8'
down_revision: Union[str, None] = '506d67cdfa17'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'notification',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, nullable=False),
        sa.Column('alert_datetime', sa.DateTime, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('source', sa.String(255), nullable=True),
        sa.Column('viewed', sa.Boolean, default=False, nullable=True),
    )


def downgrade() -> None:
    op.drop_table('notification')
