"""Insert data into department table

Revision ID: fc1b98f5930b
Revises: b5c4316c140a
Create Date: 2024-02-21 06:25:53.570261

"""
from typing import Sequence, Union
from sqlalchemy import Table, MetaData, Column, Integer, String
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'fc1b98f5930b'
down_revision: Union[str, None] = 'b5c4316c140a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Get the departments table object from your database model
    metadata = MetaData()

    departments = Table(
        'departments',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String),
        schema='public'
    )

    # Insert data into the departments table
    op.bulk_insert(departments, [
        {'id': 4, 'name': 'Main Department'},
        {'id': 5, 'name': 'HR Department'}
    ])

def downgrade() -> None:
    pass
