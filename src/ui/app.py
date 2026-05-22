import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Configurar path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.infrastructure.api_client import PolymarketAPIClient
from src.application.sync_index_use_case import SyncIndexUseCase
from src.infrastructure.database import init_db, SessionLocal, MarketIndexDB

# Inicializar Base de Datos (Crea la tabla si no existe)
init_db()

# Inicializar dependencias
api_client = PolymarketAPIClient()
sync_index_uc = SyncIndexUseCase(api_client)

st.set_page_config(page_title="Polymarket Analytics", page_icon="📈", layout="wide")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Mantenimiento de Datos")
    st.info("Sincroniza el índice local para buscar en todo el catálogo de Polymarket.")
    if st.button("Sincronizar Índice Global", type="primary"):
        with st.spinner("Descargando catálogo e indexando en PostgreSQL..."):
            try:
                sync_index_uc.execute()
                st.success("¡Índice actualizado correctamente!")
            except Exception as e:
                st.error(f"Error en sincronización: {e}")

# --- PANTALLA PRINCIPAL ---
st.title("Polymarket Analytics Dashboard 📈")
st.markdown("Busca cualquier mercado en tu índice local (PostgreSQL).")

search_term = st.text_input("🔍 Buscar mercado por palabra clave:", placeholder="Ej: Trump, Bitcoin, Champions...")

if search_term:
    db = SessionLocal()
    try:
        # Búsqueda usando ILIKE para ignorar mayúsculas/minúsculas en Postgres
        resultados_db = db.query(MarketIndexDB).filter(MarketIndexDB.title.ilike(f"%{search_term}%")).limit(20).all()

        if not resultados_db:
            st.warning("No se encontraron mercados en el índice local. ¿Ya sincronizaste la base de datos?")
        else:
            st.subheader(f"Resultados en BD ({len(resultados_db)})")

            # Preparar datos para la tabla visual
            df_ui = pd.DataFrame(
                [{"ID": r.id, "Título del Mercado": r.title, "Categoría": r.category} for r in resultados_db])

            event = st.dataframe(
                df_ui,
                column_config={"ID": None},  # Ocultar ID
                hide_index=True,
                use_container_width=True,
                on_select="rerun",
                selection_mode="single-row"
            )

            # Si el usuario hace clic en un resultado de la BD, traemos la data viva de la API
            selected_rows = event.selection.rows
            if selected_rows:
                selected_idx = selected_rows[0]
                market_id_to_fetch = df_ui.iloc[selected_idx]['ID']

                st.divider()
                with st.spinner("Obteniendo datos en tiempo real de Polymarket..."):
                    market_live_data = api_client.get_market_by_id(market_id_to_fetch)

                if market_live_data:
                    st.subheader("🔍 Estado Actual del Mercado")
                    m1, m2, m3 = st.columns(3)
                    m1.metric(label="Estado", value="Activo" if market_live_data.active else "Cerrado")
                    m2.metric(label="Volumen Total", value=f"${market_live_data.volume:,.2f}")
                    m3.metric(label="Probabilidad (Sí)", value=f"{market_live_data.probability_yes:.2f}%")

                    st.info(f"**Pregunta:** {market_live_data.title}")

                    with st.expander("Ver Reglas y Detalles del Mercado", expanded=True):
                        st.markdown(f"**Descripción:**\n{market_live_data.description}")
                        st.markdown(f"**Cierre:** `{market_live_data.end_date}`")
                        st.markdown(
                            f"**Fuente:** [{market_live_data.resolution_source}]({market_live_data.resolution_source})")
    finally:
        db.close()