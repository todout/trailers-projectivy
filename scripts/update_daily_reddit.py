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

def get_gemini_metadata(title):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        prompt = f"Información sobre la película o serie '{title}'. Responde ÚNICAMENTE en formato JSON con los campos: title, year (ej '2024'), media_type ('PELÍCULA' o 'SERIE'), overview (sinopsis detallada en español de 2 a 3 oraciones), poster_path (path tmdb ej '/abc.jpg' o null)."
        data = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
        res = urllib.request.urlopen(req, timeout=8)
        res_json = json.loads(res.read().decode('utf-8'))
        text = res_json['candidates'][0]['content']['parts'][0]['text']
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except Exception as e:
        print(f"  [Gemini API Warning para '{title}']:", e)
    return None

def get_tmdb_info(item):
    if isinstance(item, dict):
        title = item["title"]
        tmdb_path = item.get("tmdb_path")
    else:
        title = item
        tmdb_path = None

    if not tmdb_path:
        t_upper = title.strip().upper()
        if t_upper in ["PA QUERERTE", "PA' QUERERTE"]:
            tmdb_path = "tv/136228-pa-quererte"

    poster_url = None
    backdrop_url = None
    overview = None
    year = "2025"
    cur_media_type = "PELÍCULA"
    cur_extra_info = "1h 45m"
    
    try:
        if tmdb_path:
            paths_to_try = [tmdb_path]
        else:
            encoded_title = urllib.parse.quote(title)
            url = f"https://www.themoviedb.org/search?query={encoded_title}&language=es-ES"
            req = urllib.request.Request(url, headers=HEADERS)
            html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
            
            matches = re.findall(r'href="/(movie|tv)/(\d+[^"]*)"', html)
            if not matches:
                clean_t = re.sub(r'[^\w\s]', '', title)
                url2 = f"https://www.themoviedb.org/search?query={urllib.parse.quote(clean_t)}&language=es-ES"
                html2 = urllib.request.urlopen(urllib.request.Request(url2, headers=HEADERS), timeout=10).read().decode('utf-8')
                matches = re.findall(r'href="/(movie|tv)/(\d+[^"]*)"', html2)
                
            paths_to_try = [f"{m_type}/{path_id.split('?')[0].split('#')[0]}" for m_type, path_id in matches[:3]] if matches else []

        for path in paths_to_try:
            m_type = "tv" if path.startswith("tv/") else "movie"
            cur_media_type = "SERIE" if m_type == "tv" else "PELÍCULA"
            cur_extra_info = "Serie" if cur_media_type == "SERIE" else "1h 45m"

            for lang in ["es-ES", "es-MX", "es", "en-US"]:
                detail_url = f"https://www.themoviedb.org/{path}?language={lang}"
                try:
                    d_req = urllib.request.Request(detail_url, headers=HEADERS)
                    d_html = urllib.request.urlopen(d_req, timeout=8).read().decode('utf-8')
                    
                    if not poster_url:
                        p_match = re.search(r'https://image\.tmdb\.org/t/p/w\d+/([a-zA-Z0-9_\.]+\.jpg)', d_html)
                        og_images = re.findall(r'content="https://(?:image|media)\.themoviedb\.org/t/p/[^/]+/([a-zA-Z0-9_\.]+\.jpg)"', d_html)
                        
                        if p_match:
                            poster_url = f"https://image.tmdb.org/t/p/w500/{p_match.group(1)}"
                        elif og_images:
                            poster_url = f"https://image.tmdb.org/t/p/w500/{og_images[0]}"
                            
                        if og_images and len(og_images) >= 2:
                            backdrop_url = f"https://image.tmdb.org/t/p/w500/{og_images[1]}"
                        elif poster_url:
                            backdrop_url = poster_url
                        
                    y_match = re.search(r'\((\d{4})\)', d_html)
                    if y_match:
                        year = y_match.group(1)

                    o_match = re.search(r'<div class="overview"[^>]*>\s*<p>([^<]+)</p>', d_html)
                    if not o_match:
                        o_match = re.search(r'property="og:description" content="([^"]+)"', d_html)
                    if not o_match:
                        o_match = re.search(r'<meta name="description" content="([^"]+)"', d_html)

                    if o_match:
                        cand_overview = o_match.group(1).replace('...', '').strip()
                        spanish_stopwords = {"de", "la", "el", "en", "un", "una", "los", "las", "por", "para", "con", "que", "su", "sus", "del", "como", "sobre"}
                        words = [w.strip('.,;:"()') for w in cand_overview.lower().split()]
                        spanish_count = sum(1 for w in words if w in spanish_stopwords)
                        if spanish_count >= 2 and len(cand_overview) > 20:
                            overview = cand_overview
                            break
                except Exception:
                    pass

            if poster_url and overview:
                break

    except Exception as e:
        print(f"  [TMDB Error para '{title}']:", e)

    # Fallback to Gemini if overview or poster is missing
    if not overview or not poster_url:
        gem = get_gemini_metadata(title)
        if gem:
            if not overview and gem.get("overview"):
                overview = gem["overview"]
            if not year and gem.get("year"):
                year = gem["year"]
            if gem.get("media_type"):
                cur_media_type = gem["media_type"]
                cur_extra_info = "Serie" if cur_media_type == "SERIE" else "1h 45m"
            if not poster_url and gem.get("poster_path"):
                p_path = gem["poster_path"].strip('/')
                poster_url = f"https://image.tmdb.org/t/p/w500/{p_path}"
                backdrop_url = poster_url

    if not poster_url or not overview:
        return None

    subtitle = f"{cur_media_type} • {year} • {cur_extra_info}"
    return {
        "title": title,
        "subtitle": subtitle,
        "media_type": cur_media_type,
        "year": year,
        "extra_info": cur_extra_info,
        "poster_url": poster_url,
        "backdrop_url": backdrop_url or poster_url,
        "overview": overview
    }

def is_youtube_video_playable(yt_id):
    if not yt_id:
        return False
    try:
        url = f"https://www.youtube.com/watch?v={yt_id}"
        req = urllib.request.Request(url, headers=HEADERS)
        html = urllib.request.urlopen(req, timeout=6).read().decode('utf-8', errors='ignore')
        
        if '"status":"LOGIN_REQUIRED"' in html or 'Accede para confirmar tu edad' in html or 'restricción de edad' in html or 'age-gate' in html:
            return False
            
        playability_match = re.search(r'"playabilityStatus":\s*\{\s*"status":\s*"([^"]+)"', html)
        if playability_match and playability_match.group(1) != "OK":
            return False
            
        return True
    except Exception:
        return False

def get_youtube_trailer_id(title):
    query = f"{title} trailer oficial español latino"
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        html = urllib.request.urlopen(req, timeout=8).read().decode('utf-8')
        vids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
        for vid in vids[:6]:
            if is_youtube_video_playable(vid):
                return vid
    except Exception as e:
        print(f"  [YT Error para '{title}']:", e)
    return None

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

def get_personalized_recommendations(existing_catalog=None):
    pref_path = r'd:\Antrigravity - Projects\fondos-projectivy\user_preferences.json'
    if not os.path.exists(pref_path):
        pref_path = os.path.join(os.path.dirname(__file__), '../../fondos-projectivy/user_preferences.json')

    log_path = os.path.join(os.path.dirname(__file__), 'recommendations_log.json')
    if os.path.exists(log_path):
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
        except Exception:
            log_data = {"recommendations": {}}
    else:
        log_data = {"recommendations": {}}

    rec_log = log_data.get("recommendations", {})
    
    # Mapa de ítems existentes en el catálogo para reutilizar metadatos si ya existen
    existing_items_map = {}
    if existing_catalog and 'rows' in existing_catalog:
        for row in existing_catalog['rows']:
            for item in row.get('items', []):
                t_key = item.get('title', '').strip().lower()
                if t_key:
                    if t_key not in existing_items_map or item.get('media_type') == 'SERIE':
                        existing_items_map[t_key] = item

    recent_candidates = [
        "Los renglones torcidos de dios",
        "Bellas Artes",
        "El reino",
        "La sociedad de la nieve",
        "Cabo de miedo",
        "Terapia alternativa",
        "Sugar",
        "El botín",
        "Fundación",
        "Duna: Parte dos",
        "Oppenheimer",
        "The Last of Us",
        "La casa del dragón",
        "Severance"
    ]

    free_candidates = [
        "Knives Out",
        "La noche de 12 años",
        "El jardín de bronce",
        "El lobo de Wall Street",
        "Huye",
        "Ford v Ferrari",
        "El irlandés"
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

    today_str = time.strftime('%Y-%m-%d')
    used_keys = set()

    def resolve_item(t):
        t_clean = t.strip().lower()
        if t_clean in seen_titles or t_clean in used_keys:
            return None

        item_to_use = None
        if t_clean in rec_log and "item" in rec_log[t_clean]:
            print(f"  [Recomendado para Ti] Reutilizando desde Historial Log para: '{t}' (Recomendada {rec_log[t_clean].get('count', 0) + 1} veces)...")
            item_to_use = dict(rec_log[t_clean]["item"])
            rec_log[t_clean]["count"] = rec_log[t_clean].get("count", 0) + 1
            rec_log[t_clean]["last_recommended"] = today_str
        elif t_clean in existing_items_map:
            print(f"  [Recomendado para Ti] Reutilizando metadatos existentes en catálogo para: '{t}'...")
            item_to_use = dict(existing_items_map[t_clean])
            rec_log[t_clean] = {
                "count": 1,
                "last_recommended": today_str,
                "item": item_to_use
            }
        else:
            print(f"  [Recomendado para Ti] Enriqueciendo nuevo título desde Web: '{t}'...")
            tmdb = get_tmdb_info(t)
            yt_id = get_youtube_trailer_id(t)
            item_to_use = {
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
            }
            rec_log[t_clean] = {
                "count": 1,
                "last_recommended": today_str,
                "item": item_to_use
            }
            time.sleep(0.2)

        if item_to_use:
            yt_id = item_to_use.get("youtube_id")
            if not yt_id or not is_youtube_video_playable(yt_id):
                print(f"  [Recomendado para Ti] Descartado '{t}' porque su tráiler no es reproducible o tiene restricción de edad.")
                return None
            used_keys.add(t_clean)
            item_final = dict(item_to_use)
            item_final["provider"] = "Recomendado para Ti"
            return item_final
        return None

    recent_items = []
    for t in recent_candidates:
        item = resolve_item(t)
        if item:
            try:
                item_year = int(item.get("year", "2000"))
            except ValueError:
                item_year = 2026
            
            if item_year >= 2021:
                recent_items.append(item)
            if len(recent_items) >= 10:
                break

    free_items = []
    all_remaining_candidates = [c for c in recent_candidates + free_candidates if c.strip().lower() not in used_keys]
    for t in all_remaining_candidates:
        item = resolve_item(t)
        if item:
            free_items.append(item)
            if len(free_items) >= 10:
                break

    rec_items = recent_items + free_items

    log_data["recommendations"] = rec_log
    try:
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
        print(f"  [Historial Log] Guardado correctamente en '{log_path}'.")
    except Exception as e:
        print("  [Error guardando log de recomendaciones]:", e)

    return rec_items

def update_catalog_with_reddit_items(custom_titles=None, push_to_git=False):
    json_path = 'app/src/main/assets/trailers.json'
    if not os.path.exists(json_path):
        json_path = os.path.join(os.path.dirname(__file__), '../app/src/main/assets/trailers.json')

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            catalog = json.load(f)
    except Exception:
        catalog = {"rows": []}

    rows = catalog.get('rows', [])
    
    # 1. Extraer ítems existentes de "Últimos fondos de tu TV"
    existing_reddit_items = []
    existing_items_map = {}
    for r in rows:
        if r.get('category') == "Últimos fondos de tu TV":
            existing_reddit_items = r.get('items', [])
            for item in existing_reddit_items:
                t_key = item.get('title', '').strip().lower()
                p_url = item.get('poster_url', '')
                ov = item.get('overview', '')
                # Solo reutilizar si tiene póster real y sinopsis válida
                if t_key and 'gp31EwMH5D2bftOjscwkgTmoLAB' not in p_url and not ov.startswith("Sigue la historia y los eventos de"):
                    existing_items_map[t_key] = item

    if custom_titles:
        titles = custom_titles
    else:
        titles = fetch_titles_from_reddit(limit=25)
        
    if not titles:
        titles = DEFAULT_REDDIT_TITLES[:25]

    print(f"Procesando {len(titles)} títulos para la categoría 'Últimos fondos de tu TV':")
    final_reddit_items = []
    processed_keys = set()

    for t in titles:
        t_key = t.strip().lower()
        if t_key in processed_keys:
            continue

        # Reutilizar si ya existe y es válido
        if t_key in existing_items_map:
            print(f"  [Reutilizando existente sin rescrapear]: '{t}'")
            final_reddit_items.append(existing_items_map[t_key])
            processed_keys.add(t_key)
            continue

        print(f" - Buscando metadatos y tráiler para NUEVO título de Reddit: '{t}'...")
        yt_id = get_youtube_trailer_id(t)
        if not yt_id:
            print(f"  [Descartado por tráiler no reproducible o restricción de edad]: '{t}'")
            continue

        tmdb = get_tmdb_info(t)
        if not tmdb or 'gp31EwMH5D2bftOjscwkgTmoLAB' in tmdb.get('poster_url', ''):
            print(f"  [Descartado por metadatos o póster inválido]: '{t}'")
            continue

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
        final_reddit_items.append(item)
        processed_keys.add(t_key)
        time.sleep(0.3)

    # Conservar ítems válidos anteriores que no venían en este scrape de Reddit para mantener profundidad de catálogo (hasta 25)
    for item in existing_reddit_items:
        t_key = item.get('title', '').strip().lower()
        if t_key and t_key not in processed_keys:
            p_url = item.get('poster_url', '')
            ov = item.get('overview', '')
            if 'gp31EwMH5D2bftOjscwkgTmoLAB' not in p_url and not ov.startswith("Sigue la historia y los eventos de"):
                final_reddit_items.append(item)
                processed_keys.add(t_key)
                if len(final_reddit_items) >= 25:
                    break

    filtered_rows = [r for r in rows if r.get('category') not in ["Fondos del Día (Reddit r/IMDB_esp)", "Recomendaciones del día", "Últimos Fondos (r/IMDB_esp)", "Últimos fondos de tu TV", "Recomendado para Ti"]]
    
    reddit_category = {
        "category": "Últimos fondos de tu TV",
        "items": final_reddit_items[:25]
    }

    rec_items = get_personalized_recommendations(catalog)
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
            subprocess.run(["git", "add", json_path, "scripts/recommendations_log.json"], check=True)
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
