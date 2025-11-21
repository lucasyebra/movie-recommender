import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.preprocessing import MoviePreprocessor

class MovieRecommender:
    """
    Clase que entrena el modelo y genera recomendaciones.
    """
    
    def __init__(self):
        # Inicializamos el preprocesador para obtener los datos
        self.preprocessor = MoviePreprocessor()
        self.df = pd.DataFrame()
        self.similarity_matrix = None
        
    def fit(self):
        """
        Entrena el modelo:
        1. Carga y limpia datos.
        2. Convierte texto a números (TF-IDF).
        3. Calcula la matriz de similitud.
        """
        print("Cargando datos y preprocesando...")
        self.df = self.preprocessor.prepare_data()
        
        if self.df.empty:
            print("Error: No hay datos para entrenar.")
            return

        print("Entrenando modelo TF-IDF... (Esto puede tardar un poco)")
        # TF-IDF: Convierte texto a matriz numérica
        # stop_words='english': Elimina palabras comunes en inglés (the, a, and)
        tfidf = TfidfVectorizer(stop_words='english')
        
        # Aprendemos el vocabulario y transformamos la "sopa" en números
        tfidf_matrix = tfidf.fit_transform(self.df['combined_features'])
        
        print("Calculando similitud del coseno...")
        # Crea una tabla gigante comparando TODAS contra TODAS
        self.similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
        print("¡Modelo entrenado con éxito!")

    def recommend(self, movie_title, top_n=10):
        """
        Recomienda películas similares dado un título.
        """
        # 1. Normalizamos el título buscado (minúsculas) para evitar errores
        movie_title = movie_title.lower()
        
        # 2. Buscamos si la película existe en nuestra base de datos
        # Creamos una serie donde el índice es el título (para buscar rápido)
        indices = pd.Series(self.df.index, index=self.df['title'].str.lower()).drop_duplicates()
        
        if movie_title not in indices:
            return f"La película '{movie_title}' no se encuentra en la base de datos."

        # 3. Obtenemos el índice numérico de la película (ej: Toy Story es la fila 0)
        idx = indices[movie_title]

        # 4. Obtenemos los puntajes de similitud de esa película con todas las demás
        sim_scores = list(enumerate(self.similarity_matrix[idx]))

        # 5. Ordenamos de mayor a menor similitud
        # x[1] es el puntaje. Reverse=True para que los altos vayan primero.
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # 6. Tomamos los top_n (ignoramos el 0 porque es la misma película)
        sim_scores = sim_scores[1:top_n+1]

        # 7. Obtenemos los índices de las películas ganadoras
        movie_indices = [i[0] for i in sim_scores]

        # 8. Devolvemos los títulos y posters
        return self.df[['id','title', 'poster_path','overview']].iloc[movie_indices]

# Bloque de prueba
if __name__ == "__main__":
    model = MovieRecommender()
    model.fit()
    
    # Prueba manual: Cambia "Toy Story" por otra si quieres probar
    pelicula_prueba = "Toy Story" 
    print(f"\n--- Recomendaciones para: {pelicula_prueba} ---")
    recomendaciones = model.recommend(pelicula_prueba)
    print(recomendaciones)