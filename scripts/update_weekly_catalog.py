import urllib.request
import urllib.parse
import json
import re
import time
import sys
import subprocess
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8'
}

# Categorías por Género (Multi-plataforma) y Plataformas (Sin Terror)
GENRE_AND_PLATFORM_CATALOG = {
    "Top 10: Misterio, Intriga y Suspenso": [
        "Sugar", "The Crow Girl", "Gone", "Huye", "El diablo en Ohio",
        "Mensajes de voz para Isabelle", "El botin", "El poligamo", "Hasta el final", "Frankenstein"
    ],
    "Top 10: Ciencia Ficción y Acción": [
        "Silo", "Separacion", "Duna: Parte dos", "F1 la pelicula", "Avatar: Fuego y ceniza",
        "Interestelar", "The Mandalorian", "Fundacion", "Avengers: Endgame", "Proyecto Fin del Mundo"
    ],
    "Top 10: Basadas en hechos reales": [
        "Oppenheimer", "Los asesinos de la luna", "La sociedad de la nieve", "Shogun", "Chernobyl",
        "El precio de la verdad", "Bohemian Rhapsody", "Ford v Ferrari", "El irlandes", "Sound of Freedom"
    ],
    "Top 10 Disney+": [
        "El diablo viste a la moda 2", "El diario de la princesa", "Furia",
        "Avatar: Fuego y ceniza", "Los Simpson", "Malcolm en el medio",
        "Grey's Anatomy", "Modern Family", "Shōgun", "El encargado"
    ],
    "Top 10 Netflix": [
        "GIGN: Unidad de elite", "El otro padre", "No soy quien crees", "Pesadilla en la cocina",
        "Deseo", "El cobrador de deudas", "Culpa mia", "La extorsion",
        "Mision de rescate 2", "Merlina"
    ],
    "Top 10 Prime Video": [
        "Amos del Universo", "Nunca debimos entrar", "Proyecto Fin del Mundo",
        "Spider-Man: Sin camino a casa", "La casa del dragon", "Silo",
        "Te encontrare", "El mentalista", "From", "El oso"
    ],
    "Top 10 Max": [
        "El diablo viste a la moda 2", "Boda sangrienta 2", "Duna: Parte dos",
        "Batman", "El Club de la Pelea", "La casa del dragon", "El Pengüino",
        "Juego de tronos", "The Last of Us", "Succession"
    ],
    "Top 10 Apple TV+": [
        "The Dink: Pasion por el pickleball", "F1 la pelicula", "El abismo secreto",
        "Silo", "Separacion", "Ted Lasso", "The Morning Show",
        "Fundacion", "Para toda la humanidad", "Presunto inocente"
    ]
}

def query_gemini_recommendations(api_key, genre_prompt):
    """Consulta a Gemini API para obtener las 10 mejores recomendaciones del momento si hay clave presente."""
    if not api_key:
        return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    prompt = f"Devuelve exactamente un array JSON con 10 nombres de peliculas o series en tendencia (sin incluir terror ni horror) sobre: {genre_prompt}. Formato estricto: [\"Titulo 1\", \"Titulo 2\", ...]"
    payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode('utf-8')
    
    try:
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
        res = urllib.request.urlopen(req, timeout=8).read().decode('utf-8')
        data = json.loads(res)
        text = data['candidates'][0]['content']['parts'][0]['text']
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except Exception as e:
        print(f"  [Gemini Note]: Usando catálogo optimizado para '{genre_prompt}'")
    return None

def get_tmdb_info(title):
    encoded_title = urllib.parse.quote(title)
    url = f"https://www.themoviedb.org/search?query={encoded_title}"
    
    poster_url = None
    backdrop_url = None
    overview = None
    year = "2026"
    media_type = "PELÍCULA"
    extra_info = "1h 48m"
    
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        html = urllib.request.urlopen(req).read().decode('utf-8')
        
        match = re.search(r'href="/(movie|tv)/(\d+)[^"]*"', html)
        if match:
            m_type, tmdb_id = match.groups()
            media_type = "SERIE" if m_type == "tv" else "PELÍCULA"
            extra_info = "1 Temporada" if media_type == "SERIE" else "1h 48m"
            
            detail_url = f"https://www.themoviedb.org/{m_type}/{tmdb_id}?language=es-MX"
            d_req = urllib.request.Request(detail_url, headers=HEADERS)
            d_html = urllib.request.urlopen(d_req).read().decode('utf-8')
            
            p_match = re.search(r'https://image\.tmdb\.org/t/p/w\d+/([a-zA-Z0-9_\.]+\.jpg)', d_html)
            if p_match:
                poster_url = f"https://image.tmdb.org/t/p/w500/{p_match.group(1)}"
                
            og_images = re.findall(r'content="https://media\.themoviedb\.org/t/p/[^/]+/([a-zA-Z0-9_\.]+\.jpg)"', d_html)
            if not og_images:
                og_images = re.findall(r'content="https://image\.tmdb\.org/t/p/[^/]+/([a-zA-Z0-9_\.]+\.jpg)"', d_html)
                
            if len(og_images) >= 2:
                backdrop_url = f"https://image.tmdb.org/t/p/w500/{og_images[1]}"
            elif len(og_images) == 1:
                backdrop_url = f"https://image.tmdb.org/t/p/w500/{og_images[0]}"
            else:
                backdrop_url = poster_url
                
            o_match = re.search(r'<meta name="description" content="([^"]+)"', d_html)
            if o_match:
                overview = o_match.group(1).replace('...', '').strip()

            y_match = re.search(r'\((\d{4})\)', d_html)
            if y_match:
                year = y_match.group(1)
    except Exception as e:
        print(f"  [TMDB Error para '{title}']:", e)

    if not poster_url:
        poster_url = "https://image.tmdb.org/t/p/w500/gp31EwMH5D2bftOjscwkgTmoLAB.jpg"
    if not backdrop_url:
        backdrop_url = poster_url
    if not overview:
        overview = f"Sigue la historia y los eventos de {title}."
        
    subtitle = f"{media_type} • {year} • {extra_info}"
    return {
        "title": title,
        "subtitle": subtitle,
        "media_type": media_type,
        "year": year,
        "extra_info": extra_info,
        "poster_url": poster_url,
        "backdrop_url": backdrop_url,
        "overview": overview
    }

def get_youtube_trailer_id(title):
    query = f"{title} trailer oficial espanol latino"
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        html = urllib.request.urlopen(req).read().decode('utf-8')
        vids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
        if vids:
            return vids[0]
    except Exception as e:
        print(f"  [YT Error para '{title}']:", e)
    return "cAHSi8AXbCE"

def run_weekly_update(gemini_api_key=None, push_to_git=False):
    print("=== INICIANDO ACTUALIZACIÓN SEMANAL DE CATÁLOGO Y GÉNEROS (SIN TERROR) ===")
    
    json_path = 'app/src/main/assets/trailers.json'
    if not os.path.exists(json_path):
        json_path = os.path.join(os.path.dirname(__file__), '../app/src/main/assets/trailers.json')

    # Preservar primero los Fondos del Día de Reddit si existen
    reddit_category = None
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            catalog = json.load(f)
            for row in catalog.get('rows', []):
                if row.get('category') == "Fondos del Día (Reddit r/IMDB_esp)":
                    reddit_category = row
                    break
    except Exception:
        pass

    new_rows = []
    if reddit_category:
        new_rows.append(reddit_category)

    # Construir cada categoría por género y por plataforma
    for cat_name, default_titles in GENRE_AND_PLATFORM_CATALOG.items():
        print(f"\n--- Procesando Categoría Semanal: '{cat_name}' ---")
        
        titles = None
        if gemini_api_key and "Top 10:" in cat_name:
            titles = query_gemini_recommendations(gemini_api_key, cat_name)
            
        if not titles:
            titles = default_titles

        items = []
        for t in titles:
            print(f"  Enriqueciendo con TMDB & YouTube: '{t}'...")
            tmdb = get_tmdb_info(t)
            yt_id = get_youtube_trailer_id(t)
            items.append({
                "title": tmdb["title"],
                "subtitle": tmdb["subtitle"],
                "media_type": tmdb["media_type"],
                "year": tmdb["year"],
                "extra_info": tmdb["extra_info"],
                "poster_url": tmdb["poster_url"],
                "backdrop_url": tmdb["backdrop_url"],
                "overview": tmdb["overview"],
                "youtube_id": yt_id,
                "trailer_url": f"https://www.youtube.com/watch?v={yt_id}"
            })
            time.sleep(0.2)

        new_rows.append({
            "category": cat_name,
            "items": items
        })

    updated_catalog = {"rows": new_rows}
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(updated_catalog, f, ensure_ascii=False, indent=2)

    print(f"\n[ÉXITO] Catálogo semanal actualizado correctamente en '{json_path}'!")

    if push_to_git:
        try:
            print("Subiendo catálogo semanal a GitHub...")
            subprocess.run(["git", "add", json_path], check=True)
            subprocess.run(["git", "commit", "-m", "Auto-update Catálogo Semanal (Reemplazar Terror por Hechos Reales)"], check=True)
            subprocess.run(["git", "push"], check=True)
            print("[ÉXITO] Cambios semanales subidos a GitHub correctamente.")
        except Exception as e:
            print("[Error en Git Push]:", e)

if __name__ == '__main__':
    args = sys.argv[1:]
    do_push = "--push" in args
    g_key = os.environ.get("GEMINI_API_KEY", None)
    for arg in args:
        if arg.startswith("--gemini-key="):
            g_key = arg.split("=", 1)[1]
    run_weekly_update(gemini_api_key=g_key, push_to_git=do_push)
