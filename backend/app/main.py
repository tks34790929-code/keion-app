from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app import reservations
from app.db import engine

JST = ZoneInfo("Asia/Tokyo")

app = FastAPI(title="keion-app API")
app.include_router(reservations.router)


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
