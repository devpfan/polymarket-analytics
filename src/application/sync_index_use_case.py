from sqlalchemy.dialects.postgresql import insert  # Inserción masiva nativa de Postgres
from src.infrastructure.api_client import PolymarketAPIClient
from src.infrastructure.database import SessionLocal, MarketIndexDB


class SyncIndexUseCase:
    def __init__(self, api_client: PolymarketAPIClient):
        self.api_client = api_client

    def execute(self):
        # 1. Traer los mercados desde la API
        markets = self.api_client.get_all_active_markets()

        if not markets:
            return

        db = SessionLocal()
        try:
            # 2. Convertir los modelos a una lista de diccionarios planos
            values = [
                {"id": m.id, "title": m.title, "category": m.category}
                for m in markets
            ]

            # 3. Procesar en lotes (chunks) de 1000 para optimizar memoria
            chunk_size = 1000
            for i in range(0, len(values), chunk_size):
                chunk = values[i:i + chunk_size]

                # Construir la sentencia completa
                stmt = insert(MarketIndexDB).values(chunk)

                # Definir comportamiento en conflicto: si el ID ya existe, actualiza los campos
                stmt = stmt.on_conflict_do_update(
                    index_elements=['id'],
                    set_={
                        'title': stmt.excluded.title,
                        'category': stmt.excluded.category
                    }
                )
                db.execute(stmt)

            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()