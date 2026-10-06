"""Alembic がマイグレーションを実行するときに読み込む設定"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy.engine import Connection

from app.db import engine
from app.models import Base

config = context.config

# alembic.ini のログ設定を使う
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

# モデルの定義（autogenerate でテーブルとの差分を調べるときに使う）
target_metadata = Base.metadata


def run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


# テスト（tests/conftest.py）から接続が渡された場合は、その接続（テスト用データベース）を使う。
# それ以外は app/db.py の開発用データベースに接続する。
connection = config.attributes.get("connection")
if connection is not None:
    run_migrations(connection)
else:
    with engine.connect() as connection:
        run_migrations(connection)
