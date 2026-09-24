"""quotaborrow.py：配额借用（基线：固定配额，不能借）。"""
from __future__ import annotations


class Allocator:
    def __init__(self, pool: int = 100, base: int = 40):
        self.pool = pool
        self.base = base
        self.used = {}
        self.borrowed = {}
        self.rejected = 0
        self.preemptions = 0

    def request(self, tenant: str, amount: int) -> dict:
        """基线：只看自己的基础配额。"""
        current = self.used.get(tenant, 0)
        if current + amount > self.base:
            self.rejected += 1
            return {"granted": False, "used": current}
        self.used[tenant] = current + amount
        return {"granted": True, "used": self.used[tenant]}

    def release(self, tenant: str, amount: int) -> dict:
        self.used[tenant] = max(0, self.used.get(tenant, 0) - amount)
        return {"used": self.used[tenant]}

    def reclaim(self, tenant: str) -> dict:
        raise NotImplementedError("抢占归还还没实现")

    def recover(self) -> dict:
        raise NotImplementedError("重启恢复还没实现")

    def stats(self) -> dict:
        return {"pool": self.pool, "base": self.base, "used": dict(self.used),
                "borrowed": dict(self.borrowed), "rejected": self.rejected,
                "preemptions": self.preemptions}
