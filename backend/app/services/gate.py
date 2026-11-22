from __future__ import annotations

from fastapi import HTTPException

from app.services.core import current_biz_day

# 写闸建模：营业日内一旦存在一条『一致』互证流水，当日即封印。
# 封印只挡三个改动元数据/目录的写入口；只读总览与各列表照常可用。
# 判定完全由 verify_runs（biz_day + status）重放得出，不额外落状态位，
# 因此互证流水是唯一事实源，任何时刻都能重算出同一结论。
WRITE_DOORS = ("迁移完成", "保留销毁", "分区登记")
READ_ONLY = ("只读总览", "只读列表")

RULE = "营业日内存在 status='一致' 的互证流水 → 当日封印；仅按营业日切换解封"


def replay(conn, biz_day: str) -> dict:
    """重放某营业日的互证流水，得出封印结论。"""
    runs = [
        dict(r)
        for r in conn.execute(
            '''SELECT id, status, drift_count, detail, created_at, biz_day
               FROM verify_runs WHERE biz_day=? ORDER BY id''',
            (biz_day,),
        ).fetchall()
    ]
    hit = next((r for r in runs if r["status"] == "一致"), None)
    return {
        "营业日": biz_day,
        "规则": RULE,
        "封印": hit is not None,
        "依据流水": (
            {
                "id": hit["id"],
                "status": hit["status"],
                "drift_count": hit["drift_count"],
                "created_at": hit["created_at"],
            }
            if hit
            else None
        ),
        "重放流水": [
            {"id": r["id"], "status": r["status"], "drift_count": r["drift_count"], "created_at": r["created_at"]}
            for r in runs
        ],
    }


def _verdict(state: dict, door: str) -> dict:
    if not state["封印"]:
        return {"门": door, "允许": True, "因": "当日无一致互证流水，写闸放行"}
    hit = state["依据流水"]
    return {
        "门": door,
        "允许": False,
        "因": f"营业日 {state['营业日']} 已有互证一致流水 #{hit['id']}，当日封印",
    }


def decide(conn, door: str, biz_day: str | None = None) -> dict:
    day = biz_day or current_biz_day(conn)
    return _verdict(replay(conn, day), door)


def enforce(conn, door: str) -> None:
    """写入口在自身事务内调用；封印时抛 409，事务随异常回滚，半截写不会落库。"""
    if door not in WRITE_DOORS:
        raise ValueError(f"未知写入口：{door}")
    state = replay(conn, current_biz_day(conn))
    d = _verdict(state, door)
    if not d["允许"]:
        hit = state["依据流水"]
        raise HTTPException(
            409,
            detail=(
                f"{d['因']}（互证流水 #{hit['id']} · {hit['created_at']}），"
                f"拒绝{door}。只读总览与列表仍可用；切换营业日到当日无一致互证流水的新一天即解封。"
            ),
        )


def probe(conn, biz_day: str | None = None) -> dict:
    """写闸探针：逐门给出与真实写入口同一套判定的结论，另附可重放依据。"""
    day = biz_day or current_biz_day(conn)
    state = replay(conn, day)
    return {
        **state,
        "各口": [_verdict(state, d) for d in WRITE_DOORS]
        + [{"门": d, "允许": True, "因": "只读入口不受写闸限制"} for d in READ_ONLY],
        "解封": "切换营业日到当日尚无一致互证流水的一天；回到已封印的营业日会重新封印",
    }
