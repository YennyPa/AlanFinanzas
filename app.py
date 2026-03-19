import streamlit as st
import pandas as pd
import requests
import json

# --- CONFIGURACIÓN DE DATOS ---
URL_CONTENIDO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=0&single=true&output=csv"
URL_USUARIOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0ezjgOs96GuOBIwmsv4S0lx3IA7x2K-q1dVBTtO37eUo35h6BmupREN_cVkCvt2XaOaYIijQbIP5A/pub?gid=83033184&single=true&output=csv"

# --- REEMPLAZA ESTO CON TU URL DE APPS SCRIPT (LA QUE TERMINA EN /exec) ---
URL_SCRIPT_RESPUESTAS = "TU_URL_AQUÍ" 

# --- URL DE TU LOGO EN GITHUB ---
URL_LOGO = "https://raw.githubusercontent.com/YennyPa/AlanFinanzas/main/Logo%20de%20Alan%20Finanzas.png"

st.set_page_config(page_title="Alan Finanzas - Reto", page_icon="💰", layout="centered")

# --- ESTILOS CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #FDFEFE; }}
    .slide-card {{
        background-color: #FFFFFF;
        border-radius: 25px;
        padding: 45px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        border: 1px solid #F2F3F4;
        margin-bottom: 20px;
    }}
    .titulo-finanzas {{ font-size: 34px !important; font-weight: bold; color: #8B5A2B; margin-bottom: 10px; }}
    .subtitulo-finanzas {{ font-size: 20px !important; color: #457B9D; font-style: italic; margin-bottom: 25px; }}
    .texto-finanzas {{ font-size: 22px !important; line-height: 1.6; color: #2E4053; }}
    
    /* Botones de navegación (puntos) */
    .stButton>button[key^="p"] {{
        border-radius: 50% !important; width: 14px !important; height: 14px !important; padding: 0 !important;
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

# --- FLUJO DE LA APP ---
if 'autenticado' not in st.session_state:
    st.image(URL_LOGO, width=250)
    st.title("Acceso al Reto")
    email_input = st.text_input("Tu correo registrado:").lower().strip()
    if st.button("Comenzar"):
        df_users = cargar_datos(URL_USUARIOS)
        user_row = df_users[df_users['email'].str.lower().str.strip() == email_input]
        if not user_row.empty:
            st.session_state.autenticado, st.session_state.usuario_nombre, st.session_state.usuario_email = True, user_row.iloc[0]['nombrecompleto'], email_input
            st.rerun()
        else: st.error("Correo no encontrado.")
else:
    # Contenido
    df_content = cargar_datos(URL_CONTENIDO)
    pasos = df_content[df_content['dia'] == 2].sort_values('paso')
    if 'indice' not in st.session_state: st.session_state.indice = 0
    fila = pasos.iloc[st.session_state.indice]

    # Cabecera con Logo
    st.image(URL_LOGO, width=150)
    st.write(f"Hola, **{st.session_state['usuario_nombre']}**")
    
    # Tarjeta de contenido
    st.markdown("<div class='slide-card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='titulo-finanzas'>{fila.get('titulo', '')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitulo-finanzas'>{fila.get('subtitulo', '')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='texto-finanzas'>{fila.get('teoriatarea', '').replace('\\n', '<br>')}</div>", unsafe_allow_html=True)
    
    resp_usuario = ""
    if str(fila.get('tipoinput', '')).lower() == 'texto':
        resp_usuario = st.text_area("Escribe aquí tu respuesta:", key=f"in_{st.session_state.indice}")
    
    if pd.notna(fila.get('audiourl')) and str(fila.get('audiourl')).startswith('http'):
        st.audio(fila.get('audiourl'))
    st.markdown("</div>", unsafe_allow_html=True)

    # Navegación
    c1, c2, c3 = st.columns([1,3,1])
    with c1:
        if st.session_state.indice > 0 and st.button("⬅️"):
            st.session_state.indice -= 1
            st.rerun()
    with c3:
        if st.session_state.indice < len(pasos)-1:
            if st.button("➡️"):
                if resp_usuario: enviar_a_excel(st.session_state.usuario_email, 2, fila['paso'], resp_usuario)
                st.session_state.indice += 1
                st.rerun()
        else:
            if st.button("Finalizar"):
                if resp_usuario: enviar_a_excel(st.session_state.usuario_email, 2, fila['paso'], resp_usuario)
                st.balloons()
                st.success("¡Día completado! Reporte enviado.")
