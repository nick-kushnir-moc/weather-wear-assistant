"""Create employees table

Revision ID: 9e96c7a479b1
Revises: 231d65732fa7
Create Date: 2024-03-06 05:02:23.834904

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e96c7a479b1'
down_revision: Union[str, None] = '231d65732fa7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'employees',
        sa.Column('id', sa.Integer(), server_default=sa.text("nextval('employees_id_seq'::regclass)"), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=40), nullable=False),
        sa.Column('salary', sa.Integer(), nullable=True),
        sa.Column('dept_id', sa.Integer(), nullable=True),
        sa.Column('hiring_personal_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['dept_id'], ['departments.id'], name='employees_dept_id_fkey'),
        sa.ForeignKeyConstraint(['hiring_personal_id'], ['hiring_personal.id'], name='employees_hiring_personal_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='employees_pkey')
    )


def downgrade():
    op.drop_table('employees')
