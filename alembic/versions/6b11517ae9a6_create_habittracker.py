"""Create habittracker

Revision ID: 6b11517ae9a6
Revises: 97e847791fc3
Create Date: 2024-10-29 17:30:30.073689

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b11517ae9a6'
down_revision: Union[str, None] = '97e847791fc3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('habittracker',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('remind_time', sa.Time(), nullable=False),
    sa.Column('count_repeat', sa.Integer(), nullable=True),
    sa.Column('habit_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['habit_id'], ['habits.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('habittracker')
    # ### end Alembic commands ###
