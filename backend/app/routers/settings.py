from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db import db
from app.services import gate

router = APIRouter(tags=["设置"])


class DayIn(BaseModel):
    营业日: str


@router.get("/设置")
def get_settings():
    with db() as conn:
        rows = conn.execute("SELECT key, value FROM settings").fetchall()
        return {r["key"]: r["value"] for r in rows}


@router.post("/设置/营业日")
def set_day(body: DayIn):
    # 切换营业日就是写闸的解封/复封杠杆：切到无一致流水的一天即解封，
    # 切回已封印的营业日则重新封印。响应带回新营业日的封印态，随切随见。
    with db(write=True) as conn:
        conn.execute(
            "INSERT INTO settings(key, value) VALUES ('营业日', ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (body.营业日,),
        )
        return {"营业日": body.营业日, "写闸": gate.probe(conn, body.营业日)}
