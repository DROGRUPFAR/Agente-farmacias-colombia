import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse

# Configuración de la página
st.set_page_config(
    page_title="Evaluador de Precios Farmacéuticos CO",
    page_icon="💊",
    layout="wide"
)

class AgenteFarmaciasColombia:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept-Language": "es-ES,es;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }

    def buscar_farmaexpress_directo(self, producto: str) -> list:
        """Busca directamente en la web de Farmaexpress."""
        url_busqueda = f"https://www.farmaexpress.com/?s={urllib.parse.quote(producto)}&post_type=product"
        resultados = []
        try:
            res = requests.get(url_busqueda, headers=self.headers, timeout=8)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                # Se buscan los elementos de productos en el catálogo
                productos = soup.find_all("li", class_="product") or soup.find_all("div", class_="product-small")
                
                for item in productos[:6]:
                    titulo_elem = item.find("h2") or item.find("p", class_="name") or item.find("a")
                    precio_elem = item.find("span", class_="woocommerce-Price-amount") or item.find("span", class_="price")
                    link_elem = item.find("a", href=True)
                    
                    titulo = titulo_elem.text.strip() if titulo_elem else "Producto Farmaexpress"
                    precio = precio_elem.text.strip() if precio_elem else "Precio en web"
                    link = link_elem["href"] if link_elem else url_busqueda

                    resultados.append({
                        "comercio": "Farmaexpress",
                        "producto": titulo,
                        "precio": precio,
                        "enlace": link
                    })
        except Exception as e:
            st.error(f"Error consultando Farmaexpress: {e}")
        return resultados

    def buscar_mercadolibre_directo(self, producto: str) -> list:
        """Busca directamente en el catálogo de Mercado Libre Colombia."""
        query = f"{producto} farmacia".strip()
        url = f"https://listado.mercadolibre.com.co/{urllib.parse.quote(query)}"
        resultados = []
        try:
            res = requests.get(url, headers=self.headers, timeout=8)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                items = soup.find_all("li", class_="ui-search-layout__item")[:6]
                
                for item in items:
                    titulo_elem = item.find("h2")
                    precio_elem = item.find("span", class_="andes-money-amount__fraction")
                    link_elem = item.find("a", class_="ui-search-link")
                    
                    if titulo_elem and precio_elem:
                        resultados.append({
                            "comercio": "Mercado Libre",
                            "producto": titulo_elem.text.strip(),
                            "precio": f"${precio_elem.text.strip()} COP",
                            "enlace": link_elem["href"] if link_elem else url
                        })
        except Exception:
            pass
        return resultados

    def buscar_farmatodo_directo(self, producto: str) -> list:
        """Busca en el catálogo público de Farmatodo Colombia."""
        url = f"https://www.farmatodo.com.co/buscar?product={urllib.parse.quote(producto)}"
        resultados = []
        try:
            res = requests.get(url, headers=self.headers, timeout=8)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                items = soup.find_all("div", class_="product-card") or soup.find_all("article")
                for item in items[:4]:
                    titulo = item.find("span", class_="text-title") or item.find("h3")
                    precio = item.find("span", class_="text-price")
                    link = item.find("a", href=True)
                    if titulo:
                        resultados.append({
                            "comercio": "Farmatodo",
                            "producto": titulo.text.strip(),
                            "precio": precio.text.strip() if precio else "Consultar en sitio",
                            "enlace": f"https://www.farmatodo.com.co{link['href']}" if link and link['href'].startswith('/') else url
                        })
        except Exception:
            pass
        return resultados


# INTERFAZ GRÁFICA EN STREAMLIT
st.title("💊 Agente Comercial de Precios Farmacéuticos")
st.caption("Consulta directa de catálogos e inventarios web en Colombia")

st.divider()

col1, col2 = st.columns([2, 1])

with col1:
    producto_input = st.text_input("📦 Nombre del producto o medicamento:", placeholder="Ej. Amlodipino, Dolex, Losartán, etc.")

with col2:
    ciudad_input = st.selectbox(
        "📍 Ciudad de consulta / despacho:",
        ["Bogotá", "Medellín", "Cali", "Barranquilla", "Bucaramanga", "Fusagasugá", "Pereira", "Manizales", "Otras"]
    )

st.subheader("🎯 Opciones de Filtrado por Comercios")

incluir_farmaexpress = st.checkbox("Incluir Farmaexpress (farmaexpress.com)", value=True)
incluir_mercadolibre = st.checkbox("Incluir Mercado Libre Colombia", value=True)
incluir_farmatodo = st.checkbox("Incluir Farmatodo Colombia", value=True)

st.divider()

if st.button("🔍 Evaluar y Comparar Precios", type="primary", use_container_width=True):
    if not producto_input.strip():
        st.warning("Por favor ingresa el nombre de un producto para iniciar la evaluación.")
    else:
        agente = AgenteFarmaciasColombia()
        st.subheader(f"📊 Resultados para **'{producto_input}'** en {ciudad_input}")

        # 1. FARMAEXPRESS
        if incluir_farmaexpress:
            st.markdown("### 🟢 Farmaexpress")
            with st.spinner("Consultando Farmaexpress..."):
                fx_res = agente.buscar_farmaexpress_directo(producto_input)
                if fx_res:
                    cols = st.columns(min(len(fx_res), 3))
                    for idx, item in enumerate(fx_res):
                        with cols[idx % 3]:
                            with st.container(border=True):
                                st.write(f"**{item['producto']}**")
                                st.subheader(item['precio'])
                                st.link_button("🔗 Ir al producto", item['enlace'])
                else:
                    st.info("No se encontraron resultados directos o la página no devolvió coincidencias para esta búsqueda.")

        # 2. MERCADO LIBRE
        if incluir_mercadolibre:
            st.markdown("### 🛒 Mercado Libre Colombia")
            with st.spinner("Consultando Mercado Libre..."):
                ml_res = agente.buscar_mercadolibre_directo(producto_input)
                if ml_res:
                    cols_ml = st.columns(min(len(ml_res), 3))
                    for idx, item in enumerate(ml_res):
                        with cols_ml[idx % 3]:
                            with st.container(border=True):
                                st.write(f"**{item['producto']}**")
                                st.subheader(item['precio'])
                                st.link_button("🔗 Ver oferta", item['enlace'])
                else:
                    st.info("No se encontraron ofertas activas para esa búsqueda.")

        # 3. FARMATODO
        if incluir_farmatodo:
            st.markdown("### 💊 Farmatodo")
            with st.spinner("Consultando Farmatodo..."):
                ft_res = agente.buscar_farmatodo_directo(producto_input)
                if ft_res:
                    cols_ft = st.columns(min(len(ft_res), 3))
                    for idx, item in enumerate(ft_res):
                        with cols_ft[idx % 3]:
                            with st.container(border=True):
                                st.write(f"**{item['producto']}**")
                                st.subheader(item['precio'])
                                st.link_button("🔗 Ver en Farmatodo", item['enlace'])
                else:
                    st.info("Sin coincidencias directas en el portal de Farmatodo.")

st.divider()
st.caption("Agente Comercial de Precios Farmacéuticos | Colombia")
