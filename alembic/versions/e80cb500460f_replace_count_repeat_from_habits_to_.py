"""Replace count_repeat from habits to habittracker

Revision ID: e80cb500460f
Revises: 7e79a42d2918
Create Date: 2024-10-30 13:20:46.992925

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e80cb500460f'
down_revision: Union[str, None] = '7e79a42d2918'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('habits', sa.Column('count_repeat', sa.Integer(), nullable=True))
    op.drop_column('habittracker', 'count_repeat')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('habittracker', sa.Column('count_repeat', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('habits', 'count_repeat')
    # ### end Alembic commands ###
