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
    
    .titulo-finanzas {{ 
        font-size: 32px !important; 
        font-weight: bold; 
        color: #8B5A2B; 
        margin-top: 10px !important;
        margin-bottom: 10px;
        line-height: 1.2;
    }}
    
    .subtitulo-finanzas {{ 
        font-size: 19px !important; 
        color: #457B9D; 
        font-style: italic; 
        margin-bottom: 25px;
        line-height: 1.4;
    }}
    
    .texto-finanzas {{ 
        font-size: 21px !important; 
        line-height: 1.7; 
        color: #2E4053;
        margin-bottom: 20px;
    }}

    /* Estilo para los botones de navegación */
    .stButton>button {{
        border-radius: 12px;
        font-weight: bold;
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

    # --- CABECERA ---
    c1, c2 = st.columns([1, 1])
    with c1:
        st.image(URL_LOGO, width=140)
    with c2:
        st.write(f"Hola, **{st.session_state['usuario_nombre']}** 👋")
        if st.button("Cerrar Sesión"):
            del st.session_state['autenticado']
            st.rerun()

    st.divider() # Línea estética sutil

    # --- CONTENIDO (SIN MARCO) ---
    st.markdown(f"<div class='titulo-finanzas'>{fila.get('titulo', '')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitulo-finanzas'>{fila.get('subtitulo', '')}</div>", unsafe_allow_html=True)
    
    # Aplicar saltos de línea de Excel
    texto_final = str(fila.get('teoriatarea', '')).replace('\n', '<br>')
    st.markdown(f"<div class='texto-finanzas'>{texto_final}</div>", unsafe_allow_html=True)
    
    resp_usuario = ""
    if str(fila.get('tipoinput', '')).lower() == 'texto':
        st.write("---")
        resp_usuario = st.text_area("Escribe tu reflexión aquí:", key=f"in_{st.session_state.indice}", height=180)
    
    if pd.notna(fila.get('audiourl')) and str(fila.get('audiourl')).startswith('http'):
        st.audio(fila.get('audiourl'))

    # --- NAVEGACIÓN ---
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
            if st.button("✅ ¡Terminar Día 2!"):
                if resp_usuario: enviar_a_excel(st.session_state.usuario_email, 2, fila['paso'], resp_usuario)
                st.balloons()
                st.success("¡Excelente trabajo! Tus respuestas han sido guardadas.")
