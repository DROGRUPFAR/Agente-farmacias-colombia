import streamlit as st
import urllib.parse

# Configuración principal de Streamlit
st.set_page_config(
    page_title="Agente Comercial de Precios Farmacéuticos CO",
    page_icon="💊",
    layout="wide"
)

# Título y encabezado
st.title("💊 Agente Comercial de Precios Farmacéuticos")
st.caption("Evaluación y comparación de precios en tiempo real para droguerías en Colombia")

st.divider()

# Inputs principales
col1, col2 = st.columns([2, 1])

with col1:
    producto_input = st.text_input("📦 Nombre del producto o medicamento:", value="Amlodipino 5 mg")

with col2:
    ciudad_input = st.selectbox(
        "📍 Ciudad de consulta / despacho:",
        ["Bogotá", "Medellín", "Cali", "Barranquilla", "Bucaramanga", "Fusagasugá", "Pereira", "Manizales", "Cúcuta", "Ibagué"]
    )

st.subheader("🎯 Selección de Cadenas de Farmacias y Marketplaces")

cadenas = st.multiselect(
    "Selecciona los comercios a consultar:",
    options=[
        "Farmaexpress (Coopidrogas)",
        "Mercado Libre Colombia",
        "Farmatodo Colombia",
        "Cruz Verde Colombia",
        "Droguerías La Rebaja",
        "Droguerías Cafam"
    ],
    default=[
        "Farmaexpress (Coopidrogas)",
        "Mercado Libre Colombia",
        "Farmatodo Colombia",
        "Cruz Verde Colombia"
    ]
)

st.divider()

if st.button("🔍 Evaluar y Comparar Precios", type="primary", use_container_width=True):
    if not producto_input.strip():
        st.warning("Por favor ingresa un nombre de producto o medicamento.")
    else:
        prod = producto_input.strip()
        prod_encoded = urllib.parse.quote(prod)
        
        st.subheader(f"📊 Evaluador Comercial para '{prod}' en {ciudad_input}")
        st.info(f"💡 Para consultar precios exactos en **{ciudad_input}**, haz clic en el botón de cada comercio para abrir el catálogo en vivo con tu ubicación asignada.")

        cols = st.columns(min(len(cadenas), 3) if cadenas else 1)

        for idx, comercio in enumerate(cadenas):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.write(f"### {comercio}")
                    st.caption(f"📍 Cobertura asignada: **{ciudad_input}**")

                    if comercio == "Farmaexpress (Coopidrogas)":
                        link = f"https://www.farmaexpress.com/home/icom?map=ft%2Cft&ft={prod_encoded}"
                        st.markdown(f"**Buscar:** `{prod}`")
                        st.link_button("🟢 Consultar en Farmaexpress", link, use_container_width=True)

                    elif comercio == "Mercado Libre Colombia":
                        link = f"https://listado.mercadolibre.com.co/{urllib.parse.quote(prod.replace(' ', '-'))}"
                        st.markdown(f"**Buscar:** `{prod}`")
                        st.link_button("🛒 Consultar en Mercado Libre", link, use_container_width=True)

                    elif comercio == "Farmatodo Colombia":
                        link = f"https://www.farmatodo.com.co/buscar?product={prod_encoded}"
                        st.markdown(f"**Buscar:** `{prod}`")
                        st.link_button("💊 Consultar en Farmatodo", link, use_container_width=True)

                    elif comercio == "Cruz Verde Colombia":
                        link = f"https://www.cruzverde.com.co/search?query={prod_encoded}"
                        st.markdown(f"**Buscar:** `{prod}`")
                        st.link_button("🟢 Consultar en Cruz Verde", link, use_container_width=True)

                    elif comercio == "Droguerías La Rebaja":
                        link = f"https://www.domicilioslarebaja.com/buscar?controller=search&s={prod_encoded}"
                        st.markdown(f"**Buscar:** `{prod}`")
                        st.link_button("🔴 Consultar en La Rebaja", link, use_container_width=True)

                    elif comercio == "Droguerías Cafam":
                        link = f"https://www.drogueriascafam.com.co/buscar?controller=search&s={prod_encoded}"
                        st.markdown(f"**Buscar:** `{prod}`")
                        st.link_button("🔵 Consultar en Cafam", link, use_container_width=True)

st.divider()
st.caption("Agente Comercial de Precios Farmacéuticos | Droguería y Minimarket Grupo Farma D.C.")
