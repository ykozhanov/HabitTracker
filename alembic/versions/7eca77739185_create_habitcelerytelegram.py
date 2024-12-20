"""Create habitcelerytelegram

Revision ID: 7eca77739185
Revises: e80cb500460f
Create Date: 2024-10-30 13:44:37.339053

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7eca77739185"
down_revision: Union[str, None] = "e80cb500460f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### handlers_commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "habitcelerytelegram",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("celery_task_id", sa.Integer(), nullable=True),
        sa.Column("habit_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["habit_id"],
            ["habits.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("celery_task_id"),
    )
    # ### end Alembic handlers_commands ###


def downgrade() -> None:
    # ### handlers_commands auto generated by Alembic - please adjust! ###
    op.drop_table("habitcelerytelegram")
    # ### end Alembic handlers_commands ###
