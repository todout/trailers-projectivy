import urllib.request
import re
import json
import time
import sys
from bs4 import BeautifulSoup

# Ensure utf-8 stdout encoding on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Headers with browser User-Agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8'
}

platforms = [
    {"name": "Top 10 Disney+", "code": "dnp"},
    {"name": "Top 10 Prime Video", "code": "amp"},
    {"name": "Top 10 Apple TV+", "code": "apt"},
    {"name": "Top 10 Max", "code": "hbo"},
]

def load_existing_catalog():
    try:
        with open('app/src/main/assets/trailers.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print("Warning loading trailers.json:", e)
        return {"rows": []}

existing_catalog = load_existing_catalog()

# Build database of existing items by title to preserve metadata
existing_items_db = {}
for row in existing_catalog.get('rows', []):
    for item in row.get('items', []):
        t_clean = item['title'].lower().strip()
        existing_items_db[t_clean] = item

def fetch_titles_from_jw(url):
    req = urllib.request.Request(url, headers=headers)
    html = urllib.request.urlopen(req).read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    
    titles_found = []
    ignore_keywords = [
        'disney', 'prime', 'apple', 'movistar', 'claro', 'hbo', 'netflix',
        'universal', 'justwatch', 'paramount', 'vix', 'mgm', 'logo'
    ]
    
    for img in soup.find_all('img'):
        alt = img.get('alt', '').strip()
        if alt and not any(k in alt.lower() for k in ignore_keywords):
            if alt not in titles_found:
                titles_found.append(alt)
    return titles_found[:10]

new_catalog_rows = []

# Retain Recomendaciones y Netflix (proveniente de Tudum)
for row in existing_catalog.get('rows', []):
    cat = row.get('category')
    if cat in ["Recomendaciones para vos", "Top 10 Netflix"]:
        new_catalog_rows.append(row)

print("Starting JustWatch Trends Fetcher...")

for p in platforms:
    cat_name = p["name"]
    code = p["code"]
    print(f"\n[+] Fetching trends for {cat_name} (provider: {code})...")
    
    # 1. Fetch Movies
    m_url = f"https://www.justwatch.com/ar/streaming-charts?providers={code}&ct=weekly"
    m_titles = fetch_titles_from_jw(m_url)
    print(f"  - Movies Top 10 ({len(m_titles)}): {m_titles}")
    time.sleep(1.5)  # Rate limiting delay
    
    # 2. Fetch Shows
    s_url = f"https://www.justwatch.com/ar/streaming-charts?providers={code}&ct=weekly&t=shows"
    s_titles = fetch_titles_from_jw(s_url)
    print(f"  - Shows Top 10 ({len(s_titles)}): {s_titles}")
    time.sleep(1.5)  # Rate limiting delay
    
    platform_items = []
    
    # Process Movies
    for t in m_titles:
        t_clean = t.lower().strip()
        if t_clean in existing_items_db:
            item = dict(existing_items_db[t_clean])
            item['media_type'] = 'PELÍCULA'
            platform_items.append(item)
        else:
            item = {
                "title": t,
                "subtitle": "PELÍCULA • 2026 • 1h 50m",
                "media_type": "PELÍCULA",
                "year": "2026",
                "extra_info": "1h 50m",
                "poster_url": "https://image.tmdb.org/t/p/w500/tzMTmzIslvpnXG2ifAl9ZAnlIdx.jpg",
                "backdrop_url": "https://image.tmdb.org/t/p/w500/aQFeADnhJimn635owevcpwyaUAG.jpg",
                "overview": f"{t} está dentro de las películas más vistas de la semana en la plataforma.",
                "youtube_id": "cAHSi8AXbCE",
                "trailer_url": "https://www.youtube.com/watch?v=cAHSi8AXbCE"
            }
            platform_items.append(item)
            
    # Process Shows
    for t in s_titles:
        t_clean = t.lower().strip()
        if t_clean in existing_items_db:
            item = dict(existing_items_db[t_clean])
            item['media_type'] = 'SERIE'
            platform_items.append(item)
        else:
            item = {
                "title": t,
                "subtitle": "SERIE • 2026 • 1 Temporada",
                "media_type": "SERIE",
                "year": "2026",
                "extra_info": "1 Temporada",
                "poster_url": "https://image.tmdb.org/t/p/w500/4uh8mjAwKOpTrlu4nldsBf0ZOuU.jpg",
                "backdrop_url": "https://image.tmdb.org/t/p/w500/tMpfa73LmKpeZ3Fix1QmFGIUrKI.jpg",
                "overview": f"{t} se ubica entre las series tendencia de la semana.",
                "youtube_id": "75HtV3HxLRs",
                "trailer_url": "https://www.youtube.com/watch?v=75HtV3HxLRs"
            }
            platform_items.append(item)
            
    new_catalog_rows.append({
        "category": cat_name,
        "items": platform_items
    })

# Save updated trailers.json
updated_catalog = {"rows": new_catalog_rows}
with open('app/src/main/assets/trailers.json', 'w', encoding='utf-8') as f:
    json.dump(updated_catalog, f, ensure_ascii=False, indent=2)

print("\n[SUCCESS] Successfully updated trailers.json with JustWatch weekly trends!")
