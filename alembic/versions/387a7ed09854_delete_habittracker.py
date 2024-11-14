"""Delete habittracker

Revision ID: 387a7ed09854
Revises: 9acd2ccb14db
Create Date: 2024-10-29 17:38:31.277749

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '387a7ed09854'
down_revision: Union[str, None] = '9acd2ccb14db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### handlers_commands auto generated by Alembic - please adjust! ###
    op.drop_table('habittracker')
    # ### end Alembic handlers_commands ###


def downgrade() -> None:
    # ### handlers_commands auto generated by Alembic - please adjust! ###
    op.create_table('habittracker',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('remind_time', postgresql.TIME(), autoincrement=False, nullable=False),
    sa.Column('count_repeat', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('habit_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['habit_id'], ['habits.id'], name='habittracker_habit_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='habittracker_pkey')
    )
    # ### end Alembic handlers_commands ###
