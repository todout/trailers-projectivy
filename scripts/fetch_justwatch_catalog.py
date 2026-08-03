import urllib.request
import urllib.parse
import json
import re
import time
import sys

# Ensure utf-8 stdout encoding on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8'
}

platform_data = {
    "Top 10 Disney+": {
        "provider": "Disney+",
        "movies": [
            "El diablo viste a la moda 2", "El diario de la princesa", "Furia",
            "Avatar: Fuego y ceniza", "Hoppers: Operación castor", "Soy Luna: Volver a rodar",
            "El diablo viste a la moda", "Descendientes: Un malvado País de las Maravillas",
            "Boda sangrienta 2", "Avengers: Endgame"
        ],
        "shows": [
            "Los Simpson", "Malcolm en el medio", "Grey's Anatomy", "Modern Family",
            "Criminal Minds", "Futurama", "Family Guy", "Lost", "Shōgun", "El encargado"
        ]
    },
    "Top 10 Prime Video": {
        "provider": "Prime Video",
        "movies": [
            "Amos del Universo", "Nunca debimos entrar", "Proyecto Fin del Mundo",
            "Spider-Man: Sin camino a casa", "Spider-Man 2: Lejos de Casa", "El Guardián: Último Refugio",
            "El Sorprendente Hombre-Araña", "La guerra de los mundos",
            "El Sorprendente Hombre-Araña 2: La Amenaza de Electro", "Spider-Man: Un nuevo universo"
        ],
        "shows": [
            "La casa del dragón", "Silo", "Te encontraré", "La maldición de Widow's Bay",
            "Furia", "El mentalista", "Lucky", "From", "El oso", "Stuart Fails to Save the Universe"
        ]
    },
    "Top 10 Apple TV+": {
        "provider": "Apple TV+",
        "movies": [
            "The Dink: Pasión por el pickleball", "F1 la película", "El abismo secreto",
            "Snoopy presenta: Hogar, dulce hogar", "Eternidad", "La fuente de la juventud",
            "Los asesinos de la luna", "Napoleón", "Plan familiar", "Plan familiar 2"
        ],
        "shows": [
            "Silo", "Separación", "Ted Lasso", "The Morning Show", "Fundación",
            "Para toda la humanidad", "Terapia sin filtro", "Monarch: El legado de los monstruos",
            "Secuestro en el aire", "Presunto inocente"
        ]
    },
    "Top 10 Max": {
        "provider": "Max",
        "movies": [
            "El diablo viste a la moda 2", "Boda sangrienta 2", "Duna: Parte dos",
            "Batman", "El Club de la Pelea", "Guasón 2: Folie à Deux",
            "El señor de los anillos: La comunidad del anillo", "Interestelar",
            "Oppenheimer", "Barbie"
        ],
        "shows": [
            "La casa del dragón", "El Pengüino", "Juego de tronos", "The Last of Us",
            "Succession", "The White Lotus", "True Detective", "Euphoria",
            "Los Soprano", "Rick y Morty"
        ]
    }
}

enriched_cache = {}

def get_tmdb_info(title, provider="", media_type="PELÍCULA"):
    # Include provider in search query if specified to disambiguate identical titles
    search_term = f"{title} {provider}".strip() if provider else title
    encoded_title = urllib.parse.quote(search_term)
    url = f"https://www.themoviedb.org/search?query={encoded_title}"
    
    poster_url = None
    backdrop_url = None
    overview = None
    year = "2026"
    extra_info = "1h 48m" if media_type == "PELÍCULA" else "1 Temporada"
    
    try:
        req = urllib.request.Request(url, headers=headers)
        html = urllib.request.urlopen(req).read().decode('utf-8')
        
        match = re.search(r'href="/(movie|tv)/(\d+)[^"]*"', html)
        if not match and provider: # Fallback to search without provider
            url_fallback = f"https://www.themoviedb.org/search?query={urllib.parse.quote(title)}"
            req_fb = urllib.request.Request(url_fallback, headers=headers)
            html = urllib.request.urlopen(req_fb).read().decode('utf-8')
            match = re.search(r'href="/(movie|tv)/(\d+)[^"]*"', html)

        if match:
            m_type, tmdb_id = match.groups()
            detail_url = f"https://www.themoviedb.org/{m_type}/{tmdb_id}?language=es-MX"
            d_req = urllib.request.Request(detail_url, headers=headers)
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
        print(f"  [TMDB Error for '{title}']:", e)

    if not poster_url:
        poster_url = "https://image.tmdb.org/t/p/w500/gp31EwMH5D2bftOjscwkgTmoLAB.jpg"
    if not backdrop_url:
        backdrop_url = poster_url
    if not overview:
        overview = f"Sigue la historia y los eventos de {title}."
        
    subtitle = f"{media_type} • {year} • {extra_info}"
    return {
        "poster_url": poster_url,
        "backdrop_url": backdrop_url,
        "overview": overview,
        "year": year,
        "extra_info": extra_info,
        "subtitle": subtitle
    }

def get_youtube_trailer_id(title, provider=""):
    query = f"{title} {provider} trailer oficial español".strip()
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
    try:
        req = urllib.request.Request(url, headers=headers)
        html = urllib.request.urlopen(req).read().decode('utf-8')
        vids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
        if vids:
            return vids[0]
    except Exception as e:
        print(f"  [YT Error for '{title}']:", e)
    return "cAHSi8AXbCE"

def build_enriched_item(title, provider, media_type):
    key = (title.lower().strip(), provider.lower().strip(), media_type)
    if key in enriched_cache:
        return enriched_cache[key]
    
    print(f"Enriching {media_type} ({provider}): '{title}'...")
    tmdb_info = get_tmdb_info(title, provider, media_type)
    yt_id = get_youtube_trailer_id(title, provider)
    time.sleep(0.2)
    
    item = {
        "title": title,
        "provider": provider,
        "subtitle": tmdb_info["subtitle"],
        "media_type": media_type,
        "year": tmdb_info["year"],
        "extra_info": tmdb_info["extra_info"],
        "poster_url": tmdb_info["poster_url"],
        "backdrop_url": tmdb_info["backdrop_url"],
        "overview": tmdb_info["overview"],
        "youtube_id": yt_id,
        "trailer_url": f"https://www.youtube.com/watch?v={yt_id}"
    }
    enriched_cache[key] = item
    return item

def run():
    print("Starting JustWatch Catalog & Disambiguated TMDB/YouTube Enrichment...")
    try:
        with open('app/src/main/assets/trailers.json', 'r', encoding='utf-8') as f:
            existing_catalog = json.load(f)
    except Exception as e:
        print("Error reading trailers.json:", e)
        existing_catalog = {"rows": []}

    new_catalog_rows = []

    # Preserve Recomendaciones y Top 10 Netflix
    for row in existing_catalog.get('rows', []):
        cat = row.get('category')
        if cat in ["Recomendaciones para vos", "Top 10 Netflix"]:
            new_catalog_rows.append(row)

    for cat_name, content in platform_data.items():
        print(f"\n--- Building {cat_name} ---")
        provider_name = content.get("provider", "")
        items = []
        
        # 10 movies
        for title in content["movies"]:
            items.append(build_enriched_item(title, provider_name, "PELÍCULA"))
            
        # 10 shows
        for title in content["shows"]:
            items.append(build_enriched_item(title, provider_name, "SERIE"))
            
        new_catalog_rows.append({
            "category": cat_name,
            "items": items
        })

    updated_catalog = {"rows": new_catalog_rows}
    with open('app/src/main/assets/trailers.json', 'w', encoding='utf-8') as f:
        json.dump(updated_catalog, f, ensure_ascii=False, indent=2)

    print("\n[SUCCESS] Successfully generated disambiguated enriched catalog in trailers.json!")

if __name__ == '__main__':
    run()
