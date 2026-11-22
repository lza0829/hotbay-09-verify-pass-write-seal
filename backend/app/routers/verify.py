from __future__ import annotations
from fastapi import APIRouter
from app.db import db
from app.services import gate
from app.services import verify as svc

router = APIRouter(tags=["互证"])


@router.get("/目录清单")
def inventory():
    return svc.inventory_list()


@router.get("/互证流水")
def runs():
    return svc.list_verify_runs()


@router.post("/互证")
def run():
    return svc.run_verify()


@router.get("/写闸探针")
def write_gate_probe(营业日: str | None = None):
    with db() as conn:
        return gate.probe(conn, 营业日)
