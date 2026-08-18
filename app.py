import streamlit as st
import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import json
import re
import unicodedata
from urllib.parse import urljoin

# Configuración de la página
st.set_page_config(
    page_title="WebScraper de Noticias Inteligente",
    page_icon="📰",
    layout="wide"
)

# Título y descripción
st.title("📰 WebScraper de Noticias Dinámico")
st.markdown("Busca palabras clave en tus sitios de noticias favoritos en tiempo real usando **Playwright**.")

# Inicializar estado para guardar la configuración de forma persistente en la sesión
if "sitios" not in st.session_state:
    st.session_state["sitios"] = ["https://www.emol.com/", "https://www.biobiochile.cl/", "https://www.24horas.cl/"]
if "palabras" not in st.session_state:
    st.session_state["palabras"] = ["Trump", "Terremoto", "Colombia", "Ormuz"]

# --- SECCIÓN DE CONFIGURACIÓN ---
st.sidebar.header("🛠️ Configuración de Búsqueda")

st.sidebar.subheader("Sitios de Noticias")
sitios_input = st.sidebar.text_area(
    "Ingresa las URLs (una por línea):",
    value="\n".join(st.session_state["sitios"]),
    height=100
)

st.sidebar.subheader("Palabras Clave")
palabras_input = st.sidebar.text_area(
    "Ingresa SOLO palabras clave (una por línea):",
    value="\n".join(st.session_state["palabras"]),
    height=120
)

if sitios_input:
    st.session_state["sitios"] = [s.strip() for s in sitios_input.split("\n") if s.strip()]
if palabras_input:
    st.session_state["palabras"] = [p.strip() for p in palabras_input.split("\n") if p.strip()]

config_actual = {
    "sitios": st.session_state["sitios"],
    "palabras": st.session_state["palabras"]
}
config_json = json.dumps(config_actual, indent=4, ensure_ascii=False)
st.sidebar.download_button(
    label="💾 Exportar Configuración (JSON)",
    data=config_json,
    file_name="config_scraper.json",
    mime="application/json"
)

# --- FUNCIÓN AUXILIAR PARA REMOVER TILDES ---
def remover_tildes(texto):
    """Transforma caracteres con acento a su versión plana (ej: 'Shanghái' -> 'Shanghai')"""
    texto_normalizado = unicodedata.normalize('NFD', texto)
    return "".join(c for c in texto_normalizado if unicodedata.category(c) != 'Mn')

# --- FUNCIÓN DE SCRAPING ASÍNCRONA ---
async def escanear_sitio(url, palabras_clave, status_placeholder):
    resultados = []
    enlaces_procesados = set()
    status_placeholder.info(f"🌐 Conectando a {url}...")
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu"
                ]
            )
            page = await browser.new_page()
            
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            status_placeholder.info(f"🔍 Analizando contenido de {url}...")
            
            enlaces = await page.locator("a").all()
            total_encontrados_sitio = 0
            
            for enlace in enlaces:
                texto_original = await enlace.inner_text()
                
                # 1. Limpiar saltos de línea y espacios múltiples (mantiene nombres compuestos unidos)
                texto_limpio = re.sub(r'\s+', ' ', texto_original).strip()
                
                if len(texto_limpio) < 10:
                    continue
                    
                href = await enlace.get_attribute("href")
                
                if href:
                    if href.startswith("/"):
                        href = urljoin(url, href)
                    elif not href.startswith("http"):
                        continue 
                    
                    if href in enlaces_procesados:
                        continue

                    # 2. 🚀 Normalizar el titular removiendo tildes y pasando a minúsculas
                    texto_comparar = remover_tildes(texto_limpio).lower()

                    for palabra in palabras_clave:
                        palabra_limpia = palabra.strip()
                        if not palabra_limpia:
                            continue
                        
                        # 3. 🚀 Normalizar la palabra de búsqueda de la misma forma
                        palabra_comparar = remover_tildes(palabra_limpia).lower()
                        
                        # Evaluación directa insensible a acentos y mayúsculas
                        if palabra_comparar in texto_comparar:
                            resultados.append({
                                "Sitio": url,
                                "Titular": texto_limpio,  # Se muestra el titular original bonito en la interfaz
                                "Palabra Coincidente": palabra_limpia,
                                "Enlace": href
                            })
                            enlaces_procesados.add(href)
                            total_encontrados_sitio += 1
                            break 
                            
            await browser.close()
            status_placeholder.success(f"✅ {url} finalizado. ¡Se encontraron {total_encontrados_sitio} coincidencias únicas!")
            return resultados

    except Exception as e:
        status_placeholder.error(f"❌ Error al escanear {url}: {str(e)}")
        return []

# --- PANEL PRINCIPAL Y BOTÓN DE INICIO ---
st.subheader("🚀 Control de Extracción")

col1, col2 = st.columns(2)

with col1:
    iniciar_busqueda = st.button("▶️ Iniciar Búsqueda", use_container_width=True, type="primary")

with col2:
    with st.expander("👁️ Ver parámetros actuales de búsqueda", expanded=False):
        st.write("**Sitios:**", st.session_state["sitios"])
        st.write("**Palabras clave:**", st.session_state["palabras"])

if iniciar_busqueda:
    if not st.session_state["sitios"] or not st.session_state["palabras"]:
        st.error("Por favor, ingresa al menos un sitio web y una palabra clave.")
    else:
        todos_los_resultados = []
        st.markdown("### ⏳ Estado del Proceso")
        progreso_bar = st.progress(0)
        total_sitios = len(st.session_state["sitios"])
        
        for idx, sitio in enumerate(st.session_state["sitios"]):
            status_box = st.empty()
            res = asyncio.run(escanear_sitio(sitio, st.session_state["palabras"], status_box))
            todos_los_resultados.extend(res)
            progreso_bar.progress((idx + 1) / total_sitios)
        
        st.markdown("---")
        st.subheader("📊 Resultados de la Búsqueda")
        
        if todos_los_resultados:
            df = pd.DataFrame(todos_los_resultados)
            st.metric("Total de noticias encontradas", len(df))
            
            for sitio_agrupado, group_df in df.groupby("Sitio"):
                with st.expander(f"📌 {sitio_agrupado} ({len(group_df)} resultados)", expanded=True):
                    for _, row in group_df.iterrows():
                        st.markdown(f"- **[{row['Titular']}]({row['Enlace']})** — *(Filtro: {row['Palabra Coincidente']} )*")
                        
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Resultados (CSV)",
                data=csv_data,
                file_name="noticias_encontradas.csv",
                mime="text/csv"
            )
        else:
            st.warning("No se encontraron noticias que coincidan con los criterios establecidos.")