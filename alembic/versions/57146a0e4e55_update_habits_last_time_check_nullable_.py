"""Update habits - last_time_check (nullable=True)

Revision ID: 57146a0e4e55
Revises: 146d9c4bad64
Create Date: 2024-11-09 16:45:31.681190

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "57146a0e4e55"
down_revision: Union[str, None] = "146d9c4bad64"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### handlers_commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "habits", "last_time_check", existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    # ### end Alembic handlers_commands ###


def downgrade() -> None:
    # ### handlers_commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "habits",
        "last_time_check",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
    )
    # ### end Alembic handlers_commands ###
