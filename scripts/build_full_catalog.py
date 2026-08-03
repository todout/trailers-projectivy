import json

# Full dataset for Netflix Top 10 (10 Movies + 10 Series from Tudum Argentina)
netflix_tudum_items = [
    # 10 Movies
    {
        "title": "No soy quien crees",
        "subtitle": "PELÍCULA • 2026 • 1h 48m",
        "media_type": "PELÍCULA",
        "year": "2026",
        "extra_info": "1h 48m",
        "poster_url": "https://image.tmdb.org/t/p/w500/tzMTmzIslvpnXG2ifAl9ZAnlIdx.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w500/aQFeADnhJimn635owevcpwyaUAG.jpg",
        "overview": "Una mujer atrapada en un juego de identidades falsas descubre un secreto peligroso que cambia su vida.",
        "youtube_id": "cAHSi8AXbCE",
        "trailer_url": "https://www.youtube.com/watch?v=cAHSi8AXbCE"
    },
    {
        "title": "Pesadilla en la cocina",
        "subtitle": "PELÍCULA • 2026 • 1h 35m",
        "media_type": "PELÍCULA",
        "year": "2026",
        "extra_info": "1h 35m",
        "poster_url": "https://image.tmdb.org/t/p/w500/pKHqhghLmDRfwIyH7A2pGARX1IQ.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w500/dk68ykaNd3HdrDJyPJqEGsgvag7.jpg",
        "overview": "Un prestigioso restaurante se convierte en el escenario de una noche caótica cuando oscuros secretos salen a la luz.",
        "youtube_id": "NRLPZ5Bj5VQ",
        "trailer_url": "https://www.youtube.com/watch?v=NRLPZ5Bj5VQ"
    },
    {
        "title": "Deseo",
        "subtitle": "PELÍCULA • 2026 • 1h 37m",
        "media_type": "PELÍCULA",
        "year": "2026",
        "extra_info": "1h 37m",
        "poster_url": "https://image.tmdb.org/t/p/w500/5lJPvf7cJ2r2EiNrnvBVYpusKFM.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w500/oBter8Y5p2ZFUwWgQ1T9pulGFTJ.jpg",
        "overview": "Sigue a Lucero, una exitosa abogada con una vida aparentemente perfecta que oculta un profundo vacío.",
        "youtube_id": "bA7D6wx_Vy4",
        "trailer_url": "https://www.youtube.com/watch?v=bA7D6wx_Vy4"
    },
    {
        "title": "El cobrador de deudas",
        "subtitle": "PELÍCULA • 2026 • 2h 14m",
        "media_type": "PELÍCULA",
        "year": "2026",
        "extra_info": "2h 14m",
        "poster_url": "https://image.tmdb.org/t/p/w500/pKHqhghLmDRfwIyH7A2pGARX1IQ.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w500/dk68ykaNd3HdrDJyPJqEGsgvag7.jpg",
        "overview": "La trama sigue a un excobrador con una enfermedad terminal que regresa al hampa para proteger a las víctimas de una red de usura.",
        "youtube_id": "NRLPZ5Bj5VQ",
        "trailer_url": "https://www.youtube.com/watch?v=NRLPZ5Bj5VQ"
    },
    {
        "title": "Culpa mía",
        "subtitle": "PELÍCULA • 2023 • 1h 56m",
        "media_type": "PELÍCULA",
        "year": "2023",
        "extra_info": "1h 56m",
        "poster_url": "https://image.tmdb.org/t/p/w500/gp31EwMH5D2bftOjscwkgTmoLAB.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w500/oz4U9eA6ilYf1tyiVuGmkftdLac.jpg",
        "overview": "Noah debe dejar su ciudad, novio y amigos para mudarse a la mansión del nuevo marido de su madre.",
        "youtube_id": "1SqMjrE0J6E",
        "trailer_url": "https://www.youtube.com/watch?v=1SqMjrE0J6E"
    },
    {
        "title": "La extorsión",
        "subtitle": "PELÍCULA • 2023 • 1h 46m",
        "media_type": "PELÍCULA",
        "year": "2023",
        "extra_info": "1h 46m",
        "poster_url": "https://image.tmdb.org/t/p/w500/pUvs1iFFMDy3sNp5dNmkRak1oxD.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w500/2kQ71k6dq7DVNYuYY9ylNvRFKTv.jpg",
        "overview": "Un experimentado piloto comercial es chantajeado por los servicios de inteligencia de su país para llevar valijas sospechosas.",
        "youtube_id": "svGU1Mq5irI",
        "trailer_url": "https://www.youtube.com/watch?v=svGU1Mq5irI"
    },
    {
        "title": "Misión de rescate 2",
        "subtitle": "PELÍCULA • 2023 • 2h 3m",
        "media_type": "PELÍCULA",
        "year": "2023",
        "extra_info": "2h 3m",
        "poster_url": "https://image.tmdb.org/t/p/w500/7nAVXGHHtaNcdsqvDXmY6R9N0fG.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w500/guYWtcg2FXkRHvlUg7VKz4srO3.jpg",
        "overview": "El agente altamente entrenado Tyler Rake regresa para otra misión mortal de rescate de alto riesgo.",
        "youtube_id": "3WoEPRpdTIU",
        "trailer_url": "https://www.youtube.com/watch?v=3WoEPRpdTIU"
    },
    {
        "title": "72 horas",
        "subtitle": "PELÍCULA • 2026 • 1h 42m",
        "media_type": "PELÍCULA",
        "year": "2026",
        "extra_info": "1h 42m",
        "poster_url": "https://image.tmdb.org/t/p/w500/uxUrEaqf7WnDj7UcEWcIE3Xo8hY.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w500/hL5EIk48251OXlbIbRJq3yaBHk8.jpg",
        "overview": "Para salvar su carrera, un ejecutivo publicitario se une a una alocada despedida de soltero en Miami.",
        "youtube_id": "KQnm6geDT2E",
        "trailer_url": "https://www.youtube.com/watch?v=KQnm6geDT2E"
    },
    {
        "title": "Spider-Man: Sin camino a casa",
        "subtitle": "PELÍCULA • 2021 • 2h 28m",
        "media_type": "PELÍCULA",
        "year": "2021",
        "extra_info": "2h 28m",
        "poster_url": "https://image.tmdb.org/t/p/w500/fBFjaDWfNslvrs6bJjknmG27wOS.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w500/qeQJx07rK2xm8SD2sJxFKhE7gs0.jpg",
        "overview": "Por primera vez en la historia cinematográfica de Spider-Man, la identidad de nuestro amigable héroe del vecindario es revelada.",
        "youtube_id": "QXibcL7-XbU",
        "trailer_url": "https://www.youtube.com/watch?v=QXibcL7-XbU"
    },
    {
        "title": "El diablo viste a la moda",
        "subtitle": "PELÍCULA • 2006 • 1h 49m",
        "media_type": "PELÍCULA",
        "year": "2006",
        "extra_info": "1h 49m",
        "poster_url": "https://image.tmdb.org/t/p/w500/ly9m3Uc947BUPe3dKu8UgWBhIXz.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w500/Af907x5h9W1wVis8XrSd7ynTWuy.jpg",
        "overview": "Una joven graduada universitaria consigue trabajo como asistente de la exigente y despiadada editora de una revista de moda.",
        "youtube_id": "O52u0imiqNY",
        "trailer_url": "https://www.youtube.com/watch?v=O52u0imiqNY"
    },

    # 10 Series
    {
        "title": "GIGN: Unidad de élite",
        "subtitle": "SERIE • 2026 • 1 Temporada",
        "media_type": "SERIE",
        "year": "2026",
        "extra_info": "1 Temporada",
        "poster_url": "https://image.tmdb.org/t/p/w500/4uh8mjAwKOpTrlu4nldsBf0ZOuU.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w500/tMpfa73LmKpeZ3Fix1QmFGIUrKI.jpg",
        "overview": "Tras un ataque sin precedentes contra su unidad, un oficial de alto rango lidera una peligrosa misión.",
        "youtube_id": "75HtV3HxLRs",
        "trailer_url": "https://www.youtube.com/watch?v=75HtV3HxLRs"
    },
    {
        "title": "El otro padre",
        "subtitle": "SERIE • 2026 • 1 Temporada",
        "media_type": "SERIE",
        "year": "2026",
        "extra_info": "1 Temporada",
        "poster_url": "https://image.tmdb.org/t/p/w500/tzMTmzIslvpnXG2ifAl9ZAnlIdx.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w500/aQFeADnhJimn635owevcpwyaUAG.jpg",
        "overview": "Una médico que busca un donante de riñón descubre una relación secreta y una prueba de ADN impactante.",
        "youtube_id": "cAHSi8AXbCE",
        "trailer_url": "https://www.youtube.com/watch?v=cAHSi8AXbCE"
    },
    {
        "title": "Engaño",
        "subtitle": "SERIE • 2024 • 1 Temporada",
        "media_type": "SERIE",
        "year": "2024",
        "extra_info": "1 Temporada",
        "poster_url": "https://image.tmdb.org/t/p/w500/a3y0aWIJdJEw7pme6Y9W0aReIN9.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w500/z8mTDyKdAWjKsD0vwa7e9LTSY1j.jpg",
        "overview": "Tras cumplir 60 años, una adinerada mujer se enamora de un atractivo joven que guarda secretos peligrosos.",
        "youtube_id": "oJXaeB7fapw",
        "trailer_url": "https://www.youtube.com/watch?v=oJXaeB7fapw"
    },
    {
        "title": "Silo",
        "subtitle": "SERIE • 2023 • 4 Temporadas",
        "media_type": "SERIE",
        "year": "2023",
        "extra_info": "4 Temporadas",
        "poster_url": "https://image.tmdb.org/t/p/w500/s4yRu8IRcMLbfoUsO4q9Yuci4F0.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w500/uTWhbLc7Bj4qNSdW3ZvZKL8cOHv.jpg",
        "overview": "En un futuro tóxico, una comunidad vive bajo tierra en un silo gigante regido por estrictas normas.",
        "youtube_id": "0I7Q1WtTf_c",
        "trailer_url": "https://www.youtube.com/watch?v=0I7Q1WtTf_c"
    },
    {
        "title": "La casa del dragón",
        "subtitle": "SERIE • 2022 • 3 Temporadas",
        "media_type": "SERIE",
        "year": "2022",
        "extra_info": "3 Temporadas",
        "poster_url": "https://image.tmdb.org/t/p/w500/szyVpg9K3LL5s8VFAGkXzlxgZUk.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w500/577eXC8wFQT0eUrJcgznSiFPRmk.jpg",
        "overview": "La historia de la Casa Targaryen ambientada 200 años antes de los eventos de Juego de Tronos.",
        "youtube_id": "BLt3K0phvX0",
        "trailer_url": "https://www.youtube.com/watch?v=BLt3K0phvX0"
    },
    {
        "title": "La ley y el orden: UVE",
        "subtitle": "SERIE • 1999 • 28 Temporadas",
        "media_type": "SERIE",
        "year": "1999",
        "extra_info": "28 Temporadas",
        "poster_url": "https://image.tmdb.org/t/p/w500/kvo558UKEhp8v3JoRGCSIx3Xxab.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w500/obtdxPgmfykYwVnvuYXC5f2xKlQ.jpg",
        "overview": "Una unidad especial de la policía de Nueva York investiga delitos complejos de carácter especial.",
        "youtube_id": "sx4n_tSzGGk",
        "trailer_url": "https://www.youtube.com/watch?v=sx4n_tSzGGk"
    },
    {
        "title": "Elize: Sombras de una Mujer",
        "subtitle": "SERIE • 2026 • 1 Temporada",
        "media_type": "SERIE",
        "year": "2026",
        "extra_info": "1 Temporada",
        "poster_url": "https://image.tmdb.org/t/p/w500/a3y0aWIJdJEw7pme6Y9W0aReIN9.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w500/z8mTDyKdAWjKsD0vwa7e9LTSY1j.jpg",
        "overview": "Una mujer descubre la infidelidad de su esposo rico y lucha por sobrellevarlo mientras la traición envenena su matrimonio.",
        "youtube_id": "oJXaeB7fapw",
        "trailer_url": "https://www.youtube.com/watch?v=oJXaeB7fapw"
    },
    {
        "title": "Merlina",
        "subtitle": "SERIE • 2022 • 2 Temporadas",
        "media_type": "SERIE",
        "year": "2022",
        "extra_info": "2 Temporadas",
        "poster_url": "https://image.tmdb.org/t/p/w500/9PFamh9xM32VFXW92mJhFi2dZz2.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w500/iHSwvRVsRyxSuBQGlISnsK9kZio.jpg",
        "overview": "Inteligente, sarcástica y un poco muerta por dentro, Merlina Addams investiga una ola de asesinatos en la Academia Nunca Más.",
        "youtube_id": "g8Hj9tN0YpM",
        "trailer_url": "https://www.youtube.com/watch?v=g8Hj9tN0YpM"
    },
    {
        "title": "La pareja perfecta",
        "subtitle": "SERIE • 2024 • 1 Temporada",
        "media_type": "SERIE",
        "year": "2024",
        "extra_info": "1 Temporada",
        "poster_url": "https://image.tmdb.org/t/p/w500/tzMTmzIslvpnXG2ifAl9ZAnlIdx.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w500/aQFeADnhJimn635owevcpwyaUAG.jpg",
        "overview": "Amelia está a punto de casarse con un miembro de una familia rica. Pero cuando aparece un cadáver en la playa, todos son sospechosos.",
        "youtube_id": "cAHSi8AXbCE",
        "trailer_url": "https://www.youtube.com/watch?v=cAHSi8AXbCE"
    },
    {
        "title": "Emily en París",
        "subtitle": "SERIE • 2020 • 4 Temporadas",
        "media_type": "SERIE",
        "year": "2020",
        "extra_info": "4 Temporadas",
        "poster_url": "https://image.tmdb.org/t/p/w500/5lJPvf7cJ2r2EiNrnvBVYpusKFM.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w500/oBter8Y5p2ZFUwWgQ1T9pulGFTJ.jpg",
        "overview": "Tras conseguir el trabajo de sus sueños en París, una ejecutiva de marketing de Chicago emprende una nueva etapa.",
        "youtube_id": "bA7D6wx_Vy4",
        "trailer_url": "https://www.youtube.com/watch?v=bA7D6wx_Vy4"
    }
]

# Read existing JSON
with open('app/src/main/assets/trailers.json', 'r', encoding='utf-8') as f:
    existing_json = json.load(f)

# Reconstruct rows
new_rows = []
for row in existing_json.get('rows', []):
    cat_name = row.get('category')
    if cat_name == "Top 10 Netflix":
        new_rows.append({
            "category": "Top 10 Netflix",
            "items": netflix_tudum_items
        })
    else:
        new_rows.append(row)

updated_json = {"rows": new_rows}

with open('app/src/main/assets/trailers.json', 'w', encoding='utf-8') as f:
    json.dump(updated_json, f, ensure_ascii=False, indent=2)

print(f"Successfully populated Top 10 Netflix with {len(netflix_tudum_items)} official items!")
