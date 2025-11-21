import os
import requests
import pandas as pd
import sqlite3
from dotenv import load_dotenv

# Cargar variables de entorno (API Key)
load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

def obtener_peliculas_tmdb(total_peliculas=5000):
    """
    Descarga películas de la API de TMDB.
    
    Args:
        total_peliculas (int): Número aproximado de películas a descargar.
    
    Returns:
        pd.DataFrame: DataFrame con los datos de las películas.
    """
    if not API_KEY:
        raise ValueError("No se encontró la API KEY. Revisa tu archivo .env")

    movies_data = []
    page = 1
    peliculas_por_pagina = 20 # TMDB da 20 por página
    total_paginas = total_peliculas // peliculas_por_pagina

    print(f"Iniciando descarga de {total_peliculas} películas...")

    while page <= total_paginas:
        # URL para obtener películas "Top Rated"
        url = f"https://api.themoviedb.org/3/movie/top_rated?api_key={API_KEY}&language=en-US&page={page}"
        
        try:
            response = requests.get(url)
            response.raise_for_status() # Lanza error si la conexión falla
            data = response.json()
            results = data.get('results', [])

            for movie in results:
                # Extraemos solo lo que nos interesa
                movies_data.append({
                    'id': movie.get('id'),
                    'title': movie.get('title'),
                    'overview': movie.get('overview'),
                    'genre_ids': str(movie.get('genre_ids')), # Convertimos lista a string para guardar en SQLite
                    'release_date': movie.get('release_date'),
                    'vote_average': movie.get('vote_average'),
                    'poster_path': movie.get('poster_path')
                })
            
            # Mostrar progreso cada 10 páginas
            if page % 10 == 0:
                print(f"Descargadas {len(movies_data)} películas (Página {page}/{total_paginas})")
            
            page += 1
            
        except requests.exceptions.RequestException as e:
            print(f"Error en la página {page}: {e}")
            break

    return pd.DataFrame(movies_data)

def guardar_en_sqlite(df, db_path="data/movies.db"):
    """Guarda el DataFrame en una base de datos SQLite."""
    try:
        conn = sqlite3.connect(db_path)
        df.to_sql("movies", conn, if_exists="replace", index=False)
        conn.close()
        print(f"Exito! {len(df)} películas guardadas en '{db_path}'")
    except Exception as e:
        print(f"Error al guardar en la base de datos: {e}")

if __name__ == "__main__":
    # Ejecución del script
    print("--- COMENZANDO PROCESO ETL ---")
    
    # 1. Extracción
    df_movies = obtener_peliculas_tmdb(total_peliculas=5000)
    
    # 2. Carga (Guardado)
    if not df_movies.empty:
        guardar_en_sqlite(df_movies)
    else:
        print("No se obtuvieron datos.")