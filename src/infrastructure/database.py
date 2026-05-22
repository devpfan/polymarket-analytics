from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import declarative_base, sessionmaker

# Ajusta esto con tus credenciales reales (host, user, pass)
DATABASE_URL = "postgresql://admin:admin@localhost:5432/polymarket_analytics"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class MarketIndexDB(Base):
    __tablename__ = "market_index"
    id = Column(String, primary_key=True)
    title = Column(String, index=True)
    category = Column(String)

# Crear la tabla si no existe
def init_db():
    Base.metadata.create_all(bind=engine)