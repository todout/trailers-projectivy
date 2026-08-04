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
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8'
}

def get_tmdb_info(title):
    encoded_title = urllib.parse.quote(title)
    url = f"https://www.themoviedb.org/search?query={encoded_title}"
    
    poster_url = None
    backdrop_url = None
    overview = None
    year = "2026"
    media_type = "PELÍCULA"
    extra_info = "1h 45m"
    
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        html = urllib.request.urlopen(req).read().decode('utf-8')
        
        match = re.search(r'href="/(movie|tv)/(\d+)[^"]*"', html)
        if match:
            m_type, tmdb_id = match.groups()
            media_type = "SERIE" if m_type == "tv" else "PELÍCULA"
            extra_info = "1 Temporada" if media_type == "SERIE" else "1h 45m"
            
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

def fetch_titles_from_reddit():
    """Intenta obtener los últimos 4 títulos desde el RSS de Reddit r/IMDB_esp"""
    titles = []
    try:
        import xml.etree.ElementTree as ET
        url = 'https://www.reddit.com/r/IMDB_esp/new.rss'
        req = urllib.request.Request(url, headers=HEADERS)
        xml_data = urllib.request.urlopen(req).read()
        root = ET.fromstring(xml_data)
        entries = root.findall('{http://www.w3.org/2005/Atom}entry')
        for entry in entries[:4]:
            t_node = entry.find('{http://www.w3.org/2005/Atom}title')
            if t_node is not None and t_node.text:
                clean_title = re.sub(r'\[.*?\]', '', t_node.text).strip()
                titles.append(clean_title)
    except Exception as e:
        print("  [Error obteniendo RSS de Reddit]:", e)
    return titles

def update_catalog_with_reddit_items(titles=None, push_to_git=False):
    if not titles:
        titles = fetch_titles_from_reddit()
        
    if not titles:
        print("No se encontraron títulos. Especifica una lista de títulos.")
        return

    print(f"Procesando {len(titles)} títulos para la categoría 'Recomendaciones del día':")
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
    filtered_rows = [r for r in rows if r.get('category') not in ["Fondos del Día (Reddit r/IMDB_esp)", "Recomendaciones del día"]]
    
    reddit_category = {
        "category": "Recomendaciones del día",
        "items": reddit_items
    }
    
    new_rows = [reddit_category] + filtered_rows
    updated_catalog = {"rows": new_rows}

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(updated_catalog, f, ensure_ascii=False, indent=2)

    print(f"\n[ÉXITO] Actualizado '{json_path}' con {len(reddit_items)} fondos del día.")

    if push_to_git:
        try:
            print("Subiendo cambios a GitHub...")
            subprocess.run(["git", "add", json_path], check=True)
            subprocess.run(["git", "commit", "-m", "Auto-update Fondos Reddit 4AM"], check=True)
            subprocess.run(["git", "push"], check=True)
            print("[ÉXITO] Cambios subidos a GitHub correctamente.")
        except Exception as e:
            print("[Error en Git Push]:", e)

if __name__ == '__main__':
    args = sys.argv[1:]
    do_push = "--push" in args
    custom_titles = [a for a in args if a != "--push"]
    
    update_catalog_with_reddit_items(custom_titles if custom_titles else None, push_to_git=do_push)
