"""予約の一覧・作成 API"""

import datetime as dt
from collections.abc import Sequence
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Reservation
from app.schemas import ReservationCreate, ReservationRead

JST = ZoneInfo("Asia/Tokyo")

OPEN_TIME = dt.time(7, 0)  # 練習室を使える時間（開始）
CLOSE_TIME = dt.time(22, 0)  # 練習室を使える時間（終了）
SLOT_MINUTES = 10  # 予約の単位（分）
NAME_MAX_LENGTH = 50

# MySQL のデッドロックのエラー番号（2人が同時に同じ日を予約したときに起きることがある）
MYSQL_DEADLOCK = 1213

router = APIRouter(prefix="/api/reservations", tags=["reservations"])


def get_now() -> dt.datetime:
    """現在時刻（日本時間）。テストでは決まった時刻に差し替える"""
    return dt.datetime.now(JST)


def bad_request(message: str) -> HTTPException:
    return HTTPException(status_code=400, detail=message)


def fmt(t: dt.time) -> str:
    return t.strftime("%H:%M")


def is_slot_aligned(t: dt.time) -> bool:
    return t.minute % SLOT_MINUTES == 0 and t.second == 0 and t.microsecond == 0


def validate_new_reservation(name: str, body: ReservationCreate, now: dt.datetime) -> None:
    """他の予約と関係なく判定できる入力チェック。違反があれば理由付きの 400 エラーにする"""
    if not name:
        raise bad_request("名前を入力してください")
    if len(name) > NAME_MAX_LENGTH:
        raise bad_request(f"名前は{NAME_MAX_LENGTH}文字以内で入力してください")
    if not (is_slot_aligned(body.start_time) and is_slot_aligned(body.end_time)):
        raise bad_request(f"開始・終了時刻は{SLOT_MINUTES}分単位で指定してください")
    if body.start_time >= body.end_time:
        raise bad_request("終了時刻は開始時刻より後にしてください")
    if body.start_time < OPEN_TIME or body.end_time > CLOSE_TIME:
        raise bad_request(f"予約できるのは{fmt(OPEN_TIME)}〜{fmt(CLOSE_TIME)}の間です")
    start_at = dt.datetime.combine(body.date, body.start_time, tzinfo=JST)
    if start_at < now:
        raise bad_request("過去の時刻は予約できません")


def find_overlap(
    reservations: Sequence[Reservation], start: dt.time, end: dt.time
) -> Reservation | None:
    """時間が重なる予約を探す。終了と開始がぴったり接する場合は重ならないとみなす"""
    for r in reservations:
        if start < r.end_time and r.start_time < end:
            return r
    return None


@router.get("", response_model=list[ReservationRead])
def list_reservations(date: dt.date, db: Session = Depends(get_db)) -> Sequence[Reservation]:
    """指定した日の予約を開始時刻順に返す"""
    stmt = (
        select(Reservation)
        .where(Reservation.reserved_date == date)
        .order_by(Reservation.start_time)
    )
    return db.scalars(stmt).all()


@router.post("", response_model=ReservationRead, status_code=201)
def create_reservation(
    body: ReservationCreate,
    db: Session = Depends(get_db),
    now: dt.datetime = Depends(get_now),
) -> Reservation:
    """個人練の予約を作る"""
    name = body.name.strip()
    validate_new_reservation(name, body, now)

    # 同じ日の予約をロックしてから重なりを確認する。
    # ロックはコミットするまで続くので、確認してから保存するまでの間に
    # 他の人が同じ日に予約を入れることはできない。
    same_day = db.scalars(
        select(Reservation).where(Reservation.reserved_date == body.date).with_for_update()
    ).all()
    overlap = find_overlap(same_day, body.start_time, body.end_time)
    if overlap is not None:
        raise HTTPException(
            status_code=409,
            detail=(
                "その時間は既に予約されています"
                f"（{fmt(overlap.start_time)}〜{fmt(overlap.end_time)}）"
            ),
        )

    reservation = Reservation(
        kind="individual",
        name=name,
        reserved_date=body.date,
        start_time=body.start_time,
        end_time=body.end_time,
        created_at=now.replace(tzinfo=None),
    )
    db.add(reservation)
    try:
        db.commit()
    except OperationalError as e:
        db.rollback()
        if e.orig is not None and e.orig.args[0] == MYSQL_DEADLOCK:
            raise HTTPException(
                status_code=409,
                detail="他の人と同時に予約しようとしました。もう一度お試しください",
            ) from e
        raise
    db.refresh(reservation)
    return reservation
