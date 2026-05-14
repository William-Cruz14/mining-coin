from pydantic import BaseModel


class WinsDTO(BaseModel):
    tag: str
    revenue: float
    revenue24: float
    profit: float
    profit24: float

