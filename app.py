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
        """Consulta la API de Farmaexpress con filtro estricto por coincidencia."""
        palabra_clave = producto.strip().lower().split()[0] # Primera palabra para validar relevancia
        producto_encoded = urllib.parse.quote(producto.strip())
        
        url_api = f"https://www.farmaexpress.com/api/catalog_system/pub/products/search/{producto_encoded}"
        resultados = []
        
        try:
            res = requests.get(url_api, headers=self.headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list):
                    for prod in data:
                        nombre = prod.get("productName", "")
                        # Validar que el nombre del producto contenga la palabra clave buscada
                        if palabra_clave in nombre.lower():
                            link = prod.get("link", "https://www.farmaexpress.com")
                            precio = "No disponible"
                            items = prod.get("items", [])
                            if items:
                                sellers = items[0].get("sellers", [])
                                if sellers:
                                    offer = sellers[0].get("commertialOffer", {})
                                    price_val = offer.get("Price") or offer.get("ListPrice")
                                    if price_val and price_val > 0:
                                        precio = f"${price_val:,.0f} COP".replace(",", ".")
                            
                            resultados.append({
                                "comercio": "Farmaexpress",
                                "producto": nombre,
                                "precio": precio,
                                "enlace": link
                            })
                            if len(resultados) >= 6:
                                break
        except Exception:
            pass
        return resultados

    def buscar_mercadolibre(self, producto: str) -> list:
        """Consulta la API Oficial de Mercado Libre Colombia."""
        url = f"https://api.mercadolibre.com/sites/MCO/search?q={urllib.parse.quote(producto)}"
        resultados = []
        try:
            res = requests.get(url, headers=self.headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                results = data.get("results", [])
                for item in results[:6]:
                    precio_val = item.get("price")
                    precio_fmt = f"${precio_val:,.0f} COP".replace(",", ".") if precio_val else "Consultar"
                    resultados.append({
                        "comercio": "Mercado Libre",
                        "producto": item.get("title", "Producto"),
                        "precio": precio_fmt,
                        "enlace": item.get("permalink", "https://www.mercadolibre.com.co")
                    })
        except Exception:
            pass
        return resultados

    def buscar_otras_farmacias(self, producto: str, ciudad: str, dominio: str) -> list:
        """Genera un acceso directo de búsqueda específica para la cadena seleccionada."""
        query_encoded = urllib.parse.quote(f"{producto} {ciudad}")
        url_directa = f"https://www.google.com/search?q=site:{dominio}+{query_encoded}"
        return {
            "cadena": dominio,
            "enlace_busqueda": url_directa
        }


# INTERFAZ GRÁFICA EN STREAMLIT
st.title("💊 Agente Comercial de Precios Farmacéuticos")
st.caption("Consulta directa de precios y disponibilidad para droguerías en Colombia")

st.divider()

col1, col2 = st.columns([2, 1])

with col1:
    producto_input = st.text_input("📦 Nombre del producto o medicamento:", placeholder="Ej. Amlodipino, Dolex 500mg, Losartán, etc.")

with col2:
    ciudad_input = st.selectbox(
        "📍 Ciudad de consulta / despacho:",
        ["Bogotá", "Medellín", "Cali", "Barranquilla", "Bucaramanga", "Fusagasugá", "Pereira", "Manizales", "Otras"]
    )

st.subheader("🎯 Opciones de Filtrado por Comercios")

col_f1, col_f2 = st.columns(2)
with col_f1:
    incluir_farmaexpress = st.checkbox("Incluir Farmaexpress (farmaexpress.com)", value=True)
with col_f2:
    incluir_mercadolibre = st.checkbox("Incluir Mercado Libre Colombia", value=True)

cadenas_seleccionadas = st.multiselect(
    "Selecciona otras cadenas de farmacias a comparar:",
    options=[
        "farmatodo.com.co",
        "cruzverde.com.co",
        "domicilioslarebaja.com",
        "drogueriascafam.com.co"
    ],
    default=["farmatodo.com.co", "cruzverde.com.co"]
)

st.divider()

if st.button("🔍 Evaluar y Comparar Precios", type="primary", use_container_width=True):
    if not producto_input.strip():
        st.warning("Por favor ingresa un producto para consultar.")
    else:
        agente = AgenteFarmaciasColombia()
        st.markdown(f"### 📊 Resultados para **'{producto_input}'** (Ciudad: {ciudad_input})")
        st.write("")

        # 1. FARMAEXPRESS
        if incluir_farmaexpress:
            st.markdown("#### 🟢 Farmaexpress")
            with st.spinner("Consultando Farmaexpress..."):
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
                    st.info(f"No se encontraron coincidencia exactas para '{producto_input}' en Farmaexpress.")

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
                    st.info("No se encontraron publicaciones activas en Mercado Libre.")

        # 3. OTRAS CADENAS SELECCIONADAS
        if cadenas_seleccionadas:
            st.markdown("#### 💊 Otras Cadenas de Farmacias Seleccionadas")
            cols_cadenas = st.columns(len(cadenas_seleccionadas))
            for idx, dominio in enumerate(cadenas_seleccionadas):
                info = agente.buscar_Buscar_otras_farmacias = agente.buscar_otras_farmacias(producto_input, ciudad_input, dominio)
                with cols_cadenas[idx]:
                    with st.container(border=True):
                        st.write(f"**{dominio}**")
                        st.caption(f"Consulta directa en {ciudad_input}")
                        st.link_button(f"🔎 Buscar en {dominio}", info["enlace_busqueda"])

st.divider()
st.caption("Agente Comercial de Precios Farmacéuticos | Colombia")
