"""テストの準備（pytest が自動で読み込む）

- テスト用データベース（TEST_DB_NAME）に、本番と同じマイグレーションでテーブルを作る
- 「現在時刻」を FIXED_NOW に固定し、いつ実行しても同じ結果になるようにする
- テストが1つ終わるたびに予約を全件削除する
"""

import datetime as dt
import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.db import get_db, make_db_url
from app.main import app
from app.reservations import JST, get_now

TEST_DB_NAME = os.environ["TEST_DB_NAME"]
# 開発用データベースの中身を消さないための安全装置
if not TEST_DB_NAME.endswith("_test"):
    raise RuntimeError(f"テスト用データベースの名前が _test で終わっていません: {TEST_DB_NAME}")

ALEMBIC_INI = Path(__file__).resolve().parents[1] / "alembic.ini"

# テストでの「現在時刻」
FIXED_NOW = dt.datetime(2026, 10, 8, 12, 0, tzinfo=JST)


@pytest.fixture(scope="session")
def engine() -> Iterator[Engine]:
    """テスト全体で1回だけ、テーブルを作り直す"""
    engine = create_engine(make_db_url(TEST_DB_NAME))
    config = Config(ALEMBIC_INI)
    with engine.begin() as connection:
        # alembic/env.py は、この接続が渡されるとテスト用データベースに適用する
        config.attributes["connection"] = connection
        command.downgrade(config, "base")
        command.upgrade(config, "head")
    yield engine
    engine.dispose()


@pytest.fixture
def client(engine: Engine) -> Iterator[TestClient]:
    """テスト用データベースと固定の現在時刻を使う API クライアント"""
    TestSession = sessionmaker(bind=engine)

    def get_test_db() -> Iterator[Session]:
        with TestSession() as db:
            yield db

    app.dependency_overrides[get_db] = get_test_db
    app.dependency_overrides[get_now] = lambda: FIXED_NOW
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    with engine.begin() as connection:
        connection.execute(text("DELETE FROM reservations"))
