import streamlit as st
import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import json
import re
from urllib.parse import urljoin
import os
import subprocess

# 🚀 CONFIGURACIÓN DE RUTA PARA STREAMLIT CLOUD
# Forzamos a Playwright a instalar y buscar el navegador dentro de la carpeta del proyecto
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(os.getcwd(), "pw-browsers")

@st.cache_resource
def iniciar_entorno_playwright():
    ruta_navegador = os.environ["PLAYWRIGHT_BROWSERS_PATH"]
    
    # Si la carpeta del navegador no existe, procedemos a descargarla
    if not os.path.exists(ruta_navegador):
        with st.spinner("🔧 Descargando binarios de Chromium en el servidor (esto tomará un minuto)..."):
            # Instalamos las dependencias del sistema y el navegador Chromium en la ruta personalizada
            subprocess.run(["playwright", "install", "chromium"], env=os.environ, check=True)
            
iniciar_entorno_playwright()

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
    st.session_state["sitios"] = ["https://www.emol.com/", "https://www.lun.com/"]
if "palabras" not in st.session_state:
    st.session_state["palabras"] = ["Alexis Sanchez", "Elon Musk", "terremoto"]

# --- SECCIÓN DE CONFIGURACIÓN ---
st.sidebar.header("🛠️ Configuración de Búsqueda")

# Entrada para Sitios Web
st.sidebar.subheader("Sitios de Noticias")
sitios_input = st.sidebar.text_area(
    "Ingresa las URLs (una por línea):",
    value="\n".join(st.session_state["sitios"]),
    height=100
)

# Entrada para Palabras Clave
st.sidebar.subheader("Palabras Clave")
palabras_input = st.sidebar.text_area(
    "Ingresa las palabras clave (una por línea o separadas por coma):",
    value="\n".join(st.session_state["palabras"]),
    height=120
)

# Procesar entradas del usuario
if sitios_input:
    st.session_state["sitios"] = [s.strip() for s in sitios_input.split("\n") if s.strip()]
if palabras_input:
    if "," in palabras_input and "\n" not in palabras_input:
        st.session_state["palabras"] = [p.strip() for p in palabras_input.split(", ") if p.strip()]
    else:
        st.session_state["palabras"] = [p.strip() for p in palabras_input.split("\n") if p.strip()]

# Permitir descargar/guardar la configuración actual en un JSON
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

# --- FUNCIÓN DE SCRAPING ASÍNCRONA ---
async def escanear_sitio(url, palabras_clave, status_placeholder):
    resultados = []
    enlaces_procesados = set()  # Conjunto de control para almacenar URLs únicas
    status_placeholder.info(f"🌐 Conectando a {url}...")
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            status_placeholder.info(f"🔍 Analizando contenido de {url}...")
            
            enlaces = await page.locator("a").all()
            total_encontrados_sitio = 0
            
            for enlace in enlaces:
                texto_original = await enlace.inner_text()
                
                # 🚀 CORRECCIÓN CLAVE: Reemplaza saltos de línea (\n), tabulaciones (\t) 
                # y múltiples espacios continuos por un único espacio en blanco estándar.
                texto_limpio = re.sub(r'\s+', ' ', texto_original).strip()
                
                if len(texto_limpio) < 10:
                    continue
                    
                href = await enlace.get_attribute("href")
                
                if href:
                    # Formatear URLs relativas a absolutas
                    if href.startswith("/"):
                        href = urljoin(url, href)
                    elif not href.startswith("http"):
                        continue 
                    
                    # CONTROL DE DUPLICADOS: Si el enlace ya fue procesado, se descarta inmediatamente
                    if href in enlaces_procesados:
                        continue

                    # Evaluar coincidencia de palabras clave
                    for palabra in palabras_clave:
                        palabra_limpia = palabra.strip()
                        if not palabra_limpia:
                            continue
                            
                        # Comparación insensible a mayúsculas/minúsculas sobre el texto normalizado
                        if palabra_limpia.lower() in texto_limpio.lower():
                            resultados.append({
                                "Sitio": url,
                                "Titular": texto_limpio, # Guardamos el titular limpio y legible
                                "Palabra Coincidente": palabra_limpia,
                                "Enlace": href
                            })
                            enlaces_procesados.add(href)  # Registrar el enlace para evitar que se repita
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
col1, col2 = st.columns([1, 3])

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
        
        # Elementos dinámicos para el estado del scraping
        st.markdown("### ⏳ Estado del Proceso")
        progreso_bar = st.progress(0)
        total_sitios = len(st.session_state["sitios"])
        
        for idx, sitio in enumerate(st.session_state["sitios"]):
            status_box = st.empty() # Espacio dinámico reescribible por sitio
            
            # Ejecución asíncrona segura dentro del ciclo síncrono de Streamlit
            res = asyncio.run(escanear_sitio(sitio, st.session_state["palabras"], status_box))
            todos_los_resultados.extend(res)
            
            # Actualizar barra general de avance
            progreso_bar.progress((idx + 1) / total_sitios)
        
        # --- PRESENTACIÓN DE RESULTADOS ---
        st.markdown("---")
        st.subheader("📊 Resultados de la Búsqueda")
        
        if todos_los_resultados:
            df = pd.DataFrame(todos_los_resultados)
            st.metric("Total de noticias encontradas", len(df))
            
            # Agrupar los titulares por el sitio web de procedencia
            for sitio_agrupado, group_df in df.groupby("Sitio"):
                with st.expander(f"📌 {sitio_agrupado} ({len(group_df)} resultados)", expanded=True):
                    for _, row in group_df.iterrows():
                        # Generación de hipervínculos nativos en Markdown (abren automáticamente en otra pestaña)
                        st.markdown(f"- **[{row['Titular']}]({row['Enlace']})** — *(Filtro: {row['Palabra Coincidente']} )*")
                        
            # Botón adicional para exportar los hallazgos actuales a una hoja de cálculo
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Resultados (CSV)",
                data=csv_data,
                file_name="noticias_encontradas.csv",
                mime="text/csv"
            )
        else:
            st.warning("No se encontraron noticias que coincidan con los criterios establecidos.")
