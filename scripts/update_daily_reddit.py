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
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
}

def load_gemini_api_key():
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        return api_key
    
    env_paths = [
        os.path.join(os.path.dirname(__file__), '../.env'),
        os.path.join(os.getcwd(), '.env'),
        '.env',
        r'd:\Antrigravity - Projects\fondos-projectivy\.env',
        os.path.join(os.path.dirname(__file__), '../../fondos-projectivy/.env')
    ]
    for env_path in env_paths:
        if os.path.exists(env_path):
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GEMINI_API_KEY="):
                            key_val = line.split("GEMINI_API_KEY=", 1)[1].strip().strip("'\"")
                            if key_val:
                                os.environ["GEMINI_API_KEY"] = key_val
                                return key_val
            except Exception:
                pass
    return None

def call_gemini_api(prompt, timeout=45):
    api_key = load_gemini_api_key()
    if not api_key:
        return None

    models_to_try = ["gemini-2.5-flash", "gemini-3.6-flash", "gemini-flash-latest"]
    for model in models_to_try:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            data = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
            res = urllib.request.urlopen(req, timeout=timeout)
            res_json = json.loads(res.read().decode('utf-8'))
            text = res_json['candidates'][0]['content']['parts'][0]['text']
            if text:
                return text
        except Exception as e:
            print(f"  [Gemini API Model Warning '{model}']:", e)
            continue
    return None

def get_gemini_metadata(title):
    try:
        prompt = f"Información sobre la película o serie '{title}'. Responde ÚNICAMENTE en formato JSON con los campos: title, year (ej '2024'), media_type ('PELÍCULA' o 'SERIE'), overview (sinopsis detallada en español de 2 a 3 oraciones), poster_path (path tmdb ej '/abc.jpg' o null), extra_info (si es película ej '1h 45m', si es serie ej '1 Temporada • 12 cap. • 45m')."
        text = call_gemini_api(prompt, timeout=12)
        if text:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
    except Exception as e:
        print(f"  [Gemini API Warning para '{title}']:", e)
    return None

def get_gemini_recommendation_candidates(pref_path):
    api_key = load_gemini_api_key()
    if not api_key:
        print("  [Gemini API Warning]: No se encontró GEMINI_API_KEY en entorno ni en .env")
        return None, None

    likes_summary = []
    dislikes_summary = []
    all_rated = []

    if os.path.exists(pref_path):
        try:
            with open(pref_path, 'r', encoding='utf-8') as f:
                prefs = json.load(f)
            
            for item in prefs.get('likes', []):
                if isinstance(item, dict) and 'title' in item:
                    t = item['title']
                    all_rated.append(t)
                    genres = ", ".join(item.get('genres', []))
                    yr = item.get('year', '')
                    likes_summary.append(f"{t} ({yr}, {genres})")
            
            for item in prefs.get('dislikes', []):
                if isinstance(item, dict) and 'title' in item:
                    t = item['title']
                    all_rated.append(t)
                    genres = ", ".join(item.get('genres', []))
                    yr = item.get('year', '')
                    dislikes_summary.append(f"{t} ({yr}, {genres})")
            
            for item in prefs.get('neutral', []):
                if isinstance(item, dict) and 'title' in item:
                    all_rated.append(item['title'])
        except Exception as e:
            print("  [Error leyendo user_preferences para Gemini]:", e)

    likes_txt = "\n".join("- " + x for x in likes_summary) if likes_summary else "Ninguno especificado"
    dislikes_txt = "\n".join("- " + x for x in dislikes_summary) if dislikes_summary else "Ninguno especificado"
    all_rated_txt = ", ".join(all_rated) if all_rated else "Ninguno"

    prompt = f"""Eres un recomendador experto de cine y series de TV en español.
Basándote estricta y minuciosamente en el perfil de gustos del usuario:

PELÍCULA FAVORITA PRINCIPAL (REFERENCIA SUPREMA):
- Tiempo de valientes (2005, Comedia, Crimen, Misterio, Acción, Buddy Movie por Damián Szifron) y Nueve reinas (2000, Crimen, Suspense).

CONTENIDO QUE LE ENCANTA (LIKES):
{likes_txt}

CONTENIDO QUE NO LE GUSTA (DISLIKES - EVITAR ESTRICTAMENTE):
{dislikes_txt}

TÍTULOS YA VISTOS O EVALUADOS (¡PROHIBIDO RECOMENDAR NINGUNO DE ESTOS TÍTULOS!):
{all_rated_txt}

Genera EXACTAMENTE 20 recomendaciones únicas (películas o series disponibles en streaming o cine) en español:
- 10 títulos RECIENTES (lanzamientos de los últimos 5-6 años, entre 2020 y 2026).
- 10 títulos de CUALQUIER ÉPOCA / CLÁSICOS QUE ENCAJEN CON SUS GUSTOS (comedia inteligente, intriga, suspenso, buddy movie, cine argentino e hispano de culto).

Responde ÚNICAMENTE con un objeto JSON válido con el siguiente esquema exacto (sin texto adicional ni explicaciones):
{{
  "recent": ["Título 1", "Título 2", "Título 3", "Título 4", "Título 5", "Título 6", "Título 7", "Título 8", "Título 9", "Título 10"],
  "any_year": ["Título 11", "Título 12", "Título 13", "Título 14", "Título 15", "Título 16", "Título 17", "Título 18", "Título 19", "Título 20"]
}}"""

    try:
        text = call_gemini_api(prompt, timeout=45)
        if text:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
                recent = parsed.get("recent", [])
                any_year = parsed.get("any_year", [])
                if isinstance(recent, list) and isinstance(any_year, list) and len(recent) > 0:
                    print(f"  [Gemini AI] ¡Éxito! Generados {len(recent)} títulos recientes y {len(any_year)} títulos variados basados en gustos del usuario.")
                    return recent, any_year
    except Exception as e:
        print("  [Gemini AI Error al pedir recomendaciones]:", e)

    return None, None



def parse_tv_extra_info(d_html, gem=None):
    seasons = None
    episodes = None
    runtime = None

    if d_html:
        s_match = re.search(r'(\d+)\s+Temporada', d_html, re.IGNORECASE)
        if not s_match:
            s_match = re.search(r'(\d+)\s+Season', d_html, re.IGNORECASE)
        if s_match:
            n_s = int(s_match.group(1))
            seasons = f"{n_s} Temporada{'s' if n_s > 1 else ''}"

        e_match = re.search(r'(\d+)\s+Episodio', d_html, re.IGNORECASE)
        if not e_match:
            e_match = re.search(r'(\d+)\s+Episode', d_html, re.IGNORECASE)
        if e_match:
            episodes = f"{e_match.group(1)} cap."

        r_matches = re.findall(r'(\d+)\s*(?:m|min|minutos)\b', d_html, re.IGNORECASE)
        for rm in r_matches:
            val = int(rm)
            if 15 <= val <= 150:
                runtime = f"{val}m"
                break

    if not runtime and isinstance(gem, dict):
        gem_ex = gem.get("extra_info") or gem.get("episode_runtime") or ""
        r_match = re.search(r'(\d+)\s*m', str(gem_ex), re.IGNORECASE)
        if r_match:
            val = int(r_match.group(1))
            if 15 <= val <= 150:
                runtime = f"{val}m"

    if not runtime:
        runtime = "45m"

    parts = []
    if seasons:
        parts.append(seasons)
    if episodes:
        parts.append(episodes)
    parts.append(runtime)

    return " • ".join(parts)

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
    latest_d_html = None
    
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

            for lang in ["es-ES", "es-MX", "es", "en-US"]:
                detail_url = f"https://www.themoviedb.org/{path}?language={lang}"
                try:
                    d_req = urllib.request.Request(detail_url, headers=HEADERS)
                    d_html = urllib.request.urlopen(d_req, timeout=8).read().decode('utf-8')
                    latest_d_html = d_html
                    
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
    gem = None
    if not overview or not poster_url or cur_media_type == "SERIE":
        gem = get_gemini_metadata(title)
        if gem:
            if not overview and gem.get("overview"):
                overview = gem["overview"]
            if not year and gem.get("year"):
                year = gem["year"]
            if gem.get("media_type"):
                cur_media_type = gem["media_type"]
            if not poster_url and gem.get("poster_path"):
                p_path = gem["poster_path"].strip('/')
                poster_url = f"https://image.tmdb.org/t/p/w500/{p_path}"
                backdrop_url = poster_url

    if not poster_url or not overview:
        return None

    if cur_media_type == "SERIE":
        cur_extra_info = parse_tv_extra_info(latest_d_html, gem.get("extra_info") if gem else None)
    else:
        cur_extra_info = "1h 45m"

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

        # Filtrar vídeos cortos (< 30s) o excesivamente largos (> 15m) que no sean verdaderos tráileres
        m_len = re.search(r'"lengthSeconds":"(\d+)"', html)
        m_dur = re.search(r'"approxDurationMs":"(\d+)"', html)
        duration_sec = 0
        if m_len:
            duration_sec = int(m_len.group(1))
        elif m_dur:
            duration_sec = int(m_dur.group(1)) // 1000

        if duration_sec > 0 and (duration_sec < 30 or duration_sec > 900):
            print(f"  [YouTube Filter] Descartado '{yt_id}' por duración ({duration_sec}s). Debe durar al menos 30s.")
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
        for vid in vids[:8]:
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
        'https://www.reddit.com/r/IMDB_esp/new/.rss',
        'https://old.reddit.com/r/IMDB_esp/new/.rss',
        'https://www.reddit.com/r/IMDB_esp/.rss'
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
    
    # Mapa de ítems existentes en el catálogo para reutilizar metadatos (Top 10 Netflix, Disney+, Prime, Max, etc.)
    existing_items_map = {}
    if existing_catalog and 'rows' in existing_catalog:
        for row in existing_catalog['rows']:
            for item in row.get('items', []):
                t_raw = item.get('title', '').strip()
                t_key = t_raw.lower()
                if t_key:
                    if t_key not in existing_items_map or item.get('media_type') == 'SERIE':
                        existing_items_map[t_key] = item
                    # También mapear título normalizado sin caracteres especiales
                    t_norm = re.sub(r'[^\w\s]', '', t_key)
                    if t_norm and t_norm not in existing_items_map:
                        existing_items_map[t_norm] = item

    # Pedir candidatas dinámicas a Gemini AI basadas en gustos del usuario
    gem_recent, gem_any = get_gemini_recommendation_candidates(pref_path)

    if gem_recent and gem_any:
        recent_candidates = gem_recent
        free_candidates = gem_any
    else:
        print("  [Recomendado para Ti] Usando lista de respaldo con orden dinámico...")
        backup_recent = [
            "Los renglones torcidos de dios", "Bellas Artes", "El reino", "La sociedad de la nieve",
            "Terapia alternativa", "Sugar", "El botín", "Fundación", "Duna: Parte dos",
            "Oppenheimer", "The Last of Us", "La casa del dragón", "Severance"
        ]
        backup_free = [
            "Knives Out", "La noche de 12 años", "El jardín de bronce", "El lobo de Wall Street",
            "Huye", "Ford v Ferrari", "El irlandés", "Cabo de miedo"
        ]
        import random
        random.shuffle(backup_recent)
        random.shuffle(backup_free)
        recent_candidates = backup_recent
        free_candidates = backup_free

    seen_titles = set()
    if os.path.exists(pref_path):
        try:
            with open(pref_path, 'r', encoding='utf-8') as f:
                prefs = json.load(f)
            for key in ['likes', 'dislikes', 'neutral']:
                for item in prefs.get(key, []):
                    if isinstance(item, dict) and 'title' in item:
                        t_l = item['title'].lower().strip()
                        seen_titles.add(t_l)
                        seen_titles.add(re.sub(r'[^\w\s]', '', t_l))
        except Exception as e:
            print("  [Error cargando user_preferences]:", e)

    today_str = time.strftime('%Y-%m-%d')
    used_keys = set()

    def resolve_item(t):
        t_clean = t.strip().lower()
        t_norm = re.sub(r'[^\w\s]', '', t_clean)

        if t_clean in seen_titles or t_norm in seen_titles or t_clean in used_keys or t_norm in used_keys:
            return None

        item_to_use = None

        # 1º PRIORIDAD: Buscar en ítems existentes del catálogo (Top 10 Netflix, Disney+, Prime, Max, etc.)
        matched_catalog_item = existing_items_map.get(t_clean) or existing_items_map.get(t_norm)
        if matched_catalog_item:
            print(f"  [Recomendado para Ti] Reutilizando metadatos existentes de plataforma para: '{t}' (desde catálogo)...")
            item_to_use = dict(matched_catalog_item)
            rec_log[t_clean] = {
                "count": rec_log.get(t_clean, {}).get("count", 0) + 1,
                "last_recommended": today_str,
                "item": item_to_use
            }

        # 2º PRIORIDAD: Buscar en Historial Log previo
        elif t_clean in rec_log and "item" in rec_log[t_clean]:
            print(f"  [Recomendado para Ti] Reutilizando desde Historial Log para: '{t}' (Recomendada {rec_log[t_clean].get('count', 0) + 1} veces)...")
            item_to_use = dict(rec_log[t_clean]["item"])
            rec_log[t_clean]["count"] = rec_log[t_clean].get("count", 0) + 1
            rec_log[t_clean]["last_recommended"] = today_str

        # 3º PRIORIDAD: Enriquecer desde Web (TMDb + YouTube)
        else:
            print(f"  [Recomendado para Ti] Enriqueciendo nuevo título sugerido por Gemini desde Web: '{t}'...")
            tmdb = get_tmdb_info(t)
            if not tmdb:
                print(f"  [Recomendado para Ti] No se pudieron obtener metadatos TMDb para '{t}'. Descartado.")
                return None
            yt_id = get_youtube_trailer_id(t)
            if not yt_id:
                print(f"  [Recomendado para Ti] No se encontró tráiler reproducible en YouTube para '{t}'. Descartado.")
                return None

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
            used_keys.add(t_norm)
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
            
            if item_year >= 2020:
                recent_items.append(item)
            else:
                # Si es más vieja pero válida, guardarla para free_items
                pass

            if len(recent_items) >= 10:
                break

    free_items = []
    all_remaining_candidates = [c for c in free_candidates + recent_candidates if c.strip().lower() not in used_keys]
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
                # Solo reutilizar si tiene póster real, sinopsis válida y extra_info completo con minutos (ej '45m')
                if t_key and 'gp31EwMH5D2bftOjscwkgTmoLAB' not in p_url and not ov.startswith("Sigue la historia y los eventos de"):
                    if item.get('media_type') == 'SERIE' and not re.search(r'\d+m', item.get('extra_info', '')):
                        pass
                    else:
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
            subprocess.run(["git", "commit", "-m", "Auto-update Fondos y Recomendaciones para Ti 4:15AM"], check=True)
            subprocess.run(["git", "push"], check=True)
            print("[ÉXITO] Cambios subidos a GitHub correctamente.")
        except Exception as e:
            print("[Error en Git Push]:", e)

if __name__ == '__main__':
    args = sys.argv[1:]
    do_push = "--push" in args
    custom_titles = [a for a in args if a != "--push"]
    
    update_catalog_with_reddit_items(custom_titles if custom_titles else None, push_to_git=do_push)
