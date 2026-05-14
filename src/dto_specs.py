from pydantic import BaseModel
from datetime import datetime

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


