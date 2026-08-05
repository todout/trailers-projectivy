import urllib.request
import urllib.parse
import json
import re
import time
import sys
import subprocess
import os

# Configuración de codificación UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
}

def get_tmdb_info(item):
    if isinstance(item, dict):
        title = item["title"]
        tmdb_path = item.get("tmdb_path")
    else:
        title = item
        tmdb_path = None

    poster_url = None
    backdrop_url = None
    overview = None
    year = "2026"
    media_type = "PELÍCULA"
    extra_info = "1h 45m"
    
    try:
        if tmdb_path:
            paths_to_try = [tmdb_path]
        else:
            encoded_title = urllib.parse.quote(title)
            url = f"https://www.themoviedb.org/search?query={encoded_title}&language=es-ES"
            req = urllib.request.Request(url, headers=HEADERS)
            html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
            
            matches = re.findall(r'<a[^>]*class="[^"]*result[^"]*"[^>]*href="/(movie|tv)/(\d+)[^"]*"', html)
            if not matches:
                matches = re.findall(r'<div class="card[^"]*">.*?<a[^>]*href="/(movie|tv)/(\d+)[^"]*"', html, re.DOTALL)
            if not matches:
                matches = re.findall(r'<h2><a[^>]*href="/(movie|tv)/(\d+)[^"]*"', html)
            if not matches:
                matches = re.findall(r'href="/(movie|tv)/(\d+)[^"]*"', html)
                
            paths_to_try = [f"{m_type}/{tmdb_id}" for m_type, tmdb_id in matches[:3]] if matches else []

        for path in paths_to_try:
            for lang in ["es-ES", "es-MX", "es"]:
                detail_url = f"https://www.themoviedb.org/{path}?language={lang}"
                try:
                    d_req = urllib.request.Request(detail_url, headers=HEADERS)
                    d_html = urllib.request.urlopen(d_req, timeout=8).read().decode('utf-8')
                    
                    m_type = "tv" if path.startswith("tv/") else "movie"
                    cur_media_type = "SERIE" if m_type == "tv" else "PELÍCULA"
                    cur_extra_info = "1 Temporada" if cur_media_type == "SERIE" else "1h 45m"

                    p_match = re.search(r'https://image\.tmdb\.org/t/p/w\d+/([a-zA-Z0-9_\.]+\.jpg)', d_html)
                    cur_poster = f"https://image.tmdb.org/t/p/w500/{p_match.group(1)}" if p_match else None
                        
                    og_images = re.findall(r'content="https://media\.themoviedb\.org/t/p/[^/]+/([a-zA-Z0-9_\.]+\.jpg)"', d_html)
                    if not og_images:
                        og_images = re.findall(r'content="https://image\.tmdb\.org/t/p/[^/]+/([a-zA-Z0-9_\.]+\.jpg)"', d_html)
                        
                    if len(og_images) >= 2:
                        cur_backdrop = f"https://image.tmdb.org/t/p/w500/{og_images[1]}"
                    elif len(og_images) == 1:
                        cur_backdrop = f"https://image.tmdb.org/t/p/w500/{og_images[0]}"
                    else:
                        cur_backdrop = cur_poster
                        
                    o_match = re.search(r'<div class="overview"[^>]*>\s*<p>([^<]+)</p>', d_html)
                    if not o_match:
                        o_match = re.search(r'property="og:description" content="([^"]+)"', d_html)
                    if not o_match:
                        o_match = re.search(r'<meta name="description" content="([^"]+)"', d_html)
                    cur_overview = o_match.group(1).replace('...', '').strip() if o_match else None

                    y_match = re.search(r'\((\d{4})\)', d_html)
                    cur_year = y_match.group(1) if y_match else "2026"
                    
                    # Detect English overviews accurately
                    spanish_stopwords = {"de", "la", "el", "en", "un", "una", "los", "las", "por", "para", "con", "que", "su", "sus", "del", "como", "sobre"}
                    english_stopwords = {"is", "the", "who", "and", "with", "her", "his", "their", "from", "about", "which", "after", "when", "into"}
                    words = [w.strip('.,;:"()') for w in cur_overview.lower().split()]
                    spanish_count = sum(1 for w in words if w in spanish_stopwords)
                    english_count = sum(1 for w in words if w in english_stopwords)
                    is_english = (english_count >= 3) and (spanish_count < 2)

                    if cur_overview and not is_english and len(cur_overview) > 20:
                        subtitle = f"{cur_media_type} • {cur_year} • {cur_extra_info}"
                        return {
                            "title": title,
                            "subtitle": subtitle,
                            "media_type": cur_media_type,
                            "year": cur_year,
                            "extra_info": cur_extra_info,
                            "poster_url": cur_poster or "https://image.tmdb.org/t/p/w500/gp31EwMH5D2bftOjscwkgTmoLAB.jpg",
                            "backdrop_url": cur_backdrop or cur_poster or "https://image.tmdb.org/t/p/w500/gp31EwMH5D2bftOjscwkgTmoLAB.jpg",
                            "overview": cur_overview
                        }
                except Exception:
                    pass
    except Exception as e:
        print(f"  [TMDB Error para '{title}']:", e)

    subtitle = f"{media_type} • {year} • {extra_info}"
    return {
        "title": title,
        "subtitle": subtitle,
        "media_type": media_type,
        "year": year,
        "extra_info": extra_info,
        "poster_url": poster_url or "https://image.tmdb.org/t/p/w500/gp31EwMH5D2bftOjscwkgTmoLAB.jpg",
        "backdrop_url": backdrop_url or poster_url or "https://image.tmdb.org/t/p/w500/gp31EwMH5D2bftOjscwkgTmoLAB.jpg",
        "overview": overview or f"Sigue la historia y los eventos de {title}."
    }

def get_youtube_trailer_id(title):
    query = f"{title} trailer oficial español latino"
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

DEFAULT_REDDIT_TITLES = [
    "ESCÁNDALO, RELATO DE UNA OBSESIÓN", "LA PROMESA", "TRES METROS SOBRE EL CIELO",
    "HOMBRES DE PIEL DURA", "SUSANA Y ELVIRA SIN PLAN B", "PA QUERERTE",
    "LOS DEL LADO OESTE", "EL HOYO", "GIGN: UNIDAD DE ÉLITE", "EL OTRO PADRE",
    "EL COBRADOR DE DEUDAS", "EL LABERINTO DEL FAUNO", "LEY Y ORDEN: UNIDAD DE VÍCTIMAS ESPECIALES",
    "SILO", "HOUSE", "CULPA MÍA", "ROSE OF NEVADA", "CUÁNTAME CÓMO PASÓ",
    "FURIOSA", "LA AMBICIÓN DE LOS SAVAGE", "LOS CREYENTES", "DEXTER"
]

def fetch_titles_from_reddit(limit=25):
    """Obtiene los últimos 25 títulos desde el RSS de Reddit r/IMDB_esp"""
    titles = []
    urls = [
        f'https://www.reddit.com/r/IMDB_esp/new/.rss?limit={limit}',
        f'https://old.reddit.com/r/IMDB_esp/new/.rss?limit={limit}',
        f'https://www.reddit.com/r/IMDB_esp/.rss?limit={limit}'
    ]
    import xml.etree.ElementTree as ET
    for url in urls:
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            xml_data = urllib.request.urlopen(req, timeout=10).read()
            root = ET.fromstring(xml_data)
            entries = root.findall('{http://www.w3.org/2005/Atom}entry')
            for entry in entries[:limit]:
                t_node = entry.find('{http://www.w3.org/2005/Atom}title')
                if t_node is not None and t_node.text:
                    clean_title = re.sub(r'\[.*?\]', '', t_node.text).strip()
                    if clean_title and clean_title not in titles:
                        titles.append(clean_title)
            if len(titles) > 0:
                print(f"  [Obtenidos {len(titles)} títulos desde Reddit RSS]")
                break
        except Exception as e:
            print(f"  [Advertencia RSS Reddit '{url}']:", e)

    if not titles:
        print("  [Usando lista de respaldo para r/IMDB_esp]")
        titles = DEFAULT_REDDIT_TITLES[:limit]

    return titles

def get_personalized_recommendations():
    pref_path = r'd:\Antrigravity - Projects\fondos-projectivy\user_preferences.json'
    if not os.path.exists(pref_path):
        pref_path = os.path.join(os.path.dirname(__file__), '../../fondos-projectivy/user_preferences.json')
    
    candidates = [
        "Los renglones torcidos de dios",
        "Bellas Artes",
        "El reino",
        "Porno y helado",
        "La sociedad de la nieve",
        "Knives Out",
        "La noche de 12 años",
        "Cabo de miedo",
        "Terapia alternativa",
        "Argentina, 1985"
    ]
    
    seen_titles = set()
    if os.path.exists(pref_path):
        try:
            with open(pref_path, 'r', encoding='utf-8') as f:
                prefs = json.load(f)
            for key in ['likes', 'dislikes', 'neutral']:
                for item in prefs.get(key, []):
                    if isinstance(item, dict) and 'title' in item:
                        seen_titles.add(item['title'].lower().strip())
        except Exception as e:
            print("  [Error cargando user_preferences]:", e)

    rec_items = []
    for t in candidates:
        if t.lower().strip() in seen_titles:
            continue
        print(f"  [Recomendado para Ti] Enriqueciendo: '{t}'...")
        tmdb = get_tmdb_info(t)
        yt_id = get_youtube_trailer_id(t)
        rec_items.append({
            "title": tmdb["title"],
            "subtitle": tmdb["subtitle"],
            "media_type": tmdb["media_type"],
            "year": tmdb["year"],
            "extra_info": tmdb["extra_info"],
            "poster_url": tmdb["poster_url"],
            "backdrop_url": tmdb["backdrop_url"],
            "overview": tmdb["overview"],
            "youtube_id": yt_id,
            "trailer_url": f"https://www.youtube.com/watch?v={yt_id}",
            "provider": "Recomendado para Ti"
        })
        time.sleep(0.2)
        if len(rec_items) >= 10:
            break
            
    return rec_items

def update_catalog_with_reddit_items(custom_titles=None, push_to_git=False):
    if custom_titles:
        titles = custom_titles
    else:
        titles = fetch_titles_from_reddit(limit=25)
        
    if not titles:
        titles = DEFAULT_REDDIT_TITLES[:25]

    print(f"Procesando {len(titles)} títulos para la categoría 'Últimos fondos de tu TV':")
    reddit_items = []
    
    for t in titles:
        print(f" - Buscando metadatos y tráiler para: '{t}'...")
        tmdb = get_tmdb_info(t)
        yt_id = get_youtube_trailer_id(t)
        
        item = {
            "title": tmdb["title"],
            "subtitle": tmdb["subtitle"],
            "media_type": tmdb["media_type"],
            "year": tmdb["year"],
            "extra_info": tmdb["extra_info"],
            "poster_url": tmdb["poster_url"],
            "backdrop_url": tmdb["backdrop_url"],
            "overview": tmdb["overview"],
            "youtube_id": yt_id,
            "trailer_url": f"https://www.youtube.com/watch?v={yt_id}",
            "provider": "Reddit r/IMDB_esp"
        }
        reddit_items.append(item)
        time.sleep(0.3)

    json_path = 'app/src/main/assets/trailers.json'
    if not os.path.exists(json_path):
        json_path = os.path.join(os.path.dirname(__file__), '../app/src/main/assets/trailers.json')

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            catalog = json.load(f)
    except Exception:
        catalog = {"rows": []}

    rows = catalog.get('rows', [])
    filtered_rows = [r for r in rows if r.get('category') not in ["Fondos del Día (Reddit r/IMDB_esp)", "Recomendaciones del día", "Últimos Fondos (r/IMDB_esp)", "Últimos fondos de tu TV", "Recomendado para Ti"]]
    
    reddit_category = {
        "category": "Últimos fondos de tu TV",
        "items": reddit_items
    }

    rec_items = get_personalized_recommendations()
    rec_category = {
        "category": "Recomendado para Ti",
        "items": rec_items
    }
    
    new_rows = [reddit_category, rec_category] + filtered_rows
    updated_catalog = {"rows": new_rows}

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(updated_catalog, f, ensure_ascii=False, indent=2)

    print(f"\n[ÉXITO] Actualizado '{json_path}' con Fondos del Día y Recomendaciones a medida.")

    if push_to_git:
        try:
            print("Subiendo cambios a GitHub...")
            subprocess.run(["git", "add", json_path], check=True)
            subprocess.run(["git", "commit", "-m", "Auto-update Fondos y Recomendaciones para Ti 4AM"], check=True)
            subprocess.run(["git", "push"], check=True)
            print("[ÉXITO] Cambios subidos a GitHub correctamente.")
        except Exception as e:
            print("[Error en Git Push]:", e)

if __name__ == '__main__':
    args = sys.argv[1:]
    do_push = "--push" in args
    custom_titles = [a for a in args if a != "--push"]
    
    update_catalog_with_reddit_items(custom_titles if custom_titles else None, push_to_git=do_push)
