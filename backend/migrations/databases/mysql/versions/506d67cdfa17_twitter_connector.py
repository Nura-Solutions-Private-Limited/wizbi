"""twitter connector

Revision ID: 506d67cdfa17
Revises: 665eaff2bc05
Create Date: 2025-06-12 22:31:55.028073

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '506d67cdfa17'
down_revision: Union[str, None] = '665eaff2bc05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'x_conn',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_name', sa.String(255), nullable=False),
        sa.Column('bearer_token', sa.String(512), nullable=True),
        sa.Column('access_token', sa.String(512), nullable=True),
        sa.Column('access_token_secret', sa.String(512), nullable=True),
        sa.Column('db_conn_id', sa.Integer(), sa.ForeignKey('db_conn.id'), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True)
    )


def downgrade() -> None:
    op.drop_table('x_conn')
