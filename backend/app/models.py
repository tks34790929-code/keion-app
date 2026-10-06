from datetime import date, datetime, time

from sqlalchemy import CheckConstraint, Enum, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """全テーブルの共通の親クラス"""


class Reservation(Base):
    """練習室の予約（Sprint 1 は個人練のみ）"""

    __tablename__ = "reservations"
    # DB 自体にもルールを持たせ、アプリにバグがあってもおかしなデータが入らないようにする。
    # 時間の重なりは CHECK 制約では表せないので、アプリ側（reservations.py）で確認する。
    __table_args__ = (
        CheckConstraint("start_time < end_time", name="ck_reservations_start_before_end"),
        CheckConstraint(
            "start_time >= '07:00:00' AND end_time <= '22:00:00'",
            name="ck_reservations_open_hours",
        ),
        # % は PyMySQL で特別な意味を持つため、余りの計算には MOD を使う
        CheckConstraint(
            "MOD(MINUTE(start_time), 10) = 0 AND SECOND(start_time) = 0"
            " AND MOD(MINUTE(end_time), 10) = 0 AND SECOND(end_time) = 0",
            name="ck_reservations_10min_unit",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    # 予約の種類。Sprint 3 でバンド練（'band'）を追加する
    kind: Mapped[str] = mapped_column(Enum("individual", name="reservation_kind"))
    # 予約者名（ログインができるまでの仮の仕組み）
    name: Mapped[str] = mapped_column(String(50))
    reserved_date: Mapped[date] = mapped_column(index=True)
    start_time: Mapped[time]
    end_time: Mapped[time]
    # 予約した日時（日本時間）
    created_at: Mapped[datetime]
