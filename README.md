# 🎬 Tráileres Fondos Projectivy (Android TV App)

Aplicación nativa para **Android TV** (ONN TV Box) diseñada para reproducir tráileres en español a pantalla completa de los fondos automáticos de tu **Projectivy Launcher**.

---

## ⚡ Características Principales

* 🚀 **Inicio "De Una"**: Al hacer clic en el icono desde Projectivy Launcher, arranca inmediatamente el tráiler oficial en español a pantalla completa.
* 🎮 **Navegación 100% Control Remoto (D-Pad)**:
  * **▲ / ▼ (Arriba / Abajo)**: Cambia al **Tráiler Siguiente / Anterior** del feed de fondos.
  * **◄ / ► (Izquierda / Derecha)**: **Adelanta o atrasa 10 segundos** el tráiler actual.
  * **OK / Seleccionar**: **Pausa / Reanuda** el vídeo.
  * **Atrás (Back)**: Vuelve a Projectivy Launcher.
* 📺 **Interfaz Integrada**: Overlay transparente elegante con el título de la película, badges y contador que desaparece a los 3 segundos.

---

## 🛠️ Cómo Subir a GitHub y Generar tu Enlace AFTVnews (Downloader)

### Paso 1: Inicializar Git y subir a GitHub (Solo 1 vez)

Desde la terminal en esta carpeta (`D:\Antrigravity - Projects\trailers-projectivy`):

```bash
git init
git add .
git commit -m "Inicializar app Android TV para Projectivy"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/trailers-projectivy.git
git push -u origin main
```

*(Reemplaza `TU_USUARIO` con tu usuario de GitHub).*

### Paso 2: Descarga Directa Automática
Una vez subas el código, **GitHub Actions** compilará el archivo `.apk` en 1 minuto y generará automáticamente un enlace permanente:

```
https://github.com/TU_USUARIO/trailers-projectivy/releases/latest/download/trailers-projectivy.apk
```

### Paso 3: Crear Código Corto en AFTVnews (Downloader)

1. Ingresa en tu navegador a: **[https://go.aftvnews.com/](https://go.aftvnews.com/)**
2. Pega tu enlace de GitHub: `https://github.com/TU_USUARIO/trailers-projectivy/releases/latest/download/trailers-projectivy.apk`
3. Haz clic en **Create Short Code**.
4. ¡Anota el código de 5 dígitos generado (por ejemplo `12345`)!

### Paso 4: Instalar en tu ONN TV Box

1. En tu ONN TV Box, abre la aplicación **Downloader**.
2. Escribe el **código de 5 dígitos** en la casilla central de Downloader y dale a **Go**.
3. Se descargará el archivo `.apk` y te pedirá confirmación para **Instalar**.
4. ¡Listo! El icono **Tráileres Fondos** aparecerá nativamente en tu launcher Projectivy.
