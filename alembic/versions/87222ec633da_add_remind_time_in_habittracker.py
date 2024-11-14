"""Add remind_time in habittracker

Revision ID: 87222ec633da
Revises: 213ed96019e9
Create Date: 2024-10-30 13:12:14.652944

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '87222ec633da'
down_revision: Union[str, None] = '213ed96019e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### handlers_commands auto generated by Alembic - please adjust! ###
    op.add_column('habittracker', sa.Column('remind_time', sa.Time(), nullable=False))
    # ### end Alembic handlers_commands ###


def downgrade() -> None:
    # ### handlers_commands auto generated by Alembic - please adjust! ###
    op.drop_column('habittracker', 'remind_time')
    # ### end Alembic handlers_commands ###
