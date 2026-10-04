import streamlit as st
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import urllib.parse

# Configuración de la página
st.set_page_config(
    page_title="Evaluador de Precios Farmacéuticos CO",
    page_icon="💊",
    layout="wide"
)

# Estilos visuales
st.markdown("""
<style>
    .main-header { font-size: 2.2rem; color: #0E2F44; font-weight: bold; }
    .sub-header { font-size: 1.1rem; color: #555; }
    .price-card { background-color: #f8f9fa; border-left: 4px solid #008080; padding: 12px; border-radius: 6px; margin-bottom: 10px; }
    .badge-city { background-color: #e1f5fe; color: #0288d1; padding: 3px 8px; border-radius: 12px; font-size: 0.85rem; font-weight: bold; }
</style>
""", unsafe_allow_headers=True)

class AgenteFarmaciasColombia:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def buscar_mercadolibre(self, producto: str, ciudad: str = "") -> list:
        """Busca productos en Mercado Libre Colombia."""
        query = f"{producto} farmacia {ciudad}".strip()
        url = f"https://listado.mercadolibre.com.co/{urllib.parse.quote(query)}"
        resultados = []
        try:
            res = requests.get(url, headers=self.headers, timeout=6)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                items = soup.find_all("li", class_="ui-search-layout__item")[:4]
                for item in items:
                    titulo = item.find("h2").text.strip() if item.find("h2") else "Producto sin título"
                    precio = item.find("span", class_="andes-money-amount__fraction").text.strip() if item.find("span", class_="andes-money-amount__fraction") else "N/A"
                    link_elem = item.find("a", class_="ui-search-link")
                    link = link_elem["href"] if link_elem else "#"
                    resultados.append({
                        "comercio": "Mercado Libre",
                        "producto": titulo,
                        "precio": f"${precio} COP",
                        "enlace": link
                    })
        except Exception:
            pass
        return resultados

    def buscar_farmaexpress(self, producto: str, ciudad: str = "") -> list:
        """Busca específicamente en Farmaexpress y sitios relacionados."""
        query = f"site:farmaexpress.com {producto} {ciudad} precio".strip()
        resultados = []
        try:
            with DDGS() as ddgs:
                search_results = list(ddgs.text(query, region="co-es", max_results=4))
                for r in search_results:
                    resultados.append({
                        "comercio": "Farmaexpress",
                        "titulo": r.get("title"),
                        "snippet": r.get("body"),
                        "enlace": r.get("href")
                    })
        except Exception:
            pass
        return resultados

    def buscar_otras_farmacias(self, producto: str, ciudad: str = "", farmacia_domain: str = "") -> list:
        """Busca en cadenas farmacéuticas específicas."""
        sitio_filter = f"site:{farmacia_domain}" if farmacia_domain else ""
        query = f"{producto} precio colombia {ciudad} {sitio_filter}".strip()
        
        resultados = []
        try:
            with DDGS() as ddgs:
                search_results = list(ddgs.text(query, region="co-es", max_results=4))
                for r in search_results:
                    resultados.append({
                        "comercio": farmacia_domain,
                        "titulo": r.get("title"),
                        "snippet": r.get("body"),
                        "enlace": r.get("href")
                    })
        except Exception:
            pass
        return resultados


# INTERFAZ GRÁFICA EN STREAMLIT
st.markdown('<p class="main-header">💊 Agente Comercial de Precios Farmacéuticos</p>', unsafe_allow_headers=True)
st.markdown('<p class="sub-header">Evaluación en tiempo real para droguerías y productos farmacéuticos en Colombia</p>', unsafe_allow_headers=True)

st.divider()

# Formulario de entrada
col1, col2 = st.columns([2, 1])

with col1:
    producto_input = st.text_input("📦 Nombre del producto o medicamento:", placeholder="Ej. Dolex 500mg, Gel limpiador Eucerin, etc.")

with col2:
    ciudad_input = st.selectbox(
        "📍 Ciudad de consulta / despacho:",
        ["Bogotá", "Medellín", "Cali", "Barranquilla", "Bucaramanga", "Fusagasugá", "Pereira", "Manizales", "Otras"]
    )

st.subheader("🎯 Opciones de Filtrado por Comercios")

incluir_farmaexpress = st.checkbox("Incluir Farmaexpress (farmaexpress.com)", value=True)
incluir_mercadolibre = st.checkbox("Incluir Mercado Libre Colombia", value=True)

cadenas_seleccionadas = st.multiselect(
    "Selecciona otras cadenas de farmacias a comparar:",
    options=[
        "farmatodo.com.co",
        "cruzverde.com.co",
        "domicilioslarebaja.com",
        "drogueriascafam.com.co",
        "droguerialarebaja.com"
    ],
    default=["farmatodo.com.co", "cruzverde.com.co"]
)

st.divider()

if st.button("🔍 Evaluar y Comparar Precios", type="primary", use_container_width=True):
    if not producto_input.strip():
        st.warning("Por favor ingresa el nombre de un producto para iniciar la evaluación.")
    else:
        agente = AgenteFarmaciasColombia()
        
        st.markdown(f"### 📊 Resultados de búsqueda para **'{producto_input}'** <span class='badge-city'>Ciudad: {ciudad_input}</span>", unsafe_allow_headers=True)
        st.write("")

        # 1. FARMAEXPRESS
        if incluir_farmaexpress:
            st.markdown("#### 🟢 Precios / Coincidencias en **Farmaexpress**")
            with st.spinner("Consultando Farmaexpress..."):
                fx_res = agente.buscar_farmaexpress(producto_input, ciudad_input)
                if fx_res:
                    for item in fx_res:
                        st.markdown(f"""
                        <div class="price-card">
                            <b>{item['titulo']}</b><br>
                            <small>{item['snippet']}</small><br>
                            <a href="{item['enlace']}" target="_blank">🔗 Ver enlace de compra en Farmaexpress</a>
                        </div>
                        """, unsafe_allow_headers=True)
                else:
                    st.info("No se encontraron coincidencias directas en Farmaexpress para esta búsqueda.")

        # 2. MERCADO LIBRE
        if incluir_mercadolibre:
            st.markdown("#### 🛒 Opciones en **Mercado Libre Colombia**")
            with st.spinner("Consultando Mercado Libre..."):
                ml_res = agente.buscar_mercadolibre(producto_input, ciudad_input)
                if ml_res:
                    cols_ml = st.columns(len(ml_res))
                    for idx, item in enumerate(ml_res):
                        with cols_ml[idx]:
                            st.metric(label=item['comercio'], value=item['precio'])
                            st.caption(item['producto'])
                            st.markdown(f"[Ver oferta]({item['enlace']})")
                else:
                    st.info("No se encontraron resultados relevantes en Mercado Libre.")

        # 3. CADENAS Y OTRAS FARMACIAS
        if cadenas_seleccionadas:
            st.markdown("#### 💊 Otras Cadenas de Farmacias Seleccionadas")
            with st.spinner("Consultando cadenas farmacéuticas..."):
                for cadena in cadenas_seleccionadas:
                    res_c = agente.buscar_otras_farmacias(producto_input, ciudad_input, cadena)
                    if res_c:
                        st.write(f"**Resultados para {cadena}:**")
                        for r in res_c[:2]:
                            st.markdown(f"- [{r['titulo']}]({r['enlace']}) - *{r['snippet'][:120]}...*")
                    else:
                        st.caption(f"Sin resultados recientes para {cadena}")

st.divider()
st.caption("Agente Comercial de Precios Farmacéuticos | Colombia - Consultas dinámicas sin costo de API")