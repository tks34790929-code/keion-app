"""予約の一覧・作成 API のテスト（Issue #14 の受け入れ条件）

現在時刻は conftest.py の FIXED_NOW（2026-10-08 12:00）に固定している。
#15 の「1人1日1回」のルールと矛盾しないよう、予約ごとに別の名前を使う。
"""

import itertools

import pytest
from fastapi.testclient import TestClient
from httpx2 import Response
from sqlalchemy import Engine, text
from sqlalchemy.exc import DBAPIError

TODAY = "2026-10-08"
TOMORROW = "2026-10-09"

_names = (f"部員{i}" for i in itertools.count(1))


def reserve(
    client: TestClient,
    start: str,
    end: str,
    date: str = TOMORROW,
    name: str | None = None,
) -> Response:
    return client.post(
        "/api/reservations",
        json={
            "name": name if name is not None else next(_names),
            "date": date,
            "start_time": start,
            "end_time": end,
        },
    )


def list_on(client: TestClient, date: str) -> list[dict]:
    res = client.get("/api/reservations", params={"date": date})
    assert res.status_code == 200
    return res.json()


# ===== 一覧 =====


def test_一覧は指定した日の予約だけを開始時刻順に返す(client: TestClient) -> None:
    reserve(client, "18:00", "19:00")
    reserve(client, "09:00", "10:00")
    reserve(client, "13:00", "14:00")
    reserve(client, "09:00", "10:00", date="2026-10-10")

    starts = [r["start_time"] for r in list_on(client, TOMORROW)]

    assert starts == ["09:00:00", "13:00:00", "18:00:00"]


def test_予約がない日の一覧は空(client: TestClient) -> None:
    assert list_on(client, TOMORROW) == []


def test_一覧で予約者名と種類と時刻が分かる(client: TestClient) -> None:
    reserve(client, "15:10", "16:30", name="山田")

    [item] = list_on(client, TOMORROW)

    assert item["name"] == "山田"
    assert item["kind"] == "individual"
    assert (item["start_time"], item["end_time"]) == ("15:10:00", "16:30:00")


# ===== 作成 =====


def test_個人練を予約できる(client: TestClient) -> None:
    res = reserve(client, "15:10", "16:30", name="山田")

    assert res.status_code == 201
    body = res.json()
    assert body["kind"] == "individual"
    assert body["name"] == "山田"
    assert body["date"] == TOMORROW
    assert (body["start_time"], body["end_time"]) == ("15:10:00", "16:30:00")
    assert list_on(client, TOMORROW) == [body]


def test_名前の前後の空白は取り除かれる(client: TestClient) -> None:
    res = reserve(client, "10:00", "11:00", name="  山田　")

    assert res.json()["name"] == "山田"


@pytest.mark.parametrize("name", ["", "   "])
def test_名前が空なら予約できない(client: TestClient, name: str) -> None:
    res = reserve(client, "10:00", "11:00", name=name)

    assert res.status_code == 400
    assert res.json()["detail"] == "名前を入力してください"


def test_名前は50文字まで(client: TestClient) -> None:
    assert reserve(client, "10:00", "11:00", name="あ" * 50).status_code == 201

    res = reserve(client, "12:00", "13:00", name="あ" * 51)
    assert res.status_code == 400
    assert res.json()["detail"] == "名前は50文字以内で入力してください"


@pytest.mark.parametrize(
    ("start", "end"),
    [("07:05", "08:00"), ("07:00", "08:15"), ("07:00:30", "08:00")],
)
def test_10分単位でない時刻は予約できない(client: TestClient, start: str, end: str) -> None:
    res = reserve(client, start, end)

    assert res.status_code == 400
    assert res.json()["detail"] == "開始・終了時刻は10分単位で指定してください"


@pytest.mark.parametrize(
    ("start", "end"),
    [
        ("11:00", "13:00"),  # 後ろが重なる
        ("09:00", "10:10"),  # 前が重なる
        ("10:30", "11:30"),  # 既存の予約の中に入る
        ("09:00", "13:00"),  # 既存の予約を外側から包む
        ("10:00", "12:00"),  # まったく同じ時間
    ],
)
def test_他の予約と重なる時間は予約できない(client: TestClient, start: str, end: str) -> None:
    assert reserve(client, "10:00", "12:00").status_code == 201

    res = reserve(client, start, end)

    assert res.status_code == 409
    assert res.json()["detail"] == "その時間は既に予約されています（10:00〜12:00）"
    assert len(list_on(client, TOMORROW)) == 1


@pytest.mark.parametrize(("start", "end"), [("08:00", "10:00"), ("12:00", "14:00")])
def test_終了と開始がぴったり接する予約はできる(client: TestClient, start: str, end: str) -> None:
    assert reserve(client, "10:00", "12:00").status_code == 201

    assert reserve(client, start, end).status_code == 201


def test_別の日なら同じ時間でも予約できる(client: TestClient) -> None:
    assert reserve(client, "10:00", "12:00").status_code == 201

    assert reserve(client, "10:00", "12:00", date="2026-10-10").status_code == 201


@pytest.mark.parametrize(
    ("date", "start", "end"),
    [
        (TODAY, "11:50", "13:00"),  # 今日の、既に過ぎた時刻に始まる
        ("2026-10-07", "15:00", "16:00"),  # 昨日
    ],
)
def test_過去の時刻は予約できない(client: TestClient, date: str, start: str, end: str) -> None:
    res = reserve(client, start, end, date=date)

    assert res.status_code == 400
    assert res.json()["detail"] == "過去の時刻は予約できません"


@pytest.mark.parametrize("start", ["12:00", "12:10"])
def test_今の時刻以降に始まる予約はできる(client: TestClient, start: str) -> None:
    assert reserve(client, start, "13:00", date=TODAY).status_code == 201


@pytest.mark.parametrize(("start", "end"), [("06:50", "08:00"), ("21:00", "22:10")])
def test_7時から22時の範囲外は予約できない(client: TestClient, start: str, end: str) -> None:
    res = reserve(client, start, end)

    assert res.status_code == 400
    assert res.json()["detail"] == "予約できるのは07:00〜22:00の間です"


@pytest.mark.parametrize(("start", "end"), [("07:00", "08:00"), ("21:00", "22:00")])
def test_7時から22時の範囲の端は予約できる(client: TestClient, start: str, end: str) -> None:
    assert reserve(client, start, end).status_code == 201


@pytest.mark.parametrize(("start", "end"), [("10:00", "09:00"), ("10:00", "10:00")])
def test_開始が終了より後か同じなら予約できない(client: TestClient, start: str, end: str) -> None:
    res = reserve(client, start, end)

    assert res.status_code == 400
    assert res.json()["detail"] == "終了時刻は開始時刻より後にしてください"


# ===== DB の CHECK 制約 =====


@pytest.mark.parametrize(
    ("start", "end"),
    [
        ("10:00", "09:00"),  # 開始が終了より後
        ("06:50", "08:00"),  # 範囲外
        ("10:05", "11:00"),  # 10分単位でない
    ],
)
def test_DBもルール違反のデータを保存しない(engine: Engine, start: str, end: str) -> None:
    """API を通さずに保存しようとしても、DB が拒否する"""
    with pytest.raises(DBAPIError):
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO reservations"
                    " (kind, name, reserved_date, start_time, end_time, created_at)"
                    " VALUES ('individual', '山田', :date, :start, :end, NOW())"
                ),
                {"date": TOMORROW, "start": start, "end": end},
            )
