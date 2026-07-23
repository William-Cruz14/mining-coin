from datetime import datetime

from pydantic import BaseModel


class CoinState(BaseModel):
    coin: str
    balance: int
    stale_cycles: int
    blacklisted_until: datetime | None = None


class BenchFull(BaseModel):
    os: str
    ram: float
    done_ts: datetime
    hashrate: float
    threads: int
    cpu_cores: int
    cpu_threads: int


class BenchResume(BaseModel):
    id: str
    threads_ok: bool
    done_ts: datetime
    version: str
    os: str
    cpu_count: int


