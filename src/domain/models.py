from pydantic import BaseModel

class Market(BaseModel):
    id: str
    title: str
    category: str
    volume: float
    probability_yes: float
    active: bool