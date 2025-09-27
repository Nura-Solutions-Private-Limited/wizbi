"""load connector type data

Revision ID: 645d78efa42e
Revises: 1bc769123372
Create Date: 2025-02-25 09:34:41.359043

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '645d78efa42e'
down_revision: Union[str, None] = '1bc769123372'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
            insert into connector_type(connector_type, description, type, enabled)
            values ('MYSQL', 'MySql', 'Database', True),
               ('POSTGRES', 'PostgreSQL', 'Database', True),
               ('MSSQL', 'Microsoft SQL Server', 'Database', True),
               ('REDSHIFT', 'Amazon Redshift', 'Database', True),
               ('GA', 'Google Analytics', 'Database', True),
               ('S3', 'Amazon S3', 'Csv', True),
               ('LFS', 'File System', 'Csv', True),
               ('GDRIVE', 'Google Drive', 'Csv', True),
               ('ICEBERG', 'Iceberg', 'Database', True),
               ('DUCKDB', 'DuckDB', 'DuckDB', True),
               ('ORACLE', 'Oracle', 'Database', True),
               ('RESTAPI', 'Rest API', 'RestAPI', True);
    """)


def downgrade() -> None:
    op.execute("""
        delete from connector_type where connector_type in ('MYSQL', 'POSTGRES', 'MSSQL', 'REDSHIFT', 'GA',
               'S3', 'LFS', 'GDRIVE', 'ICEBERG', 'DUCKDB', 'ORACLE', 'RESTAPI');
    """)
