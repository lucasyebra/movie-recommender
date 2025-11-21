import sqlite3
import pandas as pd
import re # patrones en texto

class MoviePreprocessor:
    """
    Clase encargada de cargar, limpiar y preparar los datos para el modelo.
    """
    
    def __init__(self, db_path="data/movies.db"):
        # Guardamos la ruta de la base de datos para usarla luego
        self.db_path = db_path

    def load_data(self):
        """Paso 1: Lee los datos crudos desde SQLite."""
        try:
            conn = sqlite3.connect(self.db_path)
            # Traemos solo lo necesario. No necesitamos la fecha ni el promedio de votos para el TEXTO.
            query = "SELECT id, title, overview, genre_ids, poster_path FROM movies"
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error al cargar datos: {e}")
            return pd.DataFrame()

    def _clean_text(self, text):
        """
        Paso 2: Limpia una frase individual.
        """
        if not isinstance(text, str):
            return ""
        
        # Convertir a minúsculas
        text = text.lower()
        # Quitar caracteres raros (dejamos solo letras a-z, números 0-9 y espacios)
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        return text

    def prepare_data(self):
        """
        Paso 3 (Principal): Orquestador que une todo.
        """
        df = self.load_data()
        
        if df.empty:
            print("No hay datos.")
            return pd.DataFrame()
        
        # 1. Rellenar nulos para que no explote al sumar
        df['overview'] = df['overview'].fillna('')
        df['genre_ids'] = df['genre_ids'].fillna('')

        # 2. Feature Engineering
        # Sumamos: Título + Espacio + Resumen + Espacio + Géneros
        df['combined_features'] = (
            df['title'] + " " + 
            df['overview'] + " " + 
            df['genre_ids']
        )

        # 3. Limpiar el texto resultante
        df['combined_features'] = df['combined_features'].apply(self._clean_text)
        
        print("Datos listos y limpios.")
        return df

# Esto permite probar el archivo ejecutándolo directamente
if __name__ == "__main__":
    preprocessor = MoviePreprocessor()
    df = preprocessor.prepare_data()
    
    # Mostramos un ejemplo para verificar
    print("\n--- EJEMPLO DE 'SOPA' DE DATOS ---")
    print(df['combined_features'].iloc[0])