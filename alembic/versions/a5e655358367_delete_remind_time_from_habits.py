"""Delete remind_time from habits

Revision ID: a5e655358367
Revises: 87222ec633da
Create Date: 2024-10-30 13:14:41.185196

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a5e655358367'
down_revision: Union[str, None] = '87222ec633da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('habits', 'remind_time')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('habits', sa.Column('remind_time', postgresql.TIME(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###