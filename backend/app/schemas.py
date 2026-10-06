"""API が受け取るデータ・返すデータの形"""

import datetime as dt
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ReservationCreate(BaseModel):
    """予約を作るときに受け取るデータ"""

    name: str
    date: dt.date
    start_time: dt.time
    end_time: dt.time


class ReservationRead(BaseModel):
    """予約として返すデータ"""

    # DB のモデル（Reservation）から作れるようにする
    model_config = ConfigDict(from_attributes=True)

    id: int
    kind: Literal["individual"]
    name: str
    # DB の列名は reserved_date だが、API では date として返す
    date: dt.date = Field(validation_alias="reserved_date")
    start_time: dt.time
    end_time: dt.time
