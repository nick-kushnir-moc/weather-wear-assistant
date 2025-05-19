"""Create join employee department table

Revision ID: 231d65732fa7
Revises: 2edaec299ace
Create Date: 2024-03-06 04:50:26.093951

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '231d65732fa7'
down_revision: Union[str, None] = '2edaec299ace'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'employee_department',
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('department_id', sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='CASCADE')
    )

def downgrade():
    op.drop_table('employee_department')
