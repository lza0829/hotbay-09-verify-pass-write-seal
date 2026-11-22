from __future__ import annotations
import json
from app.db import db
from app.services.core import current_biz_day, now


def inventory_list():
    with db() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM inventory_objects ORDER BY object_key").fetchall()]


def run_verify():
    with db(write=True) as conn:
        biz_day = current_biz_day(conn)
        meta_keys = {
            r["object_key"]: r["bytes"]
            for r in conn.execute(
                '''SELECT c.object_key, c.bytes FROM clips c
                   JOIN partitions p ON p.id=c.partition_id
                   WHERE p.status IN ('在册','已过期')'''
            ).fetchall()
        }
        inv_keys = {
            r["object_key"]: r["bytes"]
            for r in conn.execute("SELECT object_key, bytes FROM inventory_objects").fetchall()
        }
        only_meta = sorted(set(meta_keys) - set(inv_keys))
        only_inv = sorted(set(inv_keys) - set(meta_keys))
        size_drift = sorted(
            k for k in set(meta_keys) & set(inv_keys) if meta_keys[k] != inv_keys[k]
        )
        drifts = []
        for k in only_meta:
            drifts.append({"对象键": k, "问题": "元数据有、目录无"})
        for k in only_inv:
            drifts.append({"对象键": k, "问题": "目录有、元数据无"})
        for k in size_drift:
            drifts.append({"对象键": k, "问题": "字节不一致"})
        status = "一致" if not drifts else "漂移"
        cur = conn.execute(
            "INSERT INTO verify_runs(status, drift_count, detail, created_at, biz_day) VALUES (?,?,?,?,?)",
            (status, len(drifts), json.dumps(drifts, ensure_ascii=False), now(), biz_day),
        )
        run_id = cur.lastrowid
        # 同一事务内取封印态，响应即反映本次互证落库后的真实闸态。
        from app.services.gate import probe as gate_probe

        seal = gate_probe(conn)
        return {
            "run_id": run_id,
            "status": status,
            "drift_count": len(drifts),
            "drifts": drifts,
            "meta_count": len(meta_keys),
            "inventory_count": len(inv_keys),
            "营业日": biz_day,
            "写闸": seal,
        }


def list_verify_runs():
    with db() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM verify_runs ORDER BY id DESC").fetchall()]
