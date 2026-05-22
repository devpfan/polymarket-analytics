import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Agregar el directorio raíz al path para que Python encuentre 'src'
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.infrastructure.api_client import PolymarketAPIClient
from src.application.fetch_markets_use_case import FetchActiveMarketsUseCase

# Inicializar dependencias
api_client = PolymarketAPIClient()
fetch_markets_uc = FetchActiveMarketsUseCase(api_client)

st.set_page_config(page_title="Polymarket Analytics", page_icon="📈", layout="wide")
st.title("Polymarket Analytics Dashboard 📈")
st.markdown("Explora y busca mercados activos en tiempo real.")

# Controles de usuario en columnas
col1, col2 = st.columns([1, 3])
with col1:
    limit = st.slider("Mercados a extraer", min_value=10, max_value=200, value=50, step=10)
with col2:
    search_term = st.text_input("🔍 Buscar mercado por palabra clave:", placeholder="Ej: Trump, Bitcoin, Champions...")

if st.button("Actualizar Datos", type="primary"):
    # Guardamos los datos en el session_state para no perderlos al interactuar con la tabla
    with st.spinner("Consultando Polymarket..."):
        try:
            st.session_state['markets'] = fetch_markets_uc.execute(limit=limit)
        except Exception as e:
            st.error(f"Ocurrió un error al consultar la API: {e}")

# Verificamos si hay datos guardados en la sesión
if 'markets' in st.session_state and st.session_state['markets']:
    markets = st.session_state['markets']

    # Convertir a DataFrame
    df = pd.DataFrame([m.model_dump() for m in markets])

    # Preparamos los datos para la tabla
    df_ui = df[['id', 'title', 'category', 'probability_yes', 'volume']].copy()
    df_ui.columns = ['ID', 'Título del Mercado', 'Categoría', 'Prob. Sí (%)', 'Volumen ($)']

    # 1. Lógica del Buscador
    if search_term:
        # Filtramos ignorando mayúsculas/minúsculas
        df_filtered = df_ui[df_ui['Título del Mercado'].str.contains(search_term, case=False, na=False)]
    else:
        df_filtered = df_ui

    st.subheader(f"Resultados ({len(df_filtered)})")

    # 2. Tabla Interactiva (Ocultamos el ID en la UI, pero lo mantenemos para la lógica)
    event = st.dataframe(
        df_filtered,
        column_config={
            "ID": None,  # Ocultamos la columna ID visualmente
            "Prob. Sí (%)": st.column_config.ProgressColumn(
                "Probabilidad 'Sí'",
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
        use_container_width=True,
        on_select="rerun",  # Vuelve a ejecutar el script al seleccionar
        selection_mode="single-row"  # Permite seleccionar solo una fila
    )

    # 3. Lógica de Detalles al Seleccionar
    selected_rows = event.selection.rows
    if selected_rows:
        # Obtenemos el índice de la fila seleccionada en el dataframe filtrado
        selected_idx = selected_rows[0]
        selected_market_data = df_filtered.iloc[selected_idx]

        st.divider()
        st.subheader("🔍 Detalles del Mercado Seleccionado")

        # Tarjeta de métricas
        m1, m2, m3 = st.columns(3)
        m1.metric(label="Mercado", value=selected_market_data['Categoría'])
        m2.metric(label="Volumen Total", value=f"${selected_market_data['Volumen ($)']:,.2f}")
        m3.metric(label="Probabilidad (Sí)", value=f"{selected_market_data['Prob. Sí (%)']:.2f}%")

        st.info(f"**Pregunta completa:** {selected_market_data['Título del Mercado']}")

        # Como iteramos sobre el dict de Pydantic original para obtener los datos extra:
        # Buscamos el mercado original en la lista usando el ID
        original_market = next((m for m in markets if m.id == selected_market_data['ID']), None)

        if original_market:
            with st.expander("Ver Reglas y Detalles del Mercado", expanded=True):
                st.markdown(f"**Descripción / Reglas:**\n{original_market.description}")
                st.markdown(f"**Fecha de Cierre:** `{original_market.end_date}`")
                st.markdown(
                    f"**Fuente de Resolución:** [{original_market.resolution_source}]({original_market.resolution_source})")

        st.caption(f"ID interno: {selected_market_data['ID']}")