"""restapi connector update to include data url

Revision ID: 665eaff2bc05
Revises: 645d78efa42e
Create Date: 2025-03-08 15:21:15.973626

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '665eaff2bc05'
down_revision: Union[str, None] = '645d78efa42e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('rest_api_conn', sa.Column('data_url', sa.String(500), nullable=True))
    op.add_column('rest_api_conn', sa.Column('is_auth_url', sa.Boolean, nullable=True))


def downgrade() -> None:
    op.drop_column('rest_api_conn', 'data_url')
    op.drop_column('rest_api_conn', 'is_auth_url')
