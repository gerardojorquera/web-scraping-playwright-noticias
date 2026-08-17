# 📰 WebScraper de Noticias Dinámico con Playwright & Streamlit

Esta aplicación permite realizar raspado web (web scraping) en tiempo real de múltiples sitios de noticias de forma simultánea. El usuario puede buscar de manera dinámica palabras clave personalizadas a través de una interfaz gráfica intuitiva y moderna.

---

## ✨ Funcionalidades Principales

*   **Configuración Dinámica:** Panel lateral para ingresar listas personalizadas de URLs de noticias y palabras clave mediante cajas de texto independientes.
*   **Exportación de Parámetros:** Opción para descargar la configuración actual de búsqueda (sitios y palabras clave) en un archivo JSON local.
*   **Monitoreo en Tiempo Real:** Barra de progreso global e indicadores de estado individuales por sitio web que muestran la fase exacta del análisis y el conteo de hallazgos.
*   **Extracción Asíncrona:** Integración optimizada con Playwright asíncrono para agilizar la navegación de los selectores HTML y prevenir bloqueos del navegador.
*   **Resultados Interactivos:** Visualización de las noticias agrupadas por su dominio de origen, permitiendo abrir cada titular de forma directa en una pestaña nueva mediante hipervínculos nativos.
*   **Descarga de Reportes:** Generación de un botón dinámico para exportar todas las coincidencias encontradas a un archivo plano estructurado en formato `.csv`.

---

## 📋 Prerrequisitos del Sistema

Antes de iniciar la instalación local, asegúrate de contar con las siguientes herramientas en tu sistema operativo:

*   **Python 3.8 o superior** instalado en el sistema.
*   **Gestor de paquetes `pip`** actualizado.
*   **Navegador Chromium o dependencias de Playwright** instaladas en la terminal.

---

## 🚀 Guía de Ejecución Local

Sigue paso a paso estas instrucciones en la terminal de tu computadora para levantar el entorno de desarrollo:

### 1. Clonar o descargar el proyecto
Crea una carpeta en tu máquina e introduce los archivos `app.py` y `requirements.txt`. Abre tu terminal dentro de esa ruta.

### 2. Crear y activar un entorno virtual (Recomendado)
Para mantener las dependencias aisladas de tu sistema global:

*   **En Windows:**
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```
*   **En macOS/Linux:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

### 3. Instalar las dependencias de Python
Ejecuta el comando para instalar las librerías necesarias del proyecto:
```bash
pip install -r requirements.txt
```

### 4. Instalar los binarios del navegador de Playwright
Este paso instala de manera interna el navegador Chromium optimizado que utilizará el software en segundo plano (modo headless):
```bash
playwright install chromium
```

### 5. Iniciar la aplicación web
Lanza el servidor local de Streamlit mediante la consola:
```bash
streamlit run app.py
```

Al terminar de ejecutar el comando anterior, se abrirá de manera automática una ventana en tu navegador web predeterminado apuntando a la dirección local del servicio (usualmente `http://localhost:8501`).
