import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Agregar el directorio raíz al path para que Python encuentre 'src'
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.infrastructure.api_client import PolymarketAPIClient
from src.application.fetch_markets_use_case import FetchActiveMarketsUseCase

# Inicializar dependencias (Inyección de dependencias manual)
api_client = PolymarketAPIClient()
fetch_markets_uc = FetchActiveMarketsUseCase(api_client)

# Configuración de la página
st.set_page_config(page_title="Polymarket Analytics", page_icon="📈", layout="wide")
st.title("Polymarket Analytics Dashboard 📈")
st.markdown("Visualización en tiempo real de los mercados activos.")

# Controles de usuario
limit = st.slider("Cantidad de mercados a consultar", min_value=5, max_value=100, value=20, step=5)

if st.button("Obtener Datos en Tiempo Real", type="primary"):
    with st.spinner("Consultando Polymarket..."):
        try:
            # Ejecutar el caso de uso
            markets = fetch_markets_uc.execute(limit=limit)

            if not markets:
                st.warning("No se obtuvieron datos de la API.")
            else:
                # Convertir los modelos Pydantic a diccionarios y luego a DataFrame (Pandas)
                df = pd.DataFrame([m.model_dump() for m in markets])

                # Seleccionar y renombrar columnas para la UI
                df_ui = df[['title', 'category', 'probability_yes', 'volume']]
                df_ui.columns = ['Título del Mercado', 'Categoría', 'Prob. Sí (%)', 'Volumen ($)']

                # Renderizar tabla interactiva con formato
                st.dataframe(
                    df_ui,
                    column_config={
                        "Prob. Sí (%)": st.column_config.ProgressColumn(
                            "Probabilidad 'Sí'",
                            help="Porcentaje de probabilidad del evento",
                            format="%.2f%%",
                            min_value=0,
                            max_value=100,
                        ),
                        "Volumen ($)": st.column_config.NumberColumn(
                            "Volumen",
                            format="$ %.2f"
                        )
                    },
                    hide_index=True,
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"Ocurrió un error al consultar la API: {e}")