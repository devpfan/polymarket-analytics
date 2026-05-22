from pydantic import BaseModel
from typing import Optional

class Market(BaseModel):
    id: str
    title: str
    category: str
    volume: float
    probability_yes: float
    active: bool
    # Nuevos campos
    description: Optional[str] = "Sin descripción"
    end_date: Optional[str] = "No definida"
    resolution_source: Optional[str] = "Desconocida"