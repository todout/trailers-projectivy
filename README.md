# 🎬 Tráileres Fondos Projectivy (Android TV App)

Aplicación nativa para **Android TV** (ONN TV Box, Chromecast con Google TV, Fire TV, etc.) diseñada para reproducir tráileres oficiales en español a pantalla completa y sincronizados automáticamente con tu feed de fondos y recomendaciones en **Projectivy Launcher**.

---

## 📥 Instalación Rápida con Downloader (AFTVnews)

Puedes instalar la aplicación directamente en tu TV Box mediante la app **Downloader**:

| Método | Código / Enlace |
| :--- | :--- |
| **Código Downloader (AFTV)** | `4981706` |
| **Enlace AFTV Corto** | [go.aftvnews.com/4981706](https://go.aftvnews.com/4981706) |
| **Descarga Directa APK** | [trailers-projectivy.apk (GitHub Release)](https://github.com/todout/trailers-projectivy/releases/latest/download/trailers-projectivy.apk) |

### Pasos para instalar en tu Android TV / ONN Box:
1. Abre la aplicación **Downloader** en tu TV Box.
2. Ingresa el código **`4981706`** y pulsa en **Go**.
3. Acepta la descarga e instala la aplicación cuando finalice.
4. ¡Listo! El icono **Tráileres Fondos** aparecerá disponible en tu pantalla de inicio de Projectivy Launcher.

---

## ⚡ Características Principales

* 🚀 **Inicio Inmediato**: Al presionar la app desde tu pantalla de inicio, arranca directamente el tráiler oficial en español a pantalla completa sin pantallas intermedias ni tiempos muertos.
* 🔄 **Catálogo Dinámico y Enriquecido**:
  * **Diario (4 AM)**: Sincronización automática de *"Últimos fondos de tu TV"* y *"Recomendado para Ti"*.
  * **Semanal**: Top 10 en vivo de **Netflix** (Tudum Argentina), **Disney+**, **Prime Video**, **Max** y **Apple TV+**, además de categorías por género enriquecidas con TMDB y YouTube.
* 📺 **Overlay Inteligente**: Información elegante con póster, título, año, duración/episodios, sinopsis y proveedor que se oculta automáticamente a los 3 segundos.

---

## 🎮 Controles del Control Remoto (D-Pad)

| Botón Control Remoto | Acción |
| :---: | :--- |
| **▲ / ▼ (Arriba / Abajo)** | Cambia de categoría / fila del catálogo. |
| **◄ / ► (Izquierda / Derecha)** | Navega entre los títulos de la categoría actual. |
| **OK / Seleccionar** | **Pausa / Reanuda** la reproducción del tráiler. |
| **Doble toque ◄ / ►** | **Retrocede o avanza 10 segundos** en el vídeo. |
| **Atrás (Back)** | Cierra el reproductor y vuelve a Projectivy Launcher. |

---

## ⚙️ Estructura del Proyecto

* `app/`: Código fuente Android (Kotlin, ExoPlayer / YouTube Player nativo).
* `app/src/main/assets/trailers.json`: Catálogo JSON local empaquetado y actualizado.
* `scripts/update_daily_reddit.py`: Script diario de extracción de fondos y recomendaciones.
* `scripts/update_weekly_catalog.py`: Script semanal de plataformas y géneros (JustWatch, Tudum, Gemini y TMDB).
* `.github/workflows/build-apk.yml`: Compilación y release automático en GitHub Actions.
