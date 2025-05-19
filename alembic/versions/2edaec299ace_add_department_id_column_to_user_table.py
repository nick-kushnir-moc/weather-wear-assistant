"""Add department_id column to User table

Revision ID: 2edaec299ace
Revises: 5a548d5e4068
Create Date: 2024-02-28 04:39:38.955472

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2edaec299ace'
down_revision: Union[str, None] = '5a548d5e4068'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the new column 'department_id' to the User table
    op.add_column('user', sa.Column('department_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_user_department_id', 'user', 'departments', ['department_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_user_department_id', 'user', type_='foreignkey')
    # Remove the 'department_id' column from the User table
    op.drop_column('user', 'department_id')
