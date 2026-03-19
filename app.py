import streamlit as st
import pandas as pd
import requests
import json

# --- CONFIGURACIÓN DE DATOS ---
URL_CONTENIDO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=0&single=true&output=csv"
URL_USUARIOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=83033184&single=true&output=csv"

# --- REEMPLAZA ESTO CON TU URL DE APPS SCRIPT ---
URL_SCRIPT_RESPUESTAS = "TU_URL_AQUÍ" 

# --- URL DEL LOGO ---
URL_LOGO = "https://raw.githubusercontent.com/YennyPa/AlanFinanzas/main/logo.png"

st.set_page_config(page_title="Alan Finanzas - Reto", page_icon="💰", layout="centered")

# --- DISEÑO (CSS) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #FDFEFE; }}
    
    /* Contenedor de la Diapositiva (Tarjeta) */
    .slide-card {{
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border: 1px solid #F0F3F4;
        margin-top: 0px; /* Quitamos margen superior para evitar el hueco */
    }}
    
    .titulo-finanzas {{ 
        font-size: 32px !important; 
        font-weight: bold; 
        color: #8B5A2B; 
        margin-top: 0px !important;
        margin-bottom: 10px;
        line-height: 1.2;
    }}
    
    .subtitulo-finanzas {{ 
        font-size: 19px !important; 
        color: #457B9D; 
        font-style: italic; 
        margin-bottom: 20px;
    }}
    
    .texto-finanzas {{ 
        font-size: 21px !important; 
        line-height: 1.6; 
        color: #2E4053;
    }}
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=10)
def cargar_datos(url):
    df = pd.read_csv(url)
    df.columns = [str(c).strip().lower().replace(" ", "").replace("_", "") for c in df.columns]
    return df

def enviar_a_excel(email, dia, paso, respuesta):
    if URL_SCRIPT_RESPUESTAS != "TU_URL_AQUÍ":
        payload = {"email": email, "dia": int(dia), "paso": int(paso), "respuesta": respuesta}
        try: requests.post(URL_SCRIPT_RESPUESTAS, data=json.dumps(payload))
        except: pass

# --- FLUJO ---
if 'autenticado' not in st.session_state:
    st.image(URL_LOGO, width=220)
    st.title("Acceso al Reto")
    email_input = st.text_input("Ingresa tu correo:").lower().strip()
    if st.button("Entrar al Reto"):
        df_users = cargar_datos(URL_USUARIOS)
        user_row = df_users[df_users['email'].str.lower().str.strip() == email_input]
        if not user_row.empty:
            st.session_state.autenticado = True
            st.session_state.usuario_nombre = user_row.iloc[0]['nombrecompleto']
            st.session_state.usuario_email = email_input
            st.rerun()
        else:
            st.error("Correo no registrado.")

else:
    df_content = cargar_datos(URL_CONTENIDO)
    pasos = df_content[df_content['dia'] == 2].sort_values('paso')
    if 'indice' not in st.session_state: st.session_state.indice = 0
    fila = pasos.iloc[st.session_state.indice]

    # 1. Cabecera (Fuera del recuadro blanco)
    c1, c2 = st.columns([1, 1])
    with c1:
        st.image(URL_LOGO, width=140)
    with c2:
        st.write(f"Hola, **{st.session_state['usuario_nombre']}** 👋")
        if st.button("Cerrar Sesión"):
            del st.session_state['autenticado']
            st.rerun()

    st.write("") # Espacio pequeño

    # 2. CUERPO DE LA TARJETA (Aquí empieza el recuadro blanco)
    # Usamos st.container para agrupar y evitar que Streamlit meta aire arriba
    with st.container():
        st.markdown('<div class="slide-card">', unsafe_allow_html=True)
        
        st.markdown(f"<div class='titulo-finanzas'>{fila.get('titulo', '')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='subtitulo-finanzas'>{fila.get('subtitulo', '')}</div>", unsafe_allow_html=True)
        
        texto_final = str(fila.get('teoriatarea', '')).replace('\n', '<br>')
        st.markdown(f"<div class='texto-finanzas'>{texto_final}</div>", unsafe_allow_html=True)
        
        resp_usuario = ""
        if str(fila.get('tipoinput', '')).lower() == 'texto':
            st.write("---")
            resp_usuario = st.text_area("Escribe tu reflexión aquí:", key=f"in_{st.session_state.indice}", height=150)
        
        if pd.notna(fila.get('audiourl')) and str(fila.get('audiourl')).startswith('http'):
            st.audio(fila.get('audiourl'))
            
        st.markdown("</div>", unsafe_allow_html=True)

    # 3. NAVEGACIÓN (Fuera del recuadro)
    st.write(" ")
    col_prev, col_next = st.columns([1, 1])
    with col_prev:
        if st.session_state.indice > 0:
            if st.button("⬅️ Anterior"):
                st.session_state.indice -= 1
                st.rerun()
    with col_next:
        if st.session_state.indice < len(pasos) - 1:
            if st.button("Siguiente ➡️"):
                if resp_usuario: enviar_a_excel(st.session_state.usuario_email, 2, fila['paso'], resp_usuario)
                st.session_state.indice += 1
                st.rerun()
        else:
            if st.button("✅ ¡Terminar!"):
                if resp_usuario: enviar_a_excel(st.session_state.usuario_email, 2, fila['paso'], resp_usuario)
                st.balloons()
