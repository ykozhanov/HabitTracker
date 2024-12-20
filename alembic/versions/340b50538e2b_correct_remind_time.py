"""Correct remind_time

Revision ID: 340b50538e2b
Revises: 55f079e1592e
Create Date: 2024-10-29 17:46:32.686630

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "340b50538e2b"
down_revision: Union[str, None] = "55f079e1592e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### handlers_commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "habits", "remind_time", existing_type=postgresql.TIME(), nullable=True
    )
    # ### end Alembic handlers_commands ###


def downgrade() -> None:
    # ### handlers_commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "habits", "remind_time", existing_type=postgresql.TIME(), nullable=False
    )
    # ### end Alembic handlers_commands ###
