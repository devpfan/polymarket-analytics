from typing import List
from src.infrastructure.api_client import PolymarketAPIClient
from src.domain.models import Market

class FetchActiveMarketsUseCase:
    """
    Caso de uso para obtener los mercados activos actuales.
    Recibe las dependencias inyectadas para facilitar el testing.
    """
    def __init__(self, api_client: PolymarketAPIClient):
        self.api_client = api_client

    def execute(self, limit: int = 20) -> List[Market]:
        # Aquí en el futuro podríamos agregar lógica adicional,
        # como filtrar mercados inválidos o cruzar con otras fuentes.
        return self.api_client.get_active_markets(limit=limit)