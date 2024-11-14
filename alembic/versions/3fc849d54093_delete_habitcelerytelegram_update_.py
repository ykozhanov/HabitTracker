"""Delete habitcelerytelegram, update habits and habittracker

Revision ID: 3fc849d54093
Revises: b90590c4deb6
Create Date: 2024-11-07 09:51:19.783336

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3fc849d54093'
down_revision: Union[str, None] = 'b90590c4deb6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### handlers_commands auto generated by Alembic - please adjust! ###
    op.drop_table('habitcelerytelegram')
    op.drop_column('habits', 'count_repeat')
    op.add_column('habittracker', sa.Column('count_repeat', sa.Integer(), nullable=True))
    # ### end Alembic handlers_commands ###


def downgrade() -> None:
    # ### handlers_commands auto generated by Alembic - please adjust! ###
    op.drop_column('habittracker', 'count_repeat')
    op.add_column('habits', sa.Column('count_repeat', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_table('habitcelerytelegram',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('celery_task_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('habit_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['habit_id'], ['habits.id'], name='habitcelerytelegram_habit_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='habitcelerytelegram_pkey'),
    sa.UniqueConstraint('celery_task_id', name='habitcelerytelegram_celery_task_id_key')
    )
    # ### end Alembic handlers_commands ###
