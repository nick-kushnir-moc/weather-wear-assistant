"""Description of the migration

Revision ID: 5a548d5e4068
Revises: fc1b98f5930b
Create Date: 2024-02-21 06:45:32.128336

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '5a548d5e4068'
down_revision: Union[str, None] = 'fc1b98f5930b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the foreign key constraints first
    op.drop_constraint('reservations_employee_id_fkey', 'reservations', type_='foreignkey')
    op.drop_constraint('employees_dept_id_fkey', 'employees', type_='foreignkey')
    op.drop_constraint('employees_hiring_personal_id_fkey', 'employees', type_='foreignkey')
    
    # Now drop the tables
    op.drop_table('reservations')
    op.drop_table('employees')
    op.drop_table('hiring_personal')
    op.drop_table('departments')

def downgrade() -> None:
    # Recreate the tables in reverse order
    op.create_table(
        'departments',
        sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('departments_id_seq'::regclass)"), autoincrement=True, nullable=False),
        sa.Column('name', sa.VARCHAR(length=30), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('id', name='departments_pkey'),
        sa.UniqueConstraint('name', name='departments_name_key'),
        postgresql_ignore_search_path=False
    )
    op.create_table(
        'hiring_personal',
        sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('hiring_personal_id_seq'::regclass)"), autoincrement=True, nullable=False),
        sa.Column('name', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
        sa.Column('age', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('gender', sa.CHAR(length=1), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('id', name='hiring_personal_pkey'),
        postgresql_ignore_search_path=False
    )
    op.create_table(
        'employees',
        sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('employees_id_seq'::regclass)"), autoincrement=True, nullable=False),
        sa.Column('name', sa.VARCHAR(length=40), autoincrement=False, nullable=False),
        sa.Column('salary', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('dept_id', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('hiring_personal_id', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['dept_id'], ['departments.id'], name='employees_dept_id_fkey'),
        sa.ForeignKeyConstraint(['hiring_personal_id'], ['hiring_personal.id'], name='employees_hiring_personal_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='employees_pkey'),
        postgresql_ignore_search_path=False
    )
    op.create_table(
        'reservations',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('employee_id', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('start_date', sa.DATE(), autoincrement=False, nullable=True),
        sa.Column('end_date', sa.DATE(), autoincrement=False, nullable=True),
        sa.Column('reservation_type', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('shift_start', postgresql.TIME(), autoincrement=False, nullable=True),
        sa.Column('shift_end', postgresql.TIME(), autoincrement=False, nullable=True),
        sa.Column('work_date', sa.DATE(), autoincrement=False, nullable=True),
        sa.CheckConstraint('reservation_type = ANY (ARRAY[1, 2, 3])', name='reservations_reservation_type_check'),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], name='reservations_employee_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='reservations_pkey')
    )

    # Re-add the foreign key constraints
    op.create_foreign_key('reservations_employee_id_fkey', 'reservations', 'employees', ['employee_id'], ['id'])
    op.create_foreign_key('employees_dept_id_fkey', 'employees', 'departments', ['dept_id'], ['id'])
    op.create_foreign_key('employees_hiring_personal_id_fkey', 'employees', 'hiring_personal', ['hiring_personal_id'], ['id'])
