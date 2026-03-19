import streamlit as st
import pandas as pd

# --- ENLACES ---
URL_CONTENIDO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=0&single=true&output=csv"
URL_USUARIOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=83033184&single=true&output=csv"

st.set_page_config(page_title="Reto Financiero", page_icon="💰", layout="centered")

# --- DISEÑO (LETRA GRANDE Y ESTILOS) ---
st.markdown("""
    <style>
    .grande-text { font-size: 24px !important; line-height: 1.6; }
    .titulo-grande { font-size: 32px !important; font-weight: bold; color: #2E4053; }
    .stButton>button { border-radius: 20px; }
    div[data-testid="stMarkdownContainer"] p { font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=10)
def cargar_datos(url):
    df = pd.read_csv(url)
    df.columns = [str(c).strip().lower().replace(" ", "").replace("_", "") for c in df.columns]
    return df

# --- LOGIN ---
if 'autenticado' not in st.session_state:
    st.title("🛡️ Acceso al Reto")
    email_input = st.text_input("Ingresa tu correo:").lower().strip()
    if st.button("Entrar"):
        df_users = cargar_datos(URL_USUARIOS)
        user_row = df_users[df_users['email'].str.lower().str.strip() == email_input]
        if not user_row.empty:
            st.session_state.autenticado = True
            st.session_state.usuario_nombre = user_row.iloc[0]['nombrecompleto']
            st.session_state.usuario_email = email_input
            st.rerun()
        else:
            st.error("Correo no encontrado.")
else:
    # --- APP PRINCIPAL ---
    df_content = cargar_datos(URL_CONTENIDO)
    pasos = df_content[df_content['dia'] == 2].sort_values('paso')
    total = len(pasos)

    if 'indice' not in st.session_state: st.session_state.indice = 0

    fila = pasos.iloc[st.session_state.indice]

    # Contenido principal con letra grande
    st.markdown(f"<div class='titulo-grande'>{fila.get('titulo', '')}</div>", unsafe_allow_html=True)
    st.markdown(f"### {fila.get('subtitulo', '')}")
    
    with st.container(border=True):
        texto_principal = fila.get('teoriatarea', 'Sin contenido')
        st.markdown(f"<div class='grande-text'>{texto_principal}</div>", unsafe_allow_html=True)
        
        # MOSTRAR ESPACIO PARA DILIGENCIAR (Si en Excel dice 'Texto')
        tipo = str(fila.get('tipoinput', '')).strip().lower()
        if tipo == 'texto':
            st.text_area("Escribe tu reflexión aquí:", key=f"input_{st.session_state.indice}", height=150)
        
        audio = fila.get('audiourl')
        if pd.notna(audio) and str(audio).startswith('http'):
            st.audio(audio)

    st.write("---")
    
    # --- NAVEGACIÓN POR PUNTOS (INDICADORES) ---
    # Creamos una fila de columnas para los puntos
    cols_puntos = st.columns(total)
    for i in range(total):
        with cols_puntos[i]:
            # El punto actual se ve diferente
            if i == st.session_state.indice:
                if st.button("●", key=f"p{i}", help=f"Paso {i+1}"): pass
            else:
                if st.button("○", key=f"p{i}", help=f"Ir al paso {i+1}"):
                    st.session_state.indice = i
                    st.rerun()

    # Botones de apoyo (Siguiente/Anterior invisibles o pequeños al final)
    c1, c2, c3 = st.columns([1,2,1])
    with c1:
        if st.session_state.indice > 0:
            if st.button("Anterior"):
                st.session_state.indice -= 1
                st.rerun()
    with c3:
        if st.session_state.indice < total - 1:
            if st.button("Siguiente"):
                st.session_state.indice += 1
                st.rerun()
        else:
            if st.button("¡Finalizar!"):
                st.balloons()
