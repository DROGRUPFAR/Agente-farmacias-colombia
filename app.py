import streamlit as st
import requests
import urllib.parse

# Configuración de la ventana
st.set_page_config(
    page_title="Agente de Precios Farmacéuticos CO",
    page_icon="💊",
    layout="wide"
)

class AgenteFarmaciasColombia:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*"
        }

    def buscar_farmaexpress(self, producto: str) -> list:
        """Consulta la API pública interna de VTEX de Farmaexpress (Precios Reales)."""
        producto_encoded = urllib.parse.quote(producto.strip())
        # Endpoints oficiales de catálogo e Intelligent Search de VTEX para Farmaexpress
        urls_api = [
            f"https://www.farmaexpress.com/api/catalog_system/pub/products/search/{producto_encoded}",
            f"https://www.farmaexpress.com/api/io/_v/api/intelligent-search/product_search/{producto_encoded}"
        ]
        
        resultados = []
        for url in urls_api:
            try:
                res = requests.get(url, headers=self.headers, timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    # Manejo de API Legacy
                    if isinstance(data, list) and len(data) > 0:
                        for prod in data[:6]:
                            nombre = prod.get("productName", "Producto sin nombre")
                            link = prod.get("link", "https://www.farmaexpress.com")
                            
                            # Extraer precio de la primera variación (SKU)
                            precio = "No disponible"
                            items = prod.get("items", [])
                            if items and len(items) > 0:
                                sellers = items[0].get("sellers", [])
                                if sellers and len(sellers) > 0:
                                    offer = sellers[0].get("commertialOffer", {})
                                    price_val = offer.get("Price") or offer.get("ListPrice")
                                    if price_val:
                                        precio = f"${price_val:,.0f} COP".replace(",", ".")
                            
                            resultados.append({
                                "comercio": "Farmaexpress",
                                "producto": nombre,
                                "precio": precio,
                                "enlace": link
                            })
                        break
                    # Manejo de API Intelligent Search
                    elif isinstance(data, dict) and "products" in data:
                        prods = data.get("products", [])
                        for prod in prods[:6]:
                            nombre = prod.get("productName", "Producto sin nombre")
                            link = f"https://www.farmaexpress.com/{prod.get('linkText', '')}/p"
                            precio = "No disponible"
                            items = prod.get("items", [])
                            if items:
                                sellers = items[0].get("sellers", [])
                                if sellers:
                                    price_val = sellers[0].get("commertialOffer", {}).get("Price")
                                    if price_val:
                                        precio = f"${price_val:,.0f} COP".replace(",", ".")
                            
                            resultados.append({
                                "comercio": "Farmaexpress",
                                "producto": nombre,
                                "precio": precio,
                                "enlace": link
                            })
                        break
            except Exception:
                continue
        return resultados

    def buscar_mercadolibre(self, producto: str) -> list:
        """Consulta la API Oficial Pública de Mercado Libre Colombia (MCO)."""
        url = f"https://api.mercadolibre.com/sites/MCO/search?q={urllib.parse.quote(producto)}&category=MCO1071" # Categoría Salud/Farmacia
        url_fallback = f"https://api.mercadolibre.com/sites/MCO/search?q={urllib.parse.quote(producto)}"
        
        resultados = []
        for api_url in [url, url_fallback]:
            try:
                res = requests.get(api_url, headers=self.headers, timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    results = data.get("results", [])
                    if results:
                        for item in results[:6]:
                            precio_val = item.get("price")
                            precio_fmt = f"${precio_val:,.0f} COP".replace(",", ".") if precio_val else "Consultar"
                            resultados.append({
                                "comercio": "Mercado Libre",
                                "producto": item.get("title", "Producto"),
                                "precio": precio_fmt,
                                "enlace": item.get("permalink", "https://www.mercadolibre.com.co")
                            })
                        break
            except Exception:
                continue
        return resultados


# INTERFAZ GRÁFICA EN STREAMLIT
st.title("💊 Agente Comercial de Precios Farmacéuticos")
st.caption("Consulta directa de precios y disponibilidad mediante conectores de API en Colombia")

st.divider()

col1, col2 = st.columns([2, 1])

with col1:
    producto_input = st.text_input("📦 Nombre del producto o medicamento:", value="Amlodipino 5 mg")

with col2:
    ciudad_input = st.selectbox(
        "📍 Ciudad de consulta:",
        ["Bogotá", "Medellín", "Cali", "Barranquilla", "Bucaramanga", "Fusagasugá", "Otras"]
    )

st.subheader("🎯 Opciones de Filtrado")

col_chk1, col_chk2 = st.columns(2)
with col_chk1:
    incluir_farmaexpress = st.checkbox("Incluir Farmaexpress (farmaexpress.com)", value=True)
with col_chk2:
    incluir_mercadolibre = st.checkbox("Incluir Mercado Libre Colombia", value=True)

st.divider()

if st.button("🔍 Evaluar y Comparar Precios", type="primary", use_container_width=True):
    if not producto_input.strip():
        st.warning("Por favor ingresa un producto para consultar.")
    else:
        agente = AgenteFarmaciasColombia()
        st.markdown(f"### 📊 Resultados para **'{producto_input}'** (Cobertura: {ciudad_input})")
        st.write("")

        # 1. FARMAEXPRESS
        if incluir_farmaexpress:
            st.markdown("#### 🟢 Farmaexpress (Coopidrogas / Droguerías Aliadas)")
            with st.spinner("Consultando inventario en Farmaexpress..."):
                fx_res = agente.buscar_farmaexpress(producto_input)
                if fx_res:
                    cols = st.columns(min(len(fx_res), 3))
                    for idx, item in enumerate(fx_res):
                        with cols[idx % 3]:
                            with st.container(border=True):
                                st.write(f"**{item['producto']}**")
                                st.subheader(item['precio'])
                                st.link_button("🔗 Ver en Farmaexpress", item['enlace'])
                else:
                    st.info("No se encontraron coincidencias exactas en el catálogo de Farmaexpress para esa búsqueda. Intenta con un nombre de marca o molécula diferente (ej: Amlodipino 5mg).")

        # 2. MERCADO LIBRE
        if incluir_mercadolibre:
            st.markdown("#### 🛒 Mercado Libre Colombia")
            with st.spinner("Consultando Mercado Libre..."):
                ml_res = agente.buscar_mercadolibre(producto_input)
                if ml_res:
                    cols_ml = st.columns(min(len(ml_res), 3))
                    for idx, item in enumerate(ml_res):
                        with cols_ml[idx % 3]:
                            with st.container(border=True):
                                st.write(f"**{item['producto']}**")
                                st.subheader(item['precio'])
                                st.link_button("🔗 Ver Oferta", item['enlace'])
                else:
                    st.info("No se encontraron publicaciones activas en Mercado Libre para este producto.")

st.divider()
st.caption("Agente Comercial de Precios Farmacéuticos | Colombia - Consultas API")
