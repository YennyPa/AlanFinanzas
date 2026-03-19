import streamlit as st
import pandas as pd
import requests
import json

# --- CONFIGURACIÓN DE DATOS ---
URL_CONTENIDO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=0&single=true&output=csv"
URL_USUARIOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=83033184&single=true&output=csv"

# --- URL DEL LOGO ---
# Sube el logo (image_0.png) a un hosting como postimages.org y pega el ENLACE DIRECTO aquí:
URL_LOGO = "TU_URL_DEL_LOGO" 

st.set_page_config(page_title="Alan Finanzas - Reto", page_icon="💰", layout="centered")

# =========================================================
# === DISEÑO BONITO (CSS INYECTADO) ===
# Basado en la paleta del logo: Marrón #8B5A2B y Azul/Gris #457B9D
# =========================================================
st.markdown(f"""
    <style>
    /* Fondo general */
    .stApp {{ background-color: #F8F9F9; }}
    
    /* Contenedor del Logo */
    .logo-container {{
        text-align: center;
        padding-top: 20px;
        padding-bottom: 30px;
    }}
    
    /* Contenedor de la Diapositiva (Tarjeta Blanca) */
    .slide-card {{
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 40px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        border: 1px solid #EAECEE;
    }}
    
    /* Tipografía */
    .titulo-finanzas {{
        font-size: 36px !important;
        font-weight: bold;
        color: #8B5A2B; /* Marrón Corporativo */
        font-family: 'Helvetica Neue', sans-serif;
        margin-bottom: 5px;
    }}
    .subtitulo-finanzas {{
        font-size: 20px !important;
        color: #5D6D7E;
        font-style: italic;
        margin-bottom: 30px;
    }}
    .texto-finanzas p, .texto-finanzas {{
        font-size: 22px !important;
        line-height: 1.7;
        color: #2C3E50;
        margin-bottom: 25px;
    }}
    
    /* Estilo de los Puntos de Navegación */
    .stButton>button[key^="p"] {{
        border-radius: 50% !important;
        padding: 0 !important;
        width: 15px !important;
        height: 15px !important;
        margin: 5px;
        font-size: 1px; /* Ocultar el texto */
    }}
    /* Punto inactivo (contorno) */
    .stButton>button[key^="p"]:not([help^="Paso actual"]) {{
        background-color: #FFFFFF !important;
        color: #457B9D !important; /* Azul Financiero */
        border: 2px solid #457B9D !important;
    }}
    /* Punto activo (relleno con degradado corporativo) */
    .stButton>button[help^="Paso actual"] {{
        background-color: #457B9D !important; /* Azul */
        background-image: linear-gradient(135deg, #457B9D, #8B5A2B) !important;
        color: #457B9D !important;
        border: none !important;
        box-shadow: 0 0 10px rgba(69, 123, 157, 0.5);
    }}
    
    /* Botones de acción */
    .stButton>button:not([key^="p"]) {{
        background-image: linear-gradient(135deg, #8B5A2B, #D4AC0D); /* Marrón a Dorado */
        color: white !important;
        border: none !important;
        border-radius: 25px;
        padding: 10px 25px;
        font-size: 18px !important;
        font-weight: bold;
        box-shadow: 0 5px 15px rgba(139, 90, 43, 0.3);
    }}
    .stButton>button:not([key^="p"]):hover {{
        background-image: linear-gradient(135deg, #D4AC0D, #8B5A2B); /* Invertir hover */
    }}
    
    /* Input de texto */
    .stTextArea>div>div>textarea {{
        border-radius: 15px;
        border: 2px solid #EAECEE;
        background-color: #FBFCFC;
        font-size: 18px;
        padding: 15px;
    }}
    .stTextArea>div>div>textarea:focus {{
        border-color: #457B9D;
        box-shadow: 0 0 10px rgba(69, 123, 157, 0.2);
    }}
    </style>
    """, unsafe_allow_html=True)

# =========================================================
# === LÓGICA DE DATOS ===
# =========================================================
@st.cache_data(ttl=10)
def cargar_datos(url):
    df = pd.read_csv(url)
    df.columns = [str(c).strip().lower().replace(" ", "").replace("_", "") for c in df.columns]
    return df

# =========================================================
# === PANTALLA DE ACCESO (BONITA) ===
# =========================================================
if 'autenticado' not in st.session_state:
    st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
    if URL_LOGO != "TU_URL_DEL_LOGO":
        st.image(URL_LOGO, width=200)
    st.markdown("</div>", unsafe_allow_html=True)
    
    with st.container(border=False):
        st.markdown(f"<div class='titulo-finanzas'>🛡️ Bienvenido al Reto</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='subtitulo-finanzas'>Ingresa para comenzar tu transformación</div>", unsafe_allow_html=True)
        
        c1, c2 = st.columns([3,1])
        with c1:
            email_input = st.text_input("Correo registrado:", label_visibility="collapsed", placeholder="ejemplo@correo.com").lower().strip()
        with c2:
            st.markdown("<div style='margin-top:2px;'>", unsafe_allow_html=True)
            entrar_btn = st.button("Entrar")
            st.markdown("</div>", unsafe_allow_html=True)
            
        if entrar_btn:
            df_users = cargar_datos(URL_USUARIOS)
            user_row = df_users[df_users['email'].str.lower().str.strip() == email_input]
            if not user_row.empty:
                st.session_state.autenticado = True
                st.session_state.usuario_nombre = user_row.iloc[0]['nombrecompleto']
                st.session_state.usuario_email = email_input
                st.rerun()
            else:
                st.error("🚫 Correo no encontrado en la lista de Alan Finanzas.")
else:
    # =========================================================
    # === APP PRINCIPAL (DISEÑO REEL) ===
    # =========================================================
    # Header minimalista con logo
    c_logo, c_perfil = st.columns([1,1])
    with c_logo:
        if URL_LOGO != "TU_URL_DEL_LOGO":
            st.image(URL_LOGO, width=120)
    with c_perfil:
        st.write(f"👋 **{st.session_state['usuario_nombre']}**")
        if st.button("Cerrar Sesión", key="logout"):
            del st.session_state['autenticado']
            st.rerun()

    st.write("---")

    df_content = cargar_datos(URL_CONTENIDO)
    pasos = df_content[df_content['dia'] == 2].sort_values('paso')
    total = len(pasos)

    if 'indice' not in st.session_state: st.session_state.indice = 0
    fila = pasos.iloc[st.session_state.indice]

    # --- INICIO DE LA TARJETA (SLIDE) ---
    st.markdown("<div class='slide-card'>", unsafe_allow_html=True)
    
    st.markdown(f"<div class='titulo-finanzas'>{fila.get('titulo', '')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitulo-finanzas'>{fila.get('subtitulo', '')}</div>", unsafe_allow_html=True)
    
    texto_principal = fila.get('teoriatarea', 'Sin contenido').replace("\n", "<br>")
    st.markdown(f"<div class='texto-finanzas'>{texto_principal}</div>", unsafe_allow_html=True)
    
    # Campo para diligenciar si corresponde
    tipo = str(fila.get('tipoinput', '')).strip().lower()
    if tipo == 'texto':
        # Texto en cursiva para la instrucción del input (paleta marrón)
        st.markdown("<p style='color:#8B5A2B; font-size:16px; font-style:italic;'>Tu reflexión aquí:</p>", unsafe_allow_html=True)
        st.text_area("", key=f"input_{st.session_state.indice}", height=120, label_visibility="collapsed")
    
    audio = fila.get('audiourl')
    if pd.notna(audio) and str(audio).startswith('http'):
        st.audio(audio)
        
    st.markdown("</div>", unsafe_allow_html=True) # --- FIN DE LA TARJETA ---

    # --- NAVEGACIÓN POR PUNTOS (ESTILIZADA CON CÓDIGOS CSS) ---
    st.write(" ") # Espacio
    cols_puntos = st.columns(total)
    for i in range(total):
        with cols_puntos[i]:
            # El botón de punto es modificado por CSS (línea 46)
            tooltip = "Paso actual" if i == st.session_state.indice else f"Ir al paso {i+1}"
            if st.button("●", key=f"p{i}", help=tooltip):
                if i != st.session_state.indice:
                    st.session_state.indice = i
                    st.rerun()

    # Botones Siguiente con paleta Dorado/Marrón
    st.write(" ") # Espacio
    c_nav1, c_nav2 = st.columns([1,1])
    with c_nav2:
        if st.session_state.indice < total - 1:
            if st.button("Siguiente ▶️"):
                st.session_state.indice += 1
                st.rerun()
        else:
            if st.button("🚀 ¡Finalizar Día!"):
                st.balloons()
