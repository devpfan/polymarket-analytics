import httpx
import json
from typing import List
from src.domain.models import Market


class PolymarketAPIClient:
    BASE_URL = "https://gamma-api.polymarket.com"

    def get_active_markets(self, limit: int = 20) -> List[Market]:
        """
        Obtiene los mercados activos y los mapea a nuestro modelo de dominio.
        """
        params = {
            "active": "true",
            "closed": "false",
            "limit": limit
        }

        with httpx.Client(base_url=self.BASE_URL) as client:
            response = client.get("/markets", params=params)
            response.raise_for_status()
            raw_data = response.json()

            markets = []
            for item in raw_data:
                # 1. Obtenemos el valor crudo
                prices_raw = item.get("outcomePrices")
                prices = []

                # 2. Verificamos si es un string (ej: '["0.65", "0.35"]') y lo parseamos
                if prices_raw:
                    if isinstance(prices_raw, str):
                        try:
                            prices = json.loads(prices_raw)
                        except json.JSONDecodeError:
                            prices = []
                    elif isinstance(prices_raw, list):
                        prices = prices_raw

                # 3. Ahora sí podemos extraer el primer elemento de forma segura
                prob_yes = float(prices[0]) * 100 if prices else 0.0

                markets.append(
                    Market(
                        id=item.get("id", ""),
                        title=item.get("question", "Desconocido"),
                        category="General",
                        volume=float(item.get("volume", 0.0)),
                        probability_yes=prob_yes,
                        active=item.get("active", True),
                        # Mapeando los nuevos campos:
                        description=item.get("description", "Sin descripción detallada."),
                        end_date=item.get("endDate", "No definida"),
                        resolution_source=item.get("resolutionSource", "Desconocida")
                    )
                )

            return markets