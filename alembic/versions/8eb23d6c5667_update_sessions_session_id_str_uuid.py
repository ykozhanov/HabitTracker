"""Update sessions (session_id str -> UUID)

Revision ID: 8eb23d6c5667
Revises: 4fc2e49bbd9d
Create Date: 2024-11-07 17:32:55.627276

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8eb23d6c5667'
down_revision: Union[str, None] = '4fc2e49bbd9d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Сначала создаем временный столбец для хранения UUID
    op.add_column('sessions', sa.Column('session_id_temp', sa.UUID(), nullable=False))

    # Копируем данные из старого столбца в новый, преобразуя их в UUID
    op.execute("""
        UPDATE sessions
        SET session_id_temp = session_id::uuid
    """)

    # Удаляем старый столбец
    op.drop_column('sessions', 'session_id')

    # Переименовываем временный столбец в оригинальное имя
    op.alter_column('sessions', 'session_id_temp', new_column_name='session_id')


def downgrade() -> None:
    # Обратная миграция: создаем временный столбец для хранения VARCHAR
    op.add_column('sessions', sa.Column('session_id_temp', sa.VARCHAR(length=36), nullable=False))

    # Копируем данные из старого столбца в новый, преобразуя их в VARCHAR
    op.execute("""
        UPDATE sessions
        SET session_id_temp = session_id::text
    """)

    # Удаляем старый столбец
    op.drop_column('sessions', 'session_id')

    # Переименовываем временный столбец в оригинальное имя
    op.alter_column('sessions', 'session_id_temp', new_column_name='session_id')

