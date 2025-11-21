import streamlit as st
import sys
import os

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="MovieMatch Pro",
    page_icon="🍿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. ESTILOS CSS ---
st.markdown("""
    <style>
    * { box-sizing: border-box; }
    
    .stApp {
        background-color: #141414;
        color: #ffffff;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    h1 {
        color: #E50914;
        text-transform: uppercase;
        font-weight: 900;
        text-align: center;
        font-size: 3rem;
        margin-bottom: 20px;
    }
    
    /* Buscador */
    .stSelectbox label { color: #e5e5e5 !important; }
    div[data-baseweb="select"] > div {
        background-color: #333;
        border: 1px solid #444;
        color: white;
    }
    
    /* Botón */
    .stButton > button {
        width: 100%;
        background-color: #E50914;
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.8rem;
        border-radius: 4px;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background-color: #ff0f1f;
    }

    /* --- TARJETA --- */
    .movie-card {
        position: relative;
        width: 100%;
        aspect-ratio: 2/3;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        transition: transform 0.3s ease;
        margin-bottom: 20px;
        background-color: #000;
    }
    
    .movie-card:hover {
        transform: scale(1.03);
        z-index: 10;
        box-shadow: 0 10px 25px rgba(0,0,0,0.8);
    }

    .movie-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }

    /* --- OVERLAY --- */
    .movie-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.90);
        opacity: 0;
        transition: opacity 0.3s ease;
        padding: 20px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .movie-card:hover .movie-overlay {
        opacity: 1;
    }

    /* Header: Título y Match */
    .overlay-header {
        width: 100%;
        border-bottom: 1px solid rgba(255,255,255,0.2);
        padding-bottom: 10px;
        margin-bottom: 10px;
    }

    .overlay-title {
        color: white;
        font-size: 16px;
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 5px;
    }

    .overlay-match {
        color: #46d369;
        font-size: 14px;
        font-weight: bold;
    }

    /* Body: Descripción */
    .overlay-body {
        flex-grow: 1;
        display: flex;
        align-items: center;
        overflow: hidden;
    }

    .overlay-desc {
        color: #cccccc;
        font-size: 13px;
        line-height: 1.4;
        display: -webkit-box;
        -webkit-line-clamp: 12; /* Muestra hasta 12 líneas */
        -webkit-box-orient: vertical;
        overflow: hidden;
    }

    /* Footer: Botón */
    .tmdb-btn {
        display: block;
        width: 100%;
        text-align: center;
        background-color: transparent;
        border: 1px solid #E50914;
        color: #E50914;
        text-decoration: none;
        padding: 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        transition: 0.2s;
        margin-top: 10px;
    }
    
    .tmdb-btn:hover {
        background-color: #E50914;
        color: white;
        text-decoration: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. BACKEND ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from src.model import MovieRecommender
except ModuleNotFoundError:
    st.error("⚠️ Error crítico: No se encuentra la carpeta 'src'.")
    st.stop()

@st.cache_resource
def cargar_modelo():
    model = MovieRecommender()
    if not os.path.exists(model.preprocessor.db_path):
        return None
    model.fit()
    return model

# --- 4. INTERFAZ ---

st.markdown("<h1>MOVIEMATCH</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #b3b3b3;'>TU IA DE CINE</p>", unsafe_allow_html=True)
st.write("")

with st.spinner('Iniciando motores...'):
    recommender = cargar_modelo()

if not recommender:
    st.error("❌ Base de datos no encontrada.")
    st.stop()

# Buscador
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    pelicula_input = st.selectbox(
        "Buscar película:",
        recommender.df['title'].values,
        index=None,
        placeholder="Escribe un título..."
    )
    btn_buscar = st.button("GENERAR RECOMENDACIONES")

# --- FUNCIÓN DE RENDERIZADO (CORREGIDA) ---
def renderizar_fila(datos, indice_inicio):
    cols = st.columns(5)
    
    for idx, (col, row) in enumerate(zip(cols, datos.iterrows())):
        pelicula = row[1]
        
        poster = f"https://image.tmdb.org/t/p/w500{pelicula['poster_path']}" if pelicula['poster_path'] else "https://via.placeholder.com/500x750"
        url_tmdb = f"https://www.themoviedb.org/movie/{pelicula['id']}"
        
        # Descripción larga
        desc = pelicula.get('overview', 'Sin descripción.')
        if len(desc) > 350:
            desc = desc[:350] + "..."
            
        match = 98 - (indice_inicio + idx) * 2
        
        # HTML SIN INDENTACIÓN PARA EVITAR ERRORES
        # Nota: Todo el HTML está pegado a la izquierda para que Streamlit no lo confunda con código.
        html_card = f"""
<div class="movie-card">
<img src="{poster}" class="movie-img">
<div class="movie-overlay">
<div class="overlay-header">
<div class="overlay-title">{pelicula['title']}</div>
<div class="overlay-match">{match}% Match</div>
</div>
<div class="overlay-body">
<div class="overlay-desc">{desc}</div>
</div>
<a href="{url_tmdb}" target="_blank" class="tmdb-btn">Ver en TMDB ↗</a>
</div>
</div>"""
        
        with col:
            st.markdown(html_card, unsafe_allow_html=True)

# --- 5. RESULTADOS ---
if btn_buscar and pelicula_input:
    st.divider()
    try:
        resultados = recommender.recommend(pelicula_input, top_n=10)
        
        st.markdown(f"### 🍿 Porque viste **{pelicula_input}**:")
        st.write("")
        
        renderizar_fila(resultados.iloc[:5], 0)
        st.write("") 
        st.write("") 
        renderizar_fila(resultados.iloc[5:], 5)
        
    except Exception as e:
        st.error(f"Error: {e}")

elif not pelicula_input and btn_buscar:
    st.warning("⚠️ Selecciona una película.")

st.write("<br><br>", unsafe_allow_html=True)