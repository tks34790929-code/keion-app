import os
from collections.abc import Iterator

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session, sessionmaker


def make_db_url(database: str) -> URL:
    """指定したデータベースへの接続 URL を作る（開発用とテスト用で共通）"""
    # 接続情報は compose.yaml から環境変数で受け取る。
    # URL.create を使うと、パスワードに記号が入っていても正しく組み立てられる。
    return URL.create(
        "mysql+pymysql",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        database=database,
    )


# pool_pre_ping: 使う前に接続が生きているか確認する（DB 再起動後のエラーを防ぐ）
engine = create_engine(make_db_url(os.environ["DB_NAME"]), pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


def get_db() -> Iterator[Session]:
    """API 1回分の DB セッションを渡し、終わったら閉じる（FastAPI の Depends で使う）"""
    with SessionLocal() as db:
        yield db
