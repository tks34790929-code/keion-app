import os
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException
from sqlalchemy import URL, create_engine, text
from sqlalchemy.exc import SQLAlchemyError

JST = ZoneInfo("Asia/Tokyo")

# 接続情報は compose.yaml から環境変数で受け取る。
# URL.create を使うと、パスワードに記号が入っていても正しく組み立てられる。
db_url = URL.create(
    "mysql+pymysql",
    username=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.environ["DB_HOST"],
    port=int(os.environ["DB_PORT"]),
    database=os.environ["DB_NAME"],
)
# pool_pre_ping: 使う前に接続が生きているか確認する（DB 再起動後のエラーを防ぐ）
engine = create_engine(db_url, pool_pre_ping=True)

app = FastAPI(title="keion-app API")


@app.get("/api/hello")
def hello() -> dict[str, str]:
    return {
        "message": "Hello from FastAPI",
        "now": datetime.now(JST).isoformat(timespec="seconds"),
    }


@app.get("/api/health/db")
def health_db() -> dict[str, str]:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except SQLAlchemyError as e:
        raise HTTPException(status_code=503, detail="DB に接続できません") from e
    return {"db": "ok"}
