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
    "Top 10: Crimen, Policiales y Thrillers": [
        {"title": "Mindhunter", "tmdb_path": "tv/67744-mindhunter"},
        {"title": "True Detective", "tmdb_path": "tv/46648-true-detective"},
        {"title": "Fargo", "tmdb_path": "tv/57243-fargo"},
        {"title": "Pecados Capitales", "tmdb_path": "movie/807-se7en"},
        {"title": "Sicario", "tmdb_path": "movie/273481-sicario"},
        {"title": "El secreto de sus ojos", "tmdb_path": "movie/25376-el-secreto-de-sus-ojos"},
        {"title": "Prisioneros", "tmdb_path": "movie/146233-prisoners"},
        {"title": "Zodiac", "tmdb_path": "movie/1949-zodiac"},
        {"title": "Mare of Easttown", "tmdb_path": "tv/101088-mare-of-easttown"},
        {"title": "El robo del siglo", "tmdb_path": "movie/653601-el-robo-del-siglo"}
    ],
    "Top 10: Basadas en hechos reales": [
        {"title": "Oppenheimer", "tmdb_path": "movie/872585-oppenheimer"}, "Los asesinos de la luna", "La sociedad de la nieve", "Shogun", "Chernobyl",
        "El precio de la verdad", "Bohemian Rhapsody", "Ford v Ferrari", "El irlandes", "Sound of Freedom"
    ],
    "Top 10: Habladas en Español (Latam y España)": [
        {"title": "La casa de papel", "tmdb_path": "tv/71446-money-heist"},
        {"title": "El encargado", "tmdb_path": "tv/154823-el-encargado"},
        {"title": "Envidiosa", "tmdb_path": "tv/270425-envidiosa"},
        {"title": "El eternauta", "tmdb_path": "tv/103516-el-eternauta"},
        {"title": "Berlín", "tmdb_path": "tv/202250-berlin"},
        {"title": "Cromañón", "tmdb_path": "tv/273934-cromanon"},
        {"title": "Relatos salvajes", "tmdb_path": "movie/265195-wild-tales"},
        {"title": "División Palermo", "tmdb_path": "tv/218843-division-palermo"},
        {"title": "Machos Alfa", "tmdb_path": "tv/215707-machos-alfa"},
        {"title": "Los Simuladores", "tmdb_path": "tv/15647-los-simuladores"}
    ],
    "Top 10 Disney+": [
        "El diablo viste a la moda 2", "El diario de la princesa", {"title": "Furia", "tmdb_path": "tv/287238-furious"},
        {"title": "Avatar: Fuego y ceniza", "tmdb_path": "movie/83533-avatar-fire-and-ash"}, "Los Simpson", "Malcolm en el medio",
        "Grey's Anatomy", "Modern Family", "Shōgun", "El encargado"
    ],
    "Top 10 Netflix": [
        "Elize: Sombras de una mujer", "Los creyentes", "Deseo", "72 horas",
        "23 000 vidas", "A pesar de ti", "El cobrador de deudas",
        "Una tóxica historia de amor", "3:10 Misión peligrosa", "Cuarentena 2: Terminal",
        "GIGN: Unidad de élite", "El otro padre", "Te encontraré",
        "El mapa de los anhelos", "Valle Salvaje", "El polígamo",
        "La casa de la pradera", "Agente Kim reactivado", "Perdiendo el juicio", "Mi otra yo"
    ],
    "Top 10 Prime Video": [
        "Amos del Universo", "Nunca debimos entrar", "Proyecto Fin del Mundo",
        "Spider-Man: Sin camino a casa", "La casa del dragon", "Silo",
        "Te encontrare", "El mentalista", "From", "El oso"
    ],
    "Top 10 Max": [
        "El diablo viste a la moda 2", "Boda sangrienta 2", "Duna: Parte dos",
        {"title": "Batman Inicia", "tmdb_path": "movie/272-batman-begins"}, "El Club de la Pelea", "La casa del dragon", {"title": "El Pengüino", "tmdb_path": "tv/194764-the-penguin"},
        "Juego de tronos", "The Last of Us", "Succession"
    ],
    "Top 10 Apple TV+": [
        "The Dink: Pasion por el pickleball", "F1 la pelicula", "El abismo secreto",
        "Silo", "Separacion", "Ted Lasso", "The Morning Show",
        "Fundacion", "Para toda la humanidad", "Presunto inocente"
    ]
}

import http.client

def fetch_tudum_titles(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        try:
            res = urllib.request.urlopen(req, timeout=10)
            html = res.read().decode('utf-8', errors='ignore')
        except http.client.IncompleteRead as e:
            html = e.partial.decode('utf-8', errors='ignore')
        
        button_titles = re.findall(r'<td[^>]*class="title"[^>]*>.*?<button>([^<]+)</button>', html, re.DOTALL)
        if not button_titles:
            button_titles = re.findall(r'data-uia="top10-card-logo"[^>]*><img [^>]*alt="([^"]+)"', html)
            
        items = []
        for t in button_titles:
            clean = re.sub(r': Temporada \d+|: Miniserie', '', t).strip()
            if clean and clean not in [i if isinstance(i, str) else i["title"] for i in items] and not clean.startswith("Top 10"):
                if clean == "Atormentado":
                    items.append({"title": "Atormentado", "tmdb_path": "movie/64720-take-shelter"})
                elif clean == "Contrato para matar":
                    items.append({"title": "Contrato para matar", "tmdb_path": "movie/945937-fast-charlie"})
                elif clean in ["El sobreviviente", "El Sobreviviente"]:
                    items.append({"title": "El sobreviviente", "tmdb_path": "movie/798645-the-running-man"})
                elif clean == "Miedo":
                    items.append({"title": "Miedo", "tmdb_path": "movie/880100-fear"})
                else:
                    items.append(clean)
        if items:
            return items[:10]
    except Exception as e:
        print(f"  [Tudum Error para {url}]:", e)
    return []

def get_netflix_tudum_top10():
    print("  [Scraping Netflix Tudum Argentina (10 Películas + 10 Series) en vivo...]")
    movies = fetch_tudum_titles("https://www.netflix.com/tudum/top10/es/argentina")
    series = fetch_tudum_titles("https://www.netflix.com/tudum/top10/es/argentina/tv")
    
    if movies or series:
        return movies[:10] + series[:10]
    return []

JUSTWATCH_SLUGS = {
    "Top 10 Disney+": "disney-plus",
    "Top 10 Prime Video": "amazon-prime-video",
    "Top 10 Max": "hbo-max",
    "Top 10 Apple TV+": "apple-tv-plus"
}

def fetch_justwatch_top10(category_name, provider_slug):
    url = f"https://www.justwatch.com/ar/proveedor/{provider_slug}"
    print(f"  [Scraping JustWatch Argentina en vivo para '{category_name}' ({url})...]")
    titles = []
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
        
        raw_titles = re.findall(r'<a[^>]*href="/ar/(?:pelicula|serie)/[^"]+"[^>]*>.*?alt="([^"]+)"', html, re.DOTALL)
        if not raw_titles:
            raw_titles = re.findall(r'<img[^>]*alt="([^"]+)"[^>]*class="picture-comp__img', html)
            
        for t in raw_titles:
            clean_t = t.replace('&#39;', "'").replace('&amp;', '&').strip()
            if clean_t and clean_t not in titles and clean_t != 'JustWatch':
                # Special disambiguation overrides
                if category_name == "Top 10 Disney+" and clean_t == "Furia":
                    titles.append({"title": "Furia", "tmdb_path": "tv/287238-furious"})
                elif clean_t in ["El oso", "El Oso", "The Bear"]:
                    titles.append({"title": "El oso", "tmdb_path": "tv/136315-the-bear"})
                elif clean_t == "Oppenheimer":
                    titles.append({"title": "Oppenheimer", "tmdb_path": "movie/872585-oppenheimer"})
                elif clean_t in ["Cabo de miedo", "Cabo de Miedo"]:
                    titles.append({"title": "Cabo de miedo", "tmdb_path": "tv/277439-cape-fear"})
                elif clean_t in ["Eternidad", "Eternity"]:
                    titles.append({"title": "Eternidad", "tmdb_path": "movie/1259102-eternity"})
                elif clean_t == "Avatar: Fuego y ceniza":
                    titles.append({"title": "Avatar: Fuego y ceniza", "tmdb_path": "movie/83533-avatar-fire-and-ash"})
                elif "Rocky" in clean_t:
                    titles.append({"title": "The Rocky Horror Picture Show", "tmdb_path": "movie/36685-the-rocky-horror-picture-show"})
                else:
                    titles.append(clean_t)
            if len(titles) >= 10:
                break
    except Exception as e:
        print(f"  [JustWatch Error para {provider_slug}]:", e)
    return titles

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

def get_gemini_metadata(title):
    api_key = load_gemini_api_key()
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
        if title == "Oppenheimer":
            tmdb_path = "movie/872585-oppenheimer"
        elif title == "Atormentado":
            tmdb_path = "movie/64720-take-shelter"
        elif title == "Contrato para matar":
            tmdb_path = "movie/945937-fast-charlie"
        elif title in ["El sobreviviente", "El Sobreviviente"]:
            tmdb_path = "movie/798645-the-running-man"
        elif title == "Miedo":
            tmdb_path = "movie/880100-fear"
        elif title in ["Cabo de miedo", "Cabo de Miedo"]:
            tmdb_path = "tv/277439-cape-fear"
        elif title in ["Eternidad", "Eternity"]:
            tmdb_path = "movie/1259102-eternity"

    poster_url = None
    backdrop_url = None
    overview = None
    year = "2025"
    cur_media_type = "PELÍCULA"
    cur_extra_info = "1h 48m"
    latest_d_html = None
    
    search_query = title.replace("El Pengüino", "El Pingüino")

    try:
        if tmdb_path:
            paths_to_try = [tmdb_path]
        else:
            encoded_title = urllib.parse.quote(search_query)
            url = f"https://www.themoviedb.org/search?query={encoded_title}&language=es-ES"
            req = urllib.request.Request(url, headers=HEADERS)
            html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
            
            matches = re.findall(r'href="/(movie|tv)/(\d+[^"]*)"', html)
            if not matches:
                clean_t = re.sub(r'[^\w\s]', '', search_query)
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
        # Si TMDB no devolvió datos completos, intentar valores de rescate razonables en vez de fallar
        poster_url = poster_url or "https://image.tmdb.org/t/p/w500/tzMTmzIslvpnXG2ifAl9ZAnlIdx.jpg"
        backdrop_url = backdrop_url or poster_url
        overview = overview or f"Disfruta de {title} en la plataforma."

    if cur_media_type == "SERIE":
        cur_extra_info = parse_tv_extra_info(latest_d_html, gem.get("extra_info") if gem else None)
    else:
        cur_extra_info = "1h 48m"

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

        m_len = re.search(r'"lengthSeconds":"(\d+)"', html)
        m_dur = re.search(r'"approxDurationMs":"(\d+)"', html)
        duration_sec = 0
        if m_len:
            duration_sec = int(m_len.group(1))
        elif m_dur:
            duration_sec = int(m_dur.group(1)) // 1000

        if duration_sec > 0 and (duration_sec < 30 or duration_sec > 900):
            return False

        return True
    except Exception:
        return False

def get_youtube_trailer_id(item):
    title = item["title"] if isinstance(item, dict) else item
    if title in ["Furioso", "Furioso: Temporada 1"]:
        return "ExwpmKH9pKA"
        
    query = f"{title} netflix 2026 trailer espanol latino" if "Furioso" in title else f"{title} trailer oficial espanol latino"
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        html = urllib.request.urlopen(req).read().decode('utf-8')
        vids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
        for vid in vids[:8]:
            if is_youtube_video_playable(vid):
                return vid
    except Exception as e:
        print(f"  [YT Error para '{title}']:", e)
    return "cAHSi8AXbCE"

def run_weekly_update(gemini_api_key=None, push_to_git=False):
    print("=== INICIANDO ACTUALIZACIÓN SEMANAL DE CATÁLOGO Y GÉNEROS (SIN TERROR) ===")
    
    json_path = 'app/src/main/assets/trailers.json'
    if not os.path.exists(json_path):
        json_path = os.path.join(os.path.dirname(__file__), '../app/src/main/assets/trailers.json')

    # Preservar primero la categoría Últimos fondos de tu TV si existe
    reddit_category = None
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            catalog = json.load(f)
            for row in catalog.get('rows', []):
                if row.get('category') in [
                    "Últimos fondos de tu TV",
                    "Últimos Fondos (r/IMDB_esp)",
                    "Recomendaciones del día",
                    "Fondos del Día (Reddit r/IMDB_esp)"
                ]:
                    row["category"] = "Últimos fondos de tu TV"
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
        if cat_name == "Top 10 Netflix":
            tudum_titles = get_netflix_tudum_top10()
            if tudum_titles:
                titles = tudum_titles
        elif cat_name in JUSTWATCH_SLUGS:
            slug = JUSTWATCH_SLUGS[cat_name]
            jw_titles = fetch_justwatch_top10(cat_name, slug)
            if jw_titles:
                titles = jw_titles
        elif gemini_api_key and "Top 10:" in cat_name:
            titles = query_gemini_recommendations(gemini_api_key, cat_name)
            
        if not titles:
            titles = default_titles

        items = []
        for t in titles:
            print(f"  Enriqueciendo con TMDB & YouTube: '{t}'...")
            tmdb = get_tmdb_info(t)
            if not tmdb:
                print(f"  [AVISO] No se pudo obtener información para '{t}', omitiendo...")
                continue
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
    g_key = load_gemini_api_key()
    for arg in args:
        if arg.startswith("--gemini-key="):
            g_key = arg.split("=", 1)[1]
    run_weekly_update(gemini_api_key=g_key, push_to_git=do_push)
