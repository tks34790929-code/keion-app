"""create reservations

予約テーブルを作る（Sprint 1: 個人練のみ）

Revision ID: 8d337febe110
Revises:
Create Date: 2026-10-06 18:30:02.625004
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "8d337febe110"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "reservations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("kind", sa.Enum("individual", name="reservation_kind"), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("reserved_date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("start_time < end_time", name="ck_reservations_start_before_end"),
        sa.CheckConstraint(
            "start_time >= '07:00:00' AND end_time <= '22:00:00'",
            name="ck_reservations_open_hours",
        ),
        sa.CheckConstraint(
            "MOD(MINUTE(start_time), 10) = 0 AND SECOND(start_time) = 0"
            " AND MOD(MINUTE(end_time), 10) = 0 AND SECOND(end_time) = 0",
            name="ck_reservations_10min_unit",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_reservations_reserved_date"), "reservations", ["reserved_date"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_reservations_reserved_date"), table_name="reservations")
    op.drop_table("reservations")
