"""Add course level with a three-step migration."""

from alembic import op
import sqlalchemy as sa


revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Сначала разрешаем пустые значения.
    op.add_column(
        "courses",
        sa.Column("level", sa.Text(), nullable=True),
    )

    # Заполняем уровень существующих курсов.
    op.execute(
        """
        UPDATE courses
        SET level = CASE
            WHEN is_elective THEN 'beginner'
            ELSE 'intermediate'
        END
        """
    )

    # Теперь делаем поле обязательным.
    op.alter_column(
        "courses",
        "level",
        existing_type=sa.Text(),
        nullable=False,
    )


def downgrade() -> None:
    op.drop_column("courses", "level")